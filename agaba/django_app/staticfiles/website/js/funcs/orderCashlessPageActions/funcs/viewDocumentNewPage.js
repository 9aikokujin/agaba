export function viewDocumentNewPage() {
    const viewButtons = document.querySelectorAll('.order_doc-view_doc-btn');
  
    viewButtons.forEach(button => {
      button.addEventListener('click', (event) => {
        event.preventDefault();
  
        const downloadButton = button.closest('.order_docs-item').querySelector('.order_doc_download_btn');
        const documentUrl = downloadButton.getAttribute('href');
  
        if (documentUrl) {
          window.open(documentUrl, '_blank');
        }
      });
    });
  }
  