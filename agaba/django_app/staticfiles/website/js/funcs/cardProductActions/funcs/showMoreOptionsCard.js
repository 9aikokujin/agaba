export async function showMoreOptionsCard() {
    const showMoreButton = document.querySelector('._show_more-option');
    const optionsList = document.querySelector('.card_product-options_list');
    const optionCounter = document.querySelector('.option_counter');

    showMoreButton.addEventListener('click', function() {
        const isVisible = optionsList.style.opacity === '1';
        if (isVisible) {
            optionsList.style.maxHeight = '0';
            optionsList.style.opacity = '0';
            optionsList.style.visibility = 'hidden';
        } else {
            optionsList.style.maxHeight = optionsList.scrollHeight + 'px';
            optionsList.style.opacity = '1';
            optionsList.style.visibility = 'visible';
        }
    });

    document.querySelectorAll('.card_option-btn').forEach(button => {
        button.addEventListener('click', function() {
            updateOptionCounter();
        });
    });

    function updateOptionCounter() {
        const activeButtonsCount = document
            .querySelectorAll('.card_option-btn.active').length;
            
        if (activeButtonsCount > 0) {
            optionCounter.textContent = `Добавлено ${activeButtonsCount}`;
            optionCounter.style.display = 'inline';
        } else {
            optionCounter.style.display = 'none';
        }
    }

    updateOptionCounter();
}
