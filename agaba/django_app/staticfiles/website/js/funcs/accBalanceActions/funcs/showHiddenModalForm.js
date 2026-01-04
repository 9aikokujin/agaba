export function showHiddenModalForm() {
    const mainInputs = document.querySelectorAll('.modal__form_value_input._main_input');
    const hiddenContainers = document.querySelectorAll('.balance_hidden_cntr');

    if(!mainInputs.length || !hiddenContainers.length) return;

    mainInputs.forEach((input, index) => {
        input.addEventListener('click', (e) => {
            e.stopPropagation();
            hiddenContainers[index].classList.add('open');
        });
    });

    hiddenContainers.forEach((container) => {
        container.addEventListener('click', (e) => {
        e.stopPropagation();
        });
    });

    document.addEventListener('click', (e) => {
        mainInputs.forEach((input, index) => {
            if (!input.contains(e.target) && !hiddenContainers[index].contains(e.target)) {
                hiddenContainers[index].classList.remove('open');
            }
        });
    });
}