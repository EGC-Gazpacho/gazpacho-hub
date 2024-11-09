
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Optional




class DataSetFormGithub(FlaskForm):
    commit_message = StringField('Mensaje del commit', validators=[DataRequired()])
    owner = StringField('Propietario del repositorio', validators=[DataRequired()])
    repo_name = StringField('Nombre del repositorio', validators=[DataRequired()])
    
    repo_type = SelectField('Tipo de Repositorio', choices=[
        ('new', 'Nuevo Repositorio'),
        ('existing', 'Repositorio Existente')
    ])

    access_token = PasswordField('Token de Acceso Personal', validators=[DataRequired()])
    license = SelectField('Licencia del Dataset', choices=[
        ('MIT', 'MIT'),
        ('GPL', 'GPL'),
        ('Apache', 'Apache'),
        ('CC BY', 'CC BY'),
        ('Ninguna', 'Ninguna')
    ])
        
    submit = SubmitField('Subir Dataset a GitHub')
    
