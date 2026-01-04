export function cutDocumentDescription() {
    const docItems = document.querySelectorAll('.order_docs-item');
    
    if(!docItems) return;

    docItems.forEach(item => {
        const docName = item.querySelector('.order_doc-name');
        const btnActions = item.querySelector('.order_doc-btn_actions');

            const availableWidth = item.clientWidth - btnActions.clientWidth - 20;
        if (docName.scrollWidth > availableWidth) {
            let text = docName.textContent;
            let trimmedText = text;

            while (docName.scrollWidth > availableWidth && trimmedText.length > 0) {
            trimmedText = trimmedText.slice(0, -1);
            docName.textContent = trimmedText + '...';
            }
        }
    });
}
  