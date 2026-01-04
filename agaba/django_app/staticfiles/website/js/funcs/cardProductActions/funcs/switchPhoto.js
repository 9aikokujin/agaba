export async function switchPhoto() {
    const bigImage = document.querySelector('.card_product-full img');

    const smallImages = document.querySelectorAll('.card_product-small img');

    smallImages.forEach(smallImage => {
        smallImage.addEventListener('click', function() {
            const bigImageSrc = bigImage.src;

            bigImage.src = this.src;

            this.src = bigImageSrc;
        });
    });
}
