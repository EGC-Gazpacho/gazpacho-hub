document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('query');
    if (searchInput) {
        console.log('Search input found');
        searchInput.addEventListener('input', filterModels);
    } else {
        console.log('Search input not found');
    }
});

function filterModels() {
    const query = document.getElementById('query').value.toLowerCase();
    console.log('Query:', query);

    const cards = document.querySelectorAll('.card');
    console.log('Number of cards:', cards.length);
    let found = false;

    cards.forEach(card => {
        const title = card.querySelector('.card-title').textContent.toLowerCase();
        console.log('Card title:', title);
        if (title.includes(query)) {
            console.log('Match found:', title);
            card.style.display = 'block';
            found = true;
        } else {
            console.log('No match:', title);
            card.style.display = 'none';
        }
    });

    const resultsNotFound = document.getElementById('results_not_found');
    if (found) {
        console.log('Models found');
        resultsNotFound.style.display = 'none';
    } else {
        console.log('No models found');
        resultsNotFound.style.display = 'block';
    }
}