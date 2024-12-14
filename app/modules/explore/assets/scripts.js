document.addEventListener('DOMContentLoaded', () => {
    populateNumberOfFeatures(1, 1000);
    populateNumberOfProducts(1, 1000);
    send_query();
});

function send_query() {

    console.log("send query...")

    document.getElementById('results').innerHTML = '';
    document.getElementById("results_not_found").style.display = "none";
    console.log("hide not found icon");

    const filters = document.querySelectorAll('#filters input, #filters select, #filters [type="radio"]');

    filters.forEach(filter => {
        filter.addEventListener('input', () => {
            const csrfToken = document.getElementById('csrf_token').value;

            const searchCriteria = {
                csrf_token: csrfToken,
                query: document.querySelector('#query').value,
                publication_type: document.querySelector('#publication_type').value,
                number_of_features: document.querySelector('#number_of_features').value,
                number_of_products: document.querySelector('#number_of_products').value,
                sorting: document.querySelector('[name="sorting"]:checked').value,
            };

            console.log(document.querySelector('#publication_type').value);
            console.log(document.querySelector('#number_of_features').value);
            console.log(document.querySelector('#number_of_products').value);

            fetch('/explore', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(searchCriteria),
            })
                .then(response => response.json())
                .then(data => {

                    console.log(data);
                    document.getElementById('results').innerHTML = '';

                    // results counter
                    const resultCount = data.length;
                    const resultText = resultCount === 1 ? 'dataset' : 'datasets';
                    document.getElementById('results_number').textContent = `${resultCount} ${resultText} found`;

                    if (resultCount === 0) {
                        console.log("show not found icon");
                        document.getElementById("results_not_found").style.display = "block";
                    } else {
                        document.getElementById("results_not_found").style.display = "none";
                    }


                    data.forEach(dataset => {
                        let card = document.createElement('div');
                        card.className = 'col-12';
                        card.innerHTML = `
                            <div class="card">
                                <div class="card-body">
                                    <div class="d-flex align-items-center justify-content-between">
                                        <h3><a href="${dataset.url}">${dataset.title}</a></h3>
                                        <div>
                                            <span class="badge bg-primary" style="cursor: pointer;" onclick="set_publication_type_as_query('${dataset.publication_type}')">${dataset.publication_type}</span>
                                        </div>
                                        <div>
                                            <span class="badge bg-primary" style="cursor: pointer;" onclick="set_number_of_features_as_query('${dataset.number_of_features}')">${dataset.number_of_features}</span>
                                        </div>
                                        <div>
                                            <span class="badge bg-primary" style="cursor: pointer;" onclick="set_number_of_products_as_query('${dataset.number_of_products}')">${dataset.number_of_products}</span>
                                        </div>
                                    </div>
                                    <p class="text-secondary">${formatDate(dataset.created_at)}</p>

                                    <div class="row mb-2">

                                        <div class="col-md-4 col-12">
                                            <span class=" text-secondary">
                                                Description
                                            </span>
                                        </div>
                                        <div class="col-md-8 col-12">
                                            <p class="card-text">${dataset.description}</p>
                                        </div>

                                    </div>

                                    <div class="row mb-2">

                                        <div class="col-md-4 col-12">
                                            <span class=" text-secondary">
                                                Authors
                                            </span>
                                        </div>
                                        <div class="col-md-8 col-12">
                                            ${dataset.authors.map(author => `
                                                <p class="p-0 m-0">${author.name}${author.affiliation ? ` (${author.affiliation})` : ''}${author.orcid ? ` (${author.orcid})` : ''}</p>
                                            `).join('')}
                                        </div>

                                    </div>

                                    <div class="row mb-2">

                                        <div class="col-md-4 col-12">
                                            <span class=" text-secondary">
                                                Tags
                                            </span>
                                        </div>
                                        <div class="col-md-8 col-12">
                                            ${dataset.tags.map(tag => `<span class="badge bg-primary me-1" style="cursor: pointer;" onclick="set_tag_as_query('${tag}')">${tag}</span>`).join('')}
                                        </div>

                                    </div>

                                    <div class="row">

                                        <div class="col-md-4 col-12">

                                        </div>
                                        <div class="col-md-8 col-12">
                                            <a href="${dataset.url}" class="btn btn-outline-primary btn-sm" id="search" style="border-radius: 5px;">
                                                View dataset
                                            </a>
                                            <a href="/dataset/download/${dataset.id}" class="btn btn-outline-primary btn-sm" id="search" style="border-radius: 5px;">
                                                Download (${dataset.total_size_in_human_format})
                                            </a>
                                            <a href="/github/upload/${dataset.id}" class="btn btn-outline-primary btn-sm" id="search" style="border-radius: 5px;">
                                                Backup dataset to GitHub 
                                            </a>
                                        </div>


                                    </div>

                                    <div class="row mb-2">
                                        <div class="col-md-12 d-flex justify-content-between align-items-center" style="min-height: 60px;">
                                                <span>Rating</span>
                                                <!-- Promedio -->
                                                <span id="average-rating-${dataset.id}" 
                                                    class="ms-2" 
                                                    style="font-size: 1.2em; color: #000;">
                                                    ${dataset.rating ? dataset.rating.toFixed(1) + '/5' : '0.0/5'}
                                                </span>
                                            </div>
                                        </div>
                                    </div>

                                </div>
                            </div>
                        `;

                        document.getElementById('results').appendChild(card);
                    });
                });
        });
    });
}


function formatDate(dateString) {
    const options = {day: 'numeric', month: 'long', year: 'numeric', hour: 'numeric', minute: 'numeric'};
    const date = new Date(dateString);
    return date.toLocaleString('en-US', options);
}

function set_tag_as_query(tagName) {
    const queryInput = document.getElementById('query');
    queryInput.value = tagName.trim();
    queryInput.dispatchEvent(new Event('input', {bubbles: true}));
}

function set_publication_type_as_query(publicationType) {
    const publicationTypeSelect = document.getElementById('publication_type');
    for (let i = 0; i < publicationTypeSelect.options.length; i++) {
        if (publicationTypeSelect.options[i].text === publicationType.trim()) {
            // Set the value of the select to the value of the matching option
            publicationTypeSelect.value = publicationTypeSelect.options[i].value;
            break;
        }
    }
    publicationTypeSelect.dispatchEvent(new Event('input', {bubbles: true}));
}

function set_number_of_features_as_query(numberOfFeatures) {
    const numberOfFeaturesSelect = document.getElementById('number_of_features');
    for (let i = 0; i < numberOfFeaturesSelect.options.length; i++) {
        if (numberOfFeaturesSelect.options[i].text === numberOfFeatures.trim()) {
            // Set the value of the select to the value of the matching option
            numberOfFeaturesSelect.value = numberOfFeaturesSelect.options[i].value;
            break;
        }
    }
    numberOfFeaturesSelect.dispatchEvent(new Event('input', {bubbles: true}));
}

function set_number_of_products_as_query(numberOfProducts) {
    const numberOfProductsSelect = document.getElementById('number_of_products');
    for (let i = 0; i < numberOfProductsSelect.options.length; i++) {
        if (numberOfProductsSelect.options[i].text === numberOfProducts.trim()) {
            // Set the value of the select to the value of the matching option
            numberOfProductsSelect.value = numberOfProductsSelect.options[i].value;
            break;
        }
    }
    numberOfProductsSelect.dispatchEvent(new Event('input', {bubbles: true}));
}

function populateNumberOfFeatures(min, max) {
    const numberOfFeaturesSelect = document.getElementById('number_of_features');

    // Clear existing options (except "Any")
    numberOfFeaturesSelect.innerHTML = '<option value="any">Any</option>';

    // Populate with numbers from min to max
    for (let i = min; i <= max; i++) {
        const option = document.createElement('option');
        option.value = i;
        option.textContent = i;
        numberOfFeaturesSelect.appendChild(option);
    }
}

function populateNumberOfProducts(min, max) {
    const numberOfProductsSelect = document.getElementById('number_of_products');

    // Clear existing options (except "Any")
    numberOfProductsSelect.innerHTML = '<option value="any">Any</option>';

    // Populate with numbers from min to max
    for (let i = min; i <= max; i++) {
        const option = document.createElement('option');
        option.value = i;
        option.textContent = i;
        numberOfProductsSelect.appendChild(option);
    }
}


document.getElementById('clear-filters').addEventListener('click', clearFilters);

function clearFilters() {

    // Reset the search query
    let queryInput = document.querySelector('#query');
    queryInput.value = "";
    // queryInput.dispatchEvent(new Event('input', {bubbles: true}));

    // Reset the publication type to its default value
    let publicationTypeSelect = document.querySelector('#publication_type');
    publicationTypeSelect.value = "any"; // replace "any" with whatever your default value is
    // publicationTypeSelect.dispatchEvent(new Event('input', {bubbles: true}));

    // Reset the number of features to its default value
    let numberOfFeaturesSelect = document.querySelector('#number_of_features');
    numberOfFeaturesSelect.value = "";

    // Reset the number of products to its default value
    let numberOfProductsSelect = document.querySelector('#number_of_products');
    numberOfProductsSelect.value = "";

    // Reset the sorting option
    let sortingOptions = document.querySelectorAll('[name="sorting"]');
    sortingOptions.forEach(option => {
        option.checked = option.value == "newest"; // replace "default" with whatever your default value is
        // option.dispatchEvent(new Event('input', {bubbles: true}));
    });

    // Perform a new search with the reset filters
    queryInput.dispatchEvent(new Event('input', {bubbles: true}));
}

document.addEventListener('DOMContentLoaded', () => {

    console.log('DOMContentLoaded event triggered');

    const datasetIds = Array.from(document.querySelectorAll('[id^="average-rating-"]'))
        .map(element => element.id.replace('average-rating-', ''));

    console.log('Dataset IDs found:', datasetIds);

    //let queryInput = document.querySelector('#query');
    //queryInput.dispatchEvent(new Event('input', {bubbles: true}));

    let urlParams = new URLSearchParams(window.location.search);
    let queryParam = urlParams.get('query');

    if (queryParam && queryParam.trim() !== '') {

        const queryInput = document.getElementById('query');
        queryInput.value = queryParam
        queryInput.dispatchEvent(new Event('input', {bubbles: true}));
        console.log("throw event");

    } else {
        const queryInput = document.getElementById('query');
        queryInput.dispatchEvent(new Event('input', {bubbles: true}));
    }

    // Actualizar el promedio para cada dataset
    datasetIds.forEach(datasetId => {
        avgRateUpdate(datasetId);
    });
});

document.addEventListener('DOMContentLoaded', function () {
    const datasetIds = Array.from(document.querySelectorAll('[id^="average-rating-"]'))
        .map(el => el.id.split('-')[2]); // Obtener los IDs de dataset desde el HTML

    console.log('Dataset IDs found:', datasetIds);

    // Obtener y actualizar el promedio para cada dataset
    datasetIds.forEach(datasetId => {
        fetchAverageRating(datasetId);
    });

    // Función para obtener el promedio desde el backend
    function fetchAverageRating(datasetId) {
        console.log(`Fetching average rating for datasetId: ${datasetId}`);
        fetch(`/datasets/${datasetId}/average-rating`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Failed to fetch average rating. Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log(`Average rating for datasetId ${datasetId}:`, data);
                updateAverageRating(datasetId, data.average_rating || 0);
            })
            .catch(error => {
                console.error(`Error fetching average rating for datasetId ${datasetId}:`, error);
            });
    }

    // Función para actualizar el promedio en el DOM
    function updateAverageRating(datasetId, averageRating) {
        const avgRatingElement = document.getElementById(`average-rating-${datasetId}`);
        if (avgRatingElement) {
            avgRatingElement.innerText = averageRating.toFixed(1); // Mostrar el promedio con 1 decimal
            console.log(`Updated average rating for datasetId ${datasetId}: ${averageRating}`);
        } else {
            console.warn(`Element with ID average-rating-${datasetId} not found in DOM.`);
        }
    }
});

