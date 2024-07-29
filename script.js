document.addEventListener('DOMContentLoaded', () => {
    const portfolioList = document.getElementById('portfolio-list');
    const addItemForm = document.getElementById('add-item-form');

    addItemForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        const itemName = document.getElementById('item-name').value;
        const itemValue = document.getElementById('item-value').value;

        if (itemName && itemValue) {
            const portfolioItem = document.createElement('div');
            portfolioItem.classList.add('portfolio-item');
            portfolioItem.innerHTML = `<strong>${itemName}</strong>: $${itemValue}`;
            
            portfolioList.appendChild(portfolioItem);

            // Clear form fields
            addItemForm.reset();
        }
    });
});
