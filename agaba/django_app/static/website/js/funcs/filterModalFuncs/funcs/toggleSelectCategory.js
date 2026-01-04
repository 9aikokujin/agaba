export async function toggleSelectCategory() {
    const buttons = document.querySelectorAll('.off-btn');
    buttons.forEach(initializeButton);
}

function initializeButton(button) {
    const strongElement = button.querySelector('strong');
    strongElement.dataset.initialText = strongElement.textContent;
    button.addEventListener('click', handleButtonClick);
}

function handleButtonClick(event) {
    const button = event.currentTarget;
    const categorySelect = button.nextElementSibling;
    if (categorySelect) toggleCategory(categorySelect, button);
}

function toggleCategory(categorySelect, button) {
    categorySelect.classList.toggle('open') ? openCategory(categorySelect, button) : closeCategory(categorySelect, button);
}

function closeCategory(categorySelect, button) {
    categorySelect.classList.remove('open');
    button.classList.remove('active');
}

function openCategory(categorySelect, button) {
    closeAllOpenCategories();
    categorySelect.classList.add('open');
    button.classList.add('active');
}

function closeAllOpenCategories() {
    const openCategories = document.querySelectorAll('.category_select.open');
    openCategories.forEach(closeCategoryElement);
}

function closeCategoryElement(openCategory) {
    openCategory.classList.remove('open');
    const associatedButton = openCategory.previousElementSibling;
    if (associatedButton) associatedButton.classList.remove('active');
}

function updateButtonText(button) {
    const categorySelect = button.nextElementSibling;
    const checkedItems = categorySelect.querySelectorAll('.category_item input:checked');
    const values = Array.from(checkedItems).map(input => input.nextElementSibling.textContent.trim());

    const strongElement = button.querySelector('strong');
    strongElement.textContent = values.length > 0 ? values.join(', ') : strongElement.dataset.initialText;
}

document.querySelectorAll('.category_item input').forEach(input => {
    input.addEventListener('change', handleInputChange);
});

function handleInputChange(event) {
    const button = event.target.closest('.category_select').previousElementSibling;
    updateButtonText(button);
}
