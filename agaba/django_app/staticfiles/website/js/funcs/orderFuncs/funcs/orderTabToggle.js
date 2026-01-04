export async function orderTabToggle() {
    const tabButtons = document.querySelectorAll('.tab_toggle');
    const tabItems = document.querySelectorAll('.order_tab-item');

    if (tabButtons.length > 0 && tabItems.length > 0) {
        tabButtons[1].classList.add('active');
        tabItems[1].style.display = 'block';
        // глобальная переменная нужна для определения типа заказа безнал или лизинг в виде
        window.orderTabValue = 1;
    }

    tabItems.forEach((item, index) => {
        if (index !== 1) {
        item.style.display = 'none';
        }
    });

    tabButtons.forEach(button => {
        button.addEventListener('click', async () => {
        const tabValue = button.getAttribute('data-tab');


        tabButtons.forEach(btn => btn.classList.remove('active'));
        tabItems.forEach(item => item.style.display = 'none');

        
        button.classList.add('active');
        const activeTab = document.querySelector(`.order_tab-item[data-tab="${tabValue}"]`);
        if (activeTab) {
            activeTab.style.display = 'block';
            // глобальная переменная нужна для определения типа заказа безнал или лизинг в виде
            window.orderTabValue = tabValue;
            }
        });
    });
}  