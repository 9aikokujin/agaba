export function filterTabActions(onTabChange) {
    const ITEMS_PER_PAGE = 10;
    const tabButtons = document.querySelectorAll('.balance_tab_btn');
    const operationItems = document.querySelectorAll('.operation_body_item');

    if(!tabButtons?.length || !operationItems?.length) return;

    const initializeDisplay = (items, limit) => {
        items.forEach((item, index) => {
            const isVisible = index < limit;
            item.style.display = isVisible ? 'flex' : 'none';
        });
    };

    const handleTabClick = (button) => {
        const selectedTab = button.dataset.tab;
        if(!selectedTab) return;

        tabButtons.forEach(btn => btn.classList.toggle('active', btn === button));

        let visibleCount = 0;
        operationItems.forEach(item => {
            const shouldBeVisible = selectedTab === 'all_operations'
                                    || 
                                    item.dataset.tab === selectedTab;

            const isVisible = shouldBeVisible && visibleCount < ITEMS_PER_PAGE;
            item.style.display = isVisible ? 'flex' : 'none';
            item.style.opacity = isVisible ? '1' : '0';
            item.style.pointerEvents = isVisible ? 'auto' : 'none';
            
            if (shouldBeVisible) visibleCount++;
        });

        if(onTabChange) onTabChange(selectedTab);
    };

    initializeDisplay(operationItems, ITEMS_PER_PAGE);
    const defaultTab = document.querySelector('[data-tab="all_operations"]');
    if(defaultTab) defaultTab.classList.add('active');

    tabButtons.forEach(button => {
        button.addEventListener('click', () => handleTabClick(button));
    });
}
