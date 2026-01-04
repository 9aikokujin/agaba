export async function toggleSelectCatalog() {
    const buttonFilter = document.querySelectorAll('.filter_feature-btn.fltr');

    buttonFilter.forEach(button => {
        const index = button.getAttribute('data-index');
        const selectContainer = document.querySelector(`.filter_select-cntr[data-index="${index}"]`);

        if (!selectContainer) return;

        const strongElement = button.querySelector('strong');
        strongElement.setAttribute('data-original-text', strongElement.textContent);

        button.addEventListener('click', (event) => handleButtonClick(event, selectContainer, button));
        setupCheckboxListeners(selectContainer, button);
    });

    document.addEventListener('click', handleDocumentClick);
}

function handleButtonClick(event, selectContainer, button) {
    event.stopPropagation();
    toggleContainer(selectContainer, button);
    updateButtonLabel(selectContainer, button);
}

function setupCheckboxListeners(selectContainer, button) {
    const checkboxes = selectContainer.querySelectorAll('.filter_select-checkbox');
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', () => updateButtonLabel(selectContainer, button));
    });
}

function handleDocumentClick(event) {
    const buttonFilter = document.querySelectorAll('.filter_feature-btn.fltr');
    buttonFilter.forEach(button => {
        const index = button.getAttribute('data-index');
        const selectContainer = document.querySelector(`.filter_select-cntr[data-index="${index}"]`);

        if (!selectContainer) return;

        if (!button.contains(event.target) && !selectContainer.contains(event.target)) {
            closeContainer(selectContainer, button);
        }
    });
}

function toggleContainer(container, button) {
    const isOpen = container.style.maxHeight;
    isOpen ? closeContainer(container, button) : openContainer(container, button);
}

function closeContainer(container, button) {
    container.style.maxHeight = null;
    container.classList.remove('open');
    button.classList.remove('active');
}

function openContainer(container, button) {
    const maxHeight = 160;
    container.style.maxHeight = Math.min(container.scrollHeight, maxHeight) + "px";
    container.classList.add('open');
    button.classList.add('active');
}

function updateButtonLabel(container, button) {
    const checkboxes = container.querySelectorAll('.filter_select-checkbox');
    const labels = container.querySelectorAll('.filter_select-label');
    const strongElement = button.querySelector('strong');
    const originalText = strongElement.getAttribute('data-original-text'); 

    let selectedLabels = Array.from(checkboxes)
        .map((checkbox, index) => checkbox.checked ? labels[index].textContent : null)
        .filter(label => label !== null);

    if (selectedLabels.length === 0) {
        strongElement.textContent = originalText; 
    } else if (selectedLabels.length === 1) {
        strongElement.textContent = selectedLabels[0];
    } else {
        strongElement.textContent = `${selectedLabels[0]} и еще ${selectedLabels.length - 1}...`;
    }
}
