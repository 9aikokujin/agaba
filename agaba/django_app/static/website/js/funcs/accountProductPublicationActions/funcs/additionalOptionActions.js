export function additionalOptionActions() {
  // Model: Управляет состоянием для каждого блока
  const createState = () => ({
    isActive: false,
    options: []
  });

  // View: Обновляет DOM в соответствии с состоянием
  const updateView = (block, state) => {
    const addButton = block.querySelector('.add__options_btn');
    const optionsSelect = block.querySelector('.acc__all_orders_select');

    if (!addButton || !optionsSelect) return;

    if (state.isActive) {
      addButton.classList.add('_active');
      optionsSelect.classList.add('_open');
    } else {
      addButton.classList.remove('_active');
      optionsSelect.classList.remove('_open');
    }
  };

  const createOptionElement = (name, price) => {
    const optionItem = document.createElement('li');
    optionItem.className = 'added__chars_item';
    optionItem.innerHTML = `
      <div data-id="additional_option" class="add__char_btn _cntr b_g_toggle_btn btn _flex_center">
        <button class="add__char_close">
          <img src="/static/website/img/accPublication/closeSvg.svg" alt="">
        </button>
        <strong class="_option__name">${name}</strong>
        <i class="_option__price">${price} ₽</i>
      </div>
    `;
    return optionItem;
  };

  // Controller: Обрабатывает события и обновляет модель и представление
  const handleAddButtonClick = (block, state, e) => {
    e.stopPropagation();
    state.isActive = !state.isActive;
    updateView(block, state);
  };

  const handleDocumentClick = (e, block, state) => {
    const optionsSelect = block.querySelector('.acc__all_orders_select');
    if (!optionsSelect.contains(e.target) && state.isActive) {
      state.isActive = false;
      updateView(block, state);
    }
  };

  const handleEscKeyPress = (e, block, state) => {
    if (e.key === 'Escape' && state.isActive) {
      state.isActive = false;
      updateView(block, state);
    }
  };

  const handleCreateOption = (block) => {
    const nameInput = block.querySelector('.add__options_input');
    const priceInput = block.querySelector('.add__price_input');
    const name = nameInput.value.trim();
    const price = priceInput.value.trim();

    if (name.length > 0 && name.length <= 40 && price.length > 0 && price.length <= 40) {
      const optionElement = createOptionElement(name, price);
      block.querySelector('.added__chars_list').appendChild(optionElement);

      nameInput.value = '';
      priceInput.value = '';
    }
  };

  const handleOptionClose = (e) => {
    if (e.target.closest('.add__char_close')) {
      e.target.closest('.added__chars_item').remove();
    }
  };

  // Инициализация: Устанавливаем обработчики событий
  const init = () => {
    const blocks = document.querySelectorAll('[data-optional-block]');
    if (!blocks.length) return;


    blocks.forEach(block => {
      const state = createState();
      const addButton = block.querySelector('.add__options_btn');
      const createButton = block.querySelector('.add__options_create_btn');
      const addedCharsList = block.querySelector('.added__chars_list');

      if (!addButton || !createButton || !addedCharsList) return;

      const nameInput = block.querySelector('.add__options_input');
      const priceInput = block.querySelector('.add__price_input');
      if (nameInput) nameInput.setAttribute('maxlength', '40');
      if (priceInput) priceInput.setAttribute('maxlength', '40');

      addButton.addEventListener('click', (e) => handleAddButtonClick(block, state, e));
      document.addEventListener('click', (e) => handleDocumentClick(e, block, state));
      document.addEventListener('keydown', (e) => handleEscKeyPress(e, block, state));
      createButton.addEventListener('click', () => handleCreateOption(block));
      addedCharsList.addEventListener('click', handleOptionClose);
    });
  };

  init();
}
