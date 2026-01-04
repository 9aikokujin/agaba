export async function showPricePopover() {
    document.querySelectorAll('.card_option-btn').forEach(button => {
        button.addEventListener('click', async function() {

            this.classList.toggle('active');
        });
    });
}
