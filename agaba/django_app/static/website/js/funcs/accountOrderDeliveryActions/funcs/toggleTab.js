export function toggleTab() {
    const tabToggleBtns = document.querySelectorAll('.order__tab_btn');
    const accTabItems = document.querySelectorAll('.acc__order_delivery');

    // Модель (Model)
    const createModel = () => {
        let state = {
            tabs: []
        };

        const initializeTabs = (tabButtons, tabItems) => {
            state.tabs = Array.from(tabButtons).map((button, index) => {
                const tabIndex = button.getAttribute('tab-index');
                const itemCount = document.querySelectorAll(`[tab-index="${tabIndex}"] .catalog__list._seller_orders .catalog_item`).length;
                return {
                    button,
                    tabIndex,
                    itemCount,
                    content: tabItems[index]
                };
            });
        };

        const getTabByIndex = (tabIndex) => state.tabs.find(tab => tab.tabIndex === tabIndex);

        return {
            initializeTabs,
            getTabByIndex,
            getState: () => state
        };
    };

    // Представление (View)
    const createView = (model) => {
        const render = () => {
            model.getState().tabs.forEach(tab => {
                const counterElement = tab.button.querySelector('._item_counter');
                if (counterElement) {
                    counterElement.textContent = tab.itemCount;
                }
            });
        };

        const updateActiveTab = (activeTab) => {
            model.getState().tabs.forEach(tab => {
                tab.button.classList.toggle('active', tab === activeTab);
                tab.content.style.display = tab === activeTab ? 'flex' : 'none';
            });
        };

        return {
            render,
            updateActiveTab
        };
    };

    // Контроллер (Controller)
    const model = createModel();
    model.initializeTabs(tabToggleBtns, accTabItems);

    const view = createView(model);
    view.render();

    tabToggleBtns.forEach(button => {
        button.addEventListener('click', () => {
        const tabValue = button.getAttribute('tab-index');
            const activeTab = model.getTabByIndex(tabValue);
        if (activeTab) {
                view.updateActiveTab(activeTab);
            }
        });
    });

    // Устанавливаем начальное активное состояние
    if (model.getState().tabs.length > 0) {
        view.updateActiveTab(model.getState().tabs[0]);
    }
}
