export async function cutDescriptionCatalogText() {
    const descriptions = document.querySelectorAll('.catalog_item .catalog_description');

    descriptions.forEach(description => {
        let text = description.textContent;

        if (text.length > 40) {
            description.textContent = text.substring(0, 40) + '...';
        }
    });
}
