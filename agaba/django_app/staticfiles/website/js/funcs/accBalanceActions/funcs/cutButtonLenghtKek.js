export function cutButtonLenghtKek() {
    function updateBtnText() {
        const cutBtn = document.querySelector('.balance_tab_btn[data-tab="all_operations"] strong');

        if(!cutBtn) return;
    
        if(window.innerWidth <= 600) {
            if(cutBtn.textContent.length > 3) {
                cutBtn.textContent = 'Все';
            }
        } else {
            cutBtn.textContent = 'Все операции';
        }
    }

    updateBtnText();

    window.addEventListener('resize', updateBtnText);

    return () => window.removeEventListener('resize', updateBtnText);
}