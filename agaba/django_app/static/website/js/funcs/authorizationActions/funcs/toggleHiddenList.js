export async function toggleHiddenList() {
    const inputFieldElement = document.querySelector('.org_inn-input');
    const hiddenContainerElement = document.querySelector('.org_inn-cntr');

    function openHiddenContainer() {
        // dynamic height
        // hiddenContainerElement.style.maxHeight = hiddenContainerElement.scrollHeight + 'px';
        hiddenContainerElement.classList.add('open');
    }

    function closeHiddenContainer() {
        // dynamic height
        // hiddenContainerElement.style.maxHeight = '0';
        hiddenContainerElement.classList.remove('open');
    }

    inputFieldElement.addEventListener('input', () => {
        if (inputFieldElement.value === '') {
            closeHiddenContainer();
        } else {
            openHiddenContainer();
        }
    });

    inputFieldElement.addEventListener('focus', () => {
        if (inputFieldElement.value !== '') {
            openHiddenContainer();
        }
    });

    document.addEventListener('click', (e) => {
        if (!hiddenContainerElement.contains(e.target) &&
            !inputFieldElement.contains(e.target)) {
            closeHiddenContainer();
        }
    });
}
