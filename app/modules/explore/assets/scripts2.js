document.addEventListener('DOMContentLoaded', () => {
    send_query();
});

.then(data => {
    console.log(data);
    document.getElementById('results').innerHTML = '';

    const resultCount = data.length;
    const resultText = resultCount === 1 ? 'model' : 'models'; // Cambia a 'model' o 'models'
    document.getElementById('results_number').textContent = `${resultCount} ${resultText} found`;

    if (resultCount === 0) {
        console.log("show not found icon");
        document.getElementById("results_not_found").style.display = "block";
    } else {
        document.getElementById("results_not_found").style.display = "none";
    }

    data.forEach(model => { // Cambia 'dataset' por 'model'
        let card = document.createElement('div');
        card.className = 'col-12';
        card.innerHTML = `
            <div class="card">
                <div class="card-body">
                    <div class="d-flex align-items-center justify-content-between">
                        <h3><a href="${model.url}">${model.name}</a></h3> <!-- Cambia title por name -->
                        <div>
                            <span class="badge bg-primary" style="cursor: pointer;" onclick="set_publication_type_as_query('${model.publication_type}')">${model.publication_type}</span>
                        </div>
                        <div>
                            <span class="badge bg-primary" style="cursor: pointer;" onclick="set_number_of_features_as_query('${model.number_of_features}')">${model.number_of_features}</span>
                        </div>
                    </div>
                    <p class="text-secondary">${formatDate(model.created_at)}</p>

                    <div class="row mb-2">
                        <div class="col-md-4 col-12">
                            <span class="text-secondary">Description</span>
                        </div>
                        <div class="col-md-8 col-12">
                            <p class="card-text">${model.description}</p>
                        </div>
                    </div>

                    <div class="row mb-2">
                        <div class="col-md-4 col-12">
                            <span class="text-secondary">Authors</span>
                        </div>
                        <div class="col-md-8 col-12">
                            ${model.authors.map(author => `
                                <p class="p-0 m-0">${author.name}${author.affiliation ? ` (${author.affiliation})` : ''}${author.orcid ? ` (${author.orcid})` : ''}</p>
                            `).join('')}
                        </div>
                    </div>

                    <div class="row mb-2">
                        <div class="col-md-4 col-12">
                            <span class="text-secondary">Tags</span>
                        </div>
                        <div class="col-md-8 col-12">
                            ${model.tags.map(tag => `<span class="badge bg-primary me-1" style="cursor: pointer;" onclick="set_tag_as_query('${tag}')">${tag}</span>`).join('')}
                        </div>
                    </div>

                    <div class="row">
                        <div class="col-md-4 col-12"></div>
                        <div class="col-md-8 col-12">
                            <a href="${model.url}" class="btn btn-outline-primary btn-sm" id="search" style="border-radius: 5px;">
                                View model
                            </a>
                            <a href="/model/download/${model.id}" class="btn btn-outline-primary btn-sm" id="search" style="border-radius: 5px;">
                                Download (${model.total_size_in_human_format})
                            </a>
                        </div>
                    </div>

                </div>
            </div>
        `;

        document.getElementById('results').appendChild(card);
    });
});


document.getElementById('search-form').addEventListener('submit', function(event) {
    event.preventDefault();
    send_query();
});

