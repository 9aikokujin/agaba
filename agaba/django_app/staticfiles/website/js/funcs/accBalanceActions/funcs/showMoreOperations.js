export function showMoreOperations() {
    const CONFIG = {
        ITEMS_PER_PAGE: 10,
        ANIMATION_DURATION: 500,
        ANIMATION_DELAY: 10
    };

    const showMoreBtn = document.querySelector('.balance__operation_show_more');
    if(!showMoreBtn) return;

    let state = {
        visibleItems: 0,
        currentTab: 'all_operations'
    };

    const getVisibleOperations = () => {
        const items = document.querySelectorAll('.operation_body_item');
        return Array.from(items).filter(item => 
            state.currentTab === 'all_operations'
            || 
            item.dataset.tab === state.currentTab
        );
    };

    const updateItemVisibility = (item, isVisible) => {
        item.style.display = isVisible ? 'flex' : 'none';
        item.style.opacity = isVisible ? '1' : '0';
        item.style.pointerEvents = isVisible ? 'auto' : 'none';
        item.style.transition = `opacity ${CONFIG.ANIMATION_DURATION}ms ease`;
    };

    const updateShowMoreButton = (totalItems) => {
        showMoreBtn.style.display = totalItems <= CONFIG.ITEMS_PER_PAGE ? 'none' : 'flex';

        if (totalItems > CONFIG.ITEMS_PER_PAGE) {
            showMoreBtn.textContent = state.isExpanded ? 'Скрыть операции' : 'Показать еще';
        }
    };

    const showNextBatch = () => {
        const visibleOperations = getVisibleOperations();
        
        if (state.isExpanded) {
            visibleOperations.forEach((item, index) => {
                updateItemVisibility(item, index < CONFIG.ITEMS_PER_PAGE);
            });
            state.visibleItems = CONFIG.ITEMS_PER_PAGE;
            state.isExpanded = false;
        } else {
            visibleOperations.forEach(item => {
                updateItemVisibility(item, true);
            });
            state.visibleItems = visibleOperations.length;
            state.isExpanded = true;
        }

        updateShowMoreButton(visibleOperations.length);
    };

    const handleTabChange = (newTab) => {
        state.currentTab = newTab;
        state.visibleItems = 0;
        
        const visibleOperations = getVisibleOperations();
        visibleOperations.forEach((item, index) => {
            updateItemVisibility(item, index < CONFIG.ITEMS_PER_PAGE);
            if(index < CONFIG.ITEMS_PER_PAGE) state.visibleItems++;
        });

        updateShowMoreButton(visibleOperations.length);
    };

    handleTabChange(state.currentTab);

    showMoreBtn.addEventListener('click', () => {
        showMoreBtn.disabled = true;
        setTimeout(() => {
            showNextBatch();
            showMoreBtn.disabled = false;
        }, CONFIG.ANIMATION_DURATION);
    });

    return handleTabChange;
}
