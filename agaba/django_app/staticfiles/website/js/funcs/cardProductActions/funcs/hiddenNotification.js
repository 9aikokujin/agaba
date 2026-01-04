export async function hiddenNotification() {
    const buttons = {
        compare: document.querySelector('.compare-btn'),
        follow: document.querySelector('.follow-btn'),
        report: document.querySelector('.report-btn'),
        dropPrice: document.querySelector('.product_drop-price_btn'),
        delivery: document.querySelector('.delivery-btn'),
        logistic: document.querySelector('.logistic_org-btn')
    };

    const notifications = {
        compare: document.querySelector('.compare_notification'),
        follow: document.querySelector('.follow_notification'),
        report: document.querySelector('.report_notification'),
        dynamicPrice: document.querySelector('.dynamic_price-cntr'),
        deliveryCalculate: document.querySelector('.delivery_calculate-cntr'),
        sellerInfo: document.querySelector('.seller_pop-info-cntr')
    };

    const reportLabels = notifications.report ? notifications.report.querySelectorAll('.report_label') : [];
    const reportTextNotif = notifications.report ? notifications.report.querySelector('.report_text-notif') : null;
    const reportTitle = notifications.report ? notifications.report.querySelector('.report_notification h4') : null;
    const deliveryInput = notifications.deliveryCalculate ? notifications.deliveryCalculate.querySelector('.delivery_input') : null;
    const deliveryMethodsList = notifications.deliveryCalculate ? notifications.deliveryCalculate.querySelector('.delivery_methods-list') : null;
    const showCalcPriceBtn = notifications.deliveryCalculate ? notifications.deliveryCalculate.querySelector('.show_calc-price-btn') : null;

    const toggleNotification = (notification, show) => {
        if (notification) {
            notification.style.opacity = show ? '1' : '0';
            notification.style.visibility = show ? 'visible' : 'hidden';
        }
    };

    const setupButtonListener = (button, notification) => {
        if (button && notification) {
            button.addEventListener('click', (event) => {
                event.stopPropagation();
                const isVisible = notification.style.opacity === '1';
                toggleNotification(notification, !isVisible);
            });
        }
    };

    setupButtonListener(buttons.compare, notifications.compare);
    setupButtonListener(buttons.follow, notifications.follow);

    if (buttons.report && notifications.report) {
        buttons.report.addEventListener('click', (event) => {
            event.stopPropagation();
            const isVisible = notifications.report.style.opacity === '1';
            toggleNotification(notifications.report, !isVisible);
            if (!isVisible && reportTextNotif && reportLabels.length > 0) {
                reportTextNotif.style.display = 'none';
                reportLabels.forEach(label => label.style.display = 'block');
            }
        });

        reportLabels.forEach(label => {
            label.addEventListener('click', () => {
                reportLabels.forEach(label => label.style.display = 'none');
                if (reportTextNotif) reportTextNotif.style.display = 'block';
                if (reportTitle) reportTitle.textContent = 'Спасибо!';
            });
        });
    }

    setupButtonListener(buttons.dropPrice, notifications.dynamicPrice);
    setupButtonListener(buttons.delivery, notifications.deliveryCalculate);

    if (deliveryInput && deliveryMethodsList) {
        deliveryInput.addEventListener('input', () => {
            if (deliveryInput.value.length >= 3) {
                deliveryMethodsList.style.maxHeight = deliveryMethodsList.scrollHeight + 'px';
            } else {
                deliveryMethodsList.style.maxHeight = '0';
            }
        });
    }

    if (showCalcPriceBtn) {
        showCalcPriceBtn.addEventListener('click', () => {
            toggleNotification(notifications.deliveryCalculate, false);
        });
    }

    setupButtonListener(buttons.logistic, notifications.sellerInfo);

    document.addEventListener('click', (event) => {
        Object.keys(notifications).forEach(key => {
            if (notifications[key] && !notifications[key].contains(event.target) 
                && buttons[key] && !buttons[key].contains(event.target)) {
                toggleNotification(notifications[key], false);
            }
        });
    });

    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape') {
            Object.keys(notifications).forEach(key => {
                if (notifications[key]) {
                    toggleNotification(notifications[key], false);
                }
            });
        }
    });
}
