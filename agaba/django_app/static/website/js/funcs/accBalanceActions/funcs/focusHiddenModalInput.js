export function focusHiddenModalInput() {
    const inputs = document.querySelectorAll('.modal__form_value_input');

    if(!inputs) return;

    const getLabel = (input) => {
        const container = input.closest('.modal__form_input_cntr');
        const label = container?.querySelector('.modal__form_label');
        return label;
    }

    const toggleLabelClass = (label, shouldAdd) => {
        shouldAdd ? label.classList.add('_up_label') : label.classList.remove('_up_label');
    }

    const updateLabelState = (input) => {
        const label = getLabel(input);
        if (!label) return;
        toggleLabelClass(label, input.value.length > 0);
    };

    inputs.forEach((input) => {
        updateLabelState(input); // Обновляем состояние при инициализации

        const observer = new MutationObserver(() => {
            updateLabelState(input);
        });

        observer.observe(input, {
            attributes: true,
            attributeFilter: ['value']
        });

        input.addEventListener('focus', () => {
            const label = getLabel(input);
            toggleLabelClass(label, true);
        });

        input.addEventListener('input', () => {
            const label = getLabel(input);
            toggleLabelClass(label, input.value.length > 0);
        });

        document.addEventListener('click', (e) => {
            const container = input.closest('.modal__form_input_cntr');
            if(!container.contains(e.target) && input.value.length === 0) {
                const label = getLabel(input);
                toggleLabelClass(label, false);
            }
        });
    });
}