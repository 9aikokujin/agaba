export function showAccountOrderDeliveryFilters() {
    // Model: Управление состоянием
    const state = {
        filters: []
    };

    // View: Управление DOM
    const View = {
        filterBtns: document.querySelectorAll('.acc__all_orders_btn'),
        filterContents: document.querySelectorAll('.acc__all_orders_select'),

        toggleFilter(btn) {
            const container = btn.closest('.acc__order_filter_item');
            const content = container ? container.querySelector('.acc__all_orders_select') : null;
            const filterList = content ? content.querySelector('.filter_select-list') : null;

            if (!content || !filterList) {
                console.log('Кнопка с другим действием');
                return;
            }

            const isOpening = !btn.classList.contains('_active');
            if (isOpening) {
                this.closeAllFilters();
                this.openFilter(btn, content, filterList);
            } else {
                this.closeFilter(btn, content, filterList);
            }
        },

        openFilter(btn, content, filterList) {
            btn.classList.add('_active');
            content.classList.add('_open');
            const maxHeight = Math.min(filterList.scrollHeight, 124);
            content.style.maxHeight = `${maxHeight}px`;
            setTimeout(() => filterList.classList.add('_show'), 200);
        },

        closeFilter(btn, content, filterList) {
            filterList.classList.remove('_show');
            setTimeout(() => {
                btn.classList.remove('_active');
                content.classList.remove('_open');
                content.style.maxHeight = '0px';
            }, 200);
        },

        closeAllFilters() {
            this.filterBtns.forEach((btn) => {
                const container = btn.closest('.acc__order_filter_item');
                const content = container ? container.querySelector('.acc__all_orders_select') : null;
                if (!content) return;
                const filterList = content.querySelector('.filter_select-list');
                if (btn.classList.contains('_active')) {
                    this.closeFilter(btn, content, filterList);
                }
            });
        },

        updateButtonText(btn, checkboxes) {
            const checkedBoxes = Array.from(checkboxes).filter(checkbox => checkbox.checked);
            const btnStrong = btn.querySelector('strong');
            const countElement = btn.querySelector('i.__count');

            if (checkedBoxes.length === 0) {
                btnStrong.textContent = btn.dataset.initialText;
                if (countElement) {
                    countElement.style.display = 'none';
                }
            } else if (checkedBoxes.length > 3) {
                btnStrong.textContent = "Выбранные фильтры...";
                if (countElement) {
                    countElement.textContent = checkedBoxes.length;
                    countElement.style.display = 'inline-flex';
                }
            } else {
                const selectedLabels = checkedBoxes.map(checkbox => checkbox.nextElementSibling.textContent);
                btnStrong.textContent = selectedLabels.join(', ');
                if (countElement) {
                    countElement.textContent = checkedBoxes.length;
                    countElement.style.display = 'inline-flex';
                }
            }
        }
    };

    // Controller: Обработка событий
    const Controller = {
        init() {
            View.filterBtns.forEach((btn) => {
                const container = btn.closest('.acc__order_filter_item');
                const content = container ? container.querySelector('.acc__all_orders_select') : null;
                if (!content) return;

                const filterList = content.querySelector('.filter_select-list');
                const checkboxes = content.querySelectorAll('.filter_select-checkbox');

                const btnStrong = btn.querySelector('strong');
                btn.dataset.initialText = btnStrong.textContent;

                const countElement = btn.querySelector('i.__count');
                if (countElement) {
                    countElement.style.display = 'none';
                }

                btn.addEventListener('click', () => {
                    View.toggleFilter(btn);
                });

                checkboxes.forEach(checkbox => {
                    checkbox.addEventListener('change', () => {
                        View.updateButtonText(btn, checkboxes);
                    });
                });
            });

            document.addEventListener('click', this.handleClickOutside);
            document.addEventListener('keydown', this.handleEscKey);
        },

        handleClickOutside(event) {
            View.filterBtns.forEach((btn) => {
                const container = btn.closest('.acc__order_filter_item');
                const content = container ? container.querySelector('.acc__all_orders_select') : null;
                if (!content) return;
                const filterList = content.querySelector('.filter_select-list');

                if (btn.classList.contains('_active') &&
                    !btn.contains(event.target) &&
                    !content.contains(event.target)) {
                    View.closeFilter(btn, content, filterList);
                }
            });
        },

        handleEscKey(event) {
            if (event.key === 'Escape') {
                View.closeAllFilters();
            }
        }
    };

    Controller.init();
}
