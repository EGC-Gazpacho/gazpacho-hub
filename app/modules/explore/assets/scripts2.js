document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('query');
    if (searchInput) {
        console.log('Search input found');
        searchInput.addEventListener('input', send_query);
    } else {
        console.log('Search input not found');
    }
});

function send_query() {
    const query = document.getElementById('query').value;
    console.log('Query:', query);

    fetch(`/explore2/models?query=${encodeURIComponent(query)}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
    })
    .then(response => {
        console.log('Response status:', response.status);
        return response.json();
    })
    .then(data => {
        console.log('Data received:', data);
        const resultsContainer = document.getElementById('results');
        resultsContainer.innerHTML = '';

        if (data.length === 0) {
            document.getElementById("results_not_found").style.display = "block";
        } else {
            document.getElementById("results_not_found").style.display = "none";
            data.forEach(model => {
                const card = document.createElement('div');
                card.className = 'col-12 mb-4';
                card.innerHTML = `
                    <div class="card">
                        <div class="card-body">
                            <h5 class="card-title">${model.fm_meta_data.title}</h5>
                            <p class="card-text">${model.fm_meta_data.uvl_filename}</p>
                        </div>
                    </div>
                `;
                resultsContainer.appendChild(card);
            });
        }
    })
    .catch(error => console.error('Error:', error));
}