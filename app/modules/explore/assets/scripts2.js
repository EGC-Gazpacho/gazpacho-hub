document.addEventListener('DOMContentLoaded', () => {
    send_query();
});

function send_query() {
    const queryInput = document.getElementById('query');
    const query = queryInput.value.trim();

    fetch('/explore2/models?query=' + encodeURIComponent(query))
        .then(response => response.json())
        .then(data => {
            const resultsDiv = document.getElementById('results');
            resultsDiv.innerHTML = '';

            // results counter
            const resultCount = data.length;
            const resultText = resultCount === 1 ? 'feature model' : 'feature models';
            document.getElementById('results_number').textContent = `${resultCount} ${resultText} found`;

            if (resultCount === 0) {
                document.getElementById("results_not_found").style.display = "block";
            } else {
                document.getElementById("results_not_found").style.display = "none";
            }

            data.forEach(model => {
                let card = document.createElement('div');
                card.className = 'col-12';
                card.innerHTML = `
                    <div class="card">
                        <div class="card-body">
                            <div class="d-flex align-items-center justify-content-between">
                                <h3><a href="${model.url}">${model.fm_meta_data.title}</a></h3>
                                <div>
                                    <a href="/featuremodel/download/${model.id}" class="btn btn-outline-primary btn-sm" id="search" style="border-radius: 5px;">
                                        Download (${model.total_size_in_human_format})
                                    </a>
                                </div>
                            </div>
                            <p class="text-secondary">${formatDate(model.created_at)}</p>
                            <p class="card-text">${model.fm_meta_data.description}</p>
                            <p class="card-text"><strong>Dataset:</strong> <a href="/dataset/${model.data_set_id}">${model.data_set_title}</a></p>
                        </div>
                    </div>
                `;

                resultsDiv.appendChild(card);
            });
        });
}

function formatDate(dateString) {
    const options = {day: 'numeric', month: 'long', year: 'numeric', hour: 'numeric', minute: 'numeric'};
    const date = new Date(dateString);
    return date.toLocaleString('en-US', options);
}

document.getElementById('search-form').addEventListener('submit', function(event) {
    event.preventDefault();
    send_query();
});