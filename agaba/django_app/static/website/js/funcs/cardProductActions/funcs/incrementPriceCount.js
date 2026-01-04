export async function incrementPriceCount() {
    const buttons = document.querySelectorAll('.card_option-btn');
    const priceElement = document.querySelector('.product-order_price .prod_count');

    if(!priceElement) return;

    let currentPrice = parseInt(priceElement.textContent.replace(/\D/g, ''), 10);

    buttons.forEach(button => {
        button.addEventListener('click', async function() {

            const popoverItem = this.nextElementSibling.querySelector('.options_popover-item');
            const popoverValue = parseInt(popoverItem.textContent.replace(/\D/g, ''), 10);

            if (this.classList.contains('active')) {
                animatePriceChange(currentPrice, currentPrice + popoverValue, priceElement);
                currentPrice += popoverValue;
            } else {

                animatePriceChange(currentPrice, currentPrice - popoverValue, priceElement);
                currentPrice -= popoverValue;
            }
        });
    });
}

function animatePriceChange(startValue, endValue, element) {
    const duration = 1000;
    const startTime = performance.now();
    const createOrderButton = document.querySelector('#create_order');

    createOrderButton.style.pointerEvents = 'none';
    createOrderButton.style.opacity = '0.5';

    function updatePrice(currentTime) {
        const elapsedTime = currentTime - startTime;
        const progress = Math.min(elapsedTime / duration, 1);

        const currentValue = Math.floor(startValue + (endValue - startValue) * progress);
        element.textContent = currentValue.toLocaleString('ru-RU', {
            style: 'currency',
            currency: 'RUB',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        });

        if (progress < 1) {
            requestAnimationFrame(updatePrice);
        } else {
            createOrderButton.style.pointerEvents = 'auto';
            createOrderButton.style.opacity = '1';
        }

    }

    requestAnimationFrame(updatePrice);

}