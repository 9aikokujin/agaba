export async function showMoreCharacters() {
    const charItems = document.querySelectorAll('.card_char-item');
    const showMoreBtn = document.querySelector('.show_more-chars-btn');

    if (charItems.length <= 4) {
        showMoreBtn.style.display = 'none';
        return;
    }

    const toggleItemsVisibility = (isExpanded) => {
        charItems.forEach((item, index) => {
            item.style.display = (index >= 4 && !isExpanded) ? 'none' : 'flex';
        });
        showMoreBtn.textContent = isExpanded ? 'Скрыть' : 'Показать все' ;
    };

    toggleItemsVisibility(false);

    showMoreBtn.addEventListener('click', function() {
        const isExpanded = showMoreBtn.textContent === 'Показать все';
        toggleItemsVisibility(isExpanded);
    });
}
