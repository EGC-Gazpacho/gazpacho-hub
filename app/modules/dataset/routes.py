import logging
import os
import json
import shutil
import tempfile
import uuid
import yaml
from datetime import datetime, timezone
from zipfile import ZipFile
from xml.etree.ElementTree import Element, SubElement, tostring
import xml.dom.minidom as minidom

from flask import (
    redirect,
    render_template,
    request,
    jsonify,
    send_from_directory,
    make_response,
    abort,
    url_for,
)
from flask_login import login_required, current_user

from app.modules.dataset.forms import DataSetForm
from app.modules.dataset.models import (
    DSDownloadRecord
)
from app.modules.dataset import dataset_bp
from app.modules.dataset.services import (
    AuthorService,
    DSDownloadRecordService,
    DSMetaDataService,
    DSViewRecordService,
    DataSetService,
    DOIMappingService
)
from app.modules.zenodo.services import ZenodoService

logger = logging.getLogger(__name__)


dataset_service = DataSetService()
author_service = AuthorService()
dsmetadata_service = DSMetaDataService()
zenodo_service = ZenodoService()
doi_mapping_service = DOIMappingService()
ds_view_record_service = DSViewRecordService()


@dataset_bp.route("/dataset/upload", methods=["GET", "POST"])
@login_required
def create_dataset():
    form = DataSetForm()
    if request.method == "POST":

        dataset = None

        if not form.validate_on_submit():
            return jsonify({"message": form.errors}), 400

        try:
            logger.info("Creating dataset...")
            dataset = dataset_service.create_from_form(form=form, current_user=current_user)
            logger.info(f"Created dataset: {dataset}")
            dataset_service.move_feature_models(dataset)
        except Exception as exc:
            logger.exception(f"Exception while create dataset data in local {exc}")
            return jsonify({"Exception while create dataset data in local: ": str(exc)}), 400

        # send dataset as deposition to Zenodo
        data = {}
        try:
            zenodo_response_json = zenodo_service.create_new_deposition(dataset)
            response_data = json.dumps(zenodo_response_json)
            data = json.loads(response_data)
        except Exception as exc:
            data = {}
            zenodo_response_json = {}
            logger.exception(f"Exception while create dataset data in Zenodo {exc}")

        if data.get("conceptrecid"):
            deposition_id = data.get("id")

            # update dataset with deposition id in Zenodo
            dataset_service.update_dsmetadata(dataset.ds_meta_data_id, deposition_id=deposition_id)

            try:
                # iterate for each feature model (one feature model = one request to Zenodo)
                for feature_model in dataset.feature_models:
                    zenodo_service.upload_file(dataset, deposition_id, feature_model)

                # publish deposition
                zenodo_service.publish_deposition(deposition_id)

                # update DOI
                deposition_doi = zenodo_service.get_doi(deposition_id)
                dataset_service.update_dsmetadata(dataset.ds_meta_data_id, dataset_doi=deposition_doi)
            except Exception as e:
                msg = f"it has not been possible upload feature models in Zenodo and update the DOI: {e}"
                return jsonify({"message": msg}), 200

        # Delete temp folder
        file_path = current_user.temp_folder()
        if os.path.exists(file_path) and os.path.isdir(file_path):
            shutil.rmtree(file_path)

        msg = "Everything works!"
        return jsonify({"message": msg}), 200

    return render_template("dataset/upload_dataset.html", form=form)


@dataset_bp.route("/dataset/list", methods=["GET", "POST"])
@login_required
def list_dataset():
    return render_template(
        "dataset/list_datasets.html",
        datasets=dataset_service.get_synchronized(current_user.id),
        local_datasets=dataset_service.get_unsynchronized(current_user.id),
    )


@dataset_bp.route("/dataset/file/upload", methods=["POST"])
@login_required
def upload():
    file = request.files["file"]
    temp_folder = current_user.temp_folder()

    if not file or not file.filename.endswith(".uvl"):
        return jsonify({"message": "No valid file"}), 400

    # create temp folder
    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder)

    file_path = os.path.join(temp_folder, file.filename)

    if os.path.exists(file_path):
        # Generate unique filename (by recursion)
        base_name, extension = os.path.splitext(file.filename)
        i = 1
        while os.path.exists(
            os.path.join(temp_folder, f"{base_name} ({i}){extension}")
        ):
            i += 1
        new_filename = f"{base_name} ({i}){extension}"
        file_path = os.path.join(temp_folder, new_filename)
    else:
        new_filename = file.filename

    try:
        file.save(file_path)
    except Exception as e:
        return jsonify({"message": str(e)}), 500

    return (
        jsonify(
            {
                "message": "UVL uploaded and validated successfully",
                "filename": new_filename,
            }
        ),
        200,
    )


@dataset_bp.route("/dataset/file/delete", methods=["POST"])
def delete():
    data = request.get_json()
    filename = data.get("file")
    temp_folder = current_user.temp_folder()
    filepath = os.path.join(temp_folder, filename)

    if os.path.exists(filepath):
        os.remove(filepath)
        return jsonify({"message": "File deleted successfully"})

    return jsonify({"error": "Error: File not found"})


@dataset_bp.route("/dataset/download/<int:dataset_id>", methods=["GET"])
def download_dataset(dataset_id):
    dataset = dataset_service.get_or_404(dataset_id)

    file_path = f"uploads/user_{dataset.user_id}/dataset_{dataset.id}/"

    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, f"dataset_{dataset_id}.zip")

    with ZipFile(zip_path, "w") as zipf:
        for subdir, dirs, files in os.walk(file_path):
            for file in files:
                full_path = os.path.join(subdir, file)

                relative_path = os.path.relpath(full_path, file_path)

                zipf.write(
                    full_path,
                    arcname=os.path.join(
                        os.path.basename(zip_path[:-4]), relative_path
                    ),
                )

    user_cookie = request.cookies.get("download_cookie")
    if not user_cookie:
        user_cookie = str(
            uuid.uuid4()
        )  # Generate a new unique identifier if it does not exist
        # Save the cookie to the user's browser
        resp = make_response(
            send_from_directory(
                temp_dir,
                f"dataset_{dataset_id}.zip",
                as_attachment=True,
                mimetype="application/zip",
            )
        )
        resp.set_cookie("download_cookie", user_cookie)
    else:
        resp = send_from_directory(
            temp_dir,
            f"dataset_{dataset_id}.zip",
            as_attachment=True,
            mimetype="application/zip",
        )

    # Check if the download record already exists for this cookie
    existing_record = DSDownloadRecord.query.filter_by(
        user_id=current_user.id if current_user.is_authenticated else None,
        dataset_id=dataset_id,
        download_cookie=user_cookie
    ).first()

    if not existing_record:
        # Record the download in your database
        DSDownloadRecordService().create(
            user_id=current_user.id if current_user.is_authenticated else None,
            dataset_id=dataset_id,
            download_date=datetime.now(timezone.utc),
            download_cookie=user_cookie,
        )

    return resp


# Descargar los datos en .json
def convert_uvl_to_json(content):
    lines = content.splitlines()
    result = {}
    current_feature = None
    current_mandatory = None
    current_optional = None
    in_constraints = False

    for line in lines:
        stripped_line = line.strip()
        if stripped_line.startswith("features"):
            result["features"] = {}
            current_feature = result["features"]
        elif stripped_line.startswith("constraints"):
            in_constraints = True
            result["constraints"] = {}
            current_constraint = result["constraints"]
        elif stripped_line.startswith("Chat"):
            current_feature["Chat"] = {"mandatory": {}, "optional": {}}
            current_mandatory = current_feature["Chat"]["mandatory"]
            current_optional = current_feature["Chat"]["optional"]
        elif stripped_line.startswith("mandatory"):
            pass
        elif stripped_line.startswith("optional"):
            pass
        elif "=>" in stripped_line:
            if in_constraints:
                # Asumiendo que la restricción es en formato "A => B"
                key, value = stripped_line.split("=>")
                current_constraint[key.strip()] = value.strip().strip('"')
        else:
            if current_mandatory is not None:
                current_mandatory[stripped_line] = stripped_line  
            elif current_optional is not None:
                current_optional[stripped_line] = stripped_line  

    return result

# Descargar los elementos en xml


def convert_uvl_to_xml(content):
    # Crear el elemento raíz
    root = Element("UVLData")
    current_parent = root  # Empezamos en el nodo raíz
    parent_stack = []  # Pila para gestionar el nivel jerárquico
    indentation_level = 0  # Seguimiento de los niveles de sangría

    for line in content.splitlines():
        stripped_line = line.strip()  # Elimina espacios al inicio y final
        if not stripped_line:
            continue  # Saltar líneas en blanco

        # Calcular el nivel de indentación (2 espacios por nivel en este ejemplo)
        new_level = (len(line) - len(stripped_line)) // 4

        # Actualizar el nivel de nodo
        if new_level > indentation_level:
            parent_stack.append(current_parent)
        elif new_level < indentation_level:
            for _ in range(indentation_level - new_level):
                current_parent = parent_stack.pop()

        # Crear el nuevo nodo bajo el nodo actual
        element = SubElement(current_parent, "item", name=stripped_line)
        current_parent = element
        indentation_level = new_level

    # Generar una cadena XML bonita
    xml_str = minidom.parseString(tostring(root)).toprettyxml(indent="  ")
    return xml_str


# Convierte el uvl en yaml
def convert_uvl_to_yaml(content):
    yaml_data = {
        'features': {},
        'constraints': {}
    }

    current_feature = None
    current_mandatory = None
    current_messages = None

    for line in content.splitlines():
        stripped_line = line.strip()

        if not stripped_line:  # Ignora líneas vacías
            continue

        if stripped_line.startswith("features"):
            current_feature = "features"
        elif stripped_line.startswith("constraints"):
            current_feature = "constraints"
            continue  # No procesar más por el momento, solo ir a constraints
        elif current_feature == "features":
            # Manejar las secciones de features
            if stripped_line == "Chat":
                yaml_data[current_feature]["Chat"] = {
                    "mandatory": {},
                    "optional": []
                }
                current_mandatory = yaml_data[current_feature]["Chat"]["mandatory"]
            elif stripped_line == "mandatory":
                current_mandatory = {}
                yaml_data[current_feature]["Chat"]["mandatory"] = current_mandatory
            elif stripped_line == "optional":
                # Cambiar a una lista para almacenar elementos directamente
                yaml_data[current_feature]["Chat"]["optional"] = []
                current_mandatory = None  # No se necesita más
            elif stripped_line == "Connection":
                current_mandatory["Connection"] = {}
                current_mandatory["Connection"]["alternative"] = []
            elif stripped_line == "alternative":
                # La línea "alternative" se procesa aquí, pero no agrega nada aún
                pass
            elif stripped_line.startswith('"'):
                # Maneja las alternativas
                if current_mandatory and "Connection" in current_mandatory:
                    current_mandatory["Connection"]["alternative"].append(stripped_line.strip('"'))
                elif current_feature == "features" and "optional" in yaml_data[current_feature]["Chat"]:
                    yaml_data[current_feature]["Chat"]["optional"].append(stripped_line.strip('"'))
            elif stripped_line == "Messages":
                current_messages = {}
                current_mandatory["Messages"] = current_messages
            elif stripped_line == "or":
                current_messages["or"] = []
            elif stripped_line in ["Text", "Video", "Audio"]:
                if current_messages and "or" in current_messages:
                    current_messages["or"].append(stripped_line)

        elif current_feature == "constraints":
            # Manejo de restricciones
            if '=>' in stripped_line:
                key, value = map(str.strip, stripped_line.split('=>'))
                yaml_data['constraints'][key] = value.strip('"')
            elif ':' in stripped_line:
                key, value = map(str.strip, stripped_line.split(':'))
                yaml_data['constraints'][key] = value.strip('"')

    return yaml.dump(yaml_data, default_flow_style=False, sort_keys=False)
 
@dataset_bp.route("/dataset/download_informat/<file_format>/<int:dataset_id>", methods=["GET"])
def download_dataset_json(file_format, dataset_id):
    if file_format not in ["json", "xml", "yaml"]:
        abort(400, "Formato no soportado")  # Solo acepta json,xmly yaml

    dataset = dataset_service.get_or_404(dataset_id)
    file_path = f"uploads/user_{dataset.user_id}/dataset_{dataset.id}/"

    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, f"dataset_{dataset_id}.zip")

    with ZipFile(zip_path, "w") as zipf:
        for subdir, dirs, files in os.walk(file_path):
            for file in files:
                full_path = os.path.join(subdir, file)

                if file.endswith('.uvl'):
                    # Leer el contenido del archivo .uvl
                    with open(full_path, 'r') as uvl_file:
                        content = uvl_file.read()
                        try:
                            # Convertir según el formato solicitado
                            if file_format == "json":
                                converted_content = json.dumps(convert_uvl_to_json(content))
                                new_file_name = file[:-4] + '.json'
                            elif file_format == "xml":
                                converted_content = convert_uvl_to_xml(content)
                                new_file_name = file[:-4] + '.xml'
                            elif file_format == "yaml":
                                converted_content = convert_uvl_to_yaml(content)
                                new_file_name = file[:-4] + '.yaml'
                            zipf.writestr(new_file_name, converted_content)
                        except Exception as e:
                            print(f"Error al convertir {file}: {e}")
                else:
                    zipf.write(
                        full_path,
                        arcname=os.path.join(
                            os.path.basename(zip_path[:-4]), file
                        ),
                    )

    user_cookie = request.cookies.get("download_cookie")
    if not user_cookie:
        user_cookie = str(uuid.uuid4())
        resp = make_response(
            send_from_directory(
                temp_dir,
                f"dataset_{dataset_id}.zip",
                as_attachment=True,
                mimetype="application/zip",
            )
        )
        resp.set_cookie("download_cookie", user_cookie)
    else:
        resp = send_from_directory(
            temp_dir,
            f"dataset_{dataset_id}.zip",
            as_attachment=True,
            mimetype="application/zip",
        )

     # Check if the download record already exists for this cookie
    existing_record = DSDownloadRecord.query.filter_by(
        user_id=current_user.id if current_user.is_authenticated else None,
        dataset_id=dataset_id,
        download_cookie=user_cookie
    ).first()

    if not existing_record:
        # Record the download in your database
        DSDownloadRecordService().create(
            user_id=current_user.id if current_user.is_authenticated else None,
            dataset_id=dataset_id,
            download_date=datetime.now(timezone.utc),
            download_cookie=user_cookie,
        )

    return resp


@dataset_bp.route("/doi/<path:doi>/", methods=["GET"])
def subdomain_index(doi):

    # Check if the DOI is an old DOI
    new_doi = doi_mapping_service.get_new_doi(doi)
    if new_doi:
        # Redirect to the same path with the new DOI
        return redirect(url_for('dataset.subdomain_index', doi=new_doi), code=302)

    # Try to search the dataset by the provided DOI (which should already be the new one)
    ds_meta_data = dsmetadata_service.filter_by_doi(doi)

    if not ds_meta_data:
        abort(404)

    # Get dataset
    dataset = ds_meta_data.data_set
    # Save the cookie to the user's browser
    user_cookie = ds_view_record_service.create_cookie(dataset=dataset)
    resp = make_response(render_template("dataset/view_dataset.html", dataset=dataset))
    resp.set_cookie("view_cookie", user_cookie)

    return resp


@dataset_bp.route("/dataset/unsynchronized/<int:dataset_id>/", methods=["GET"])
@login_required
def get_unsynchronized_dataset(dataset_id):

    # Get dataset
    dataset = dataset_service.get_unsynchronized_dataset(current_user.id, dataset_id)

    if not dataset:
        abort(404)

    return render_template("dataset/view_dataset.html", dataset=dataset)
