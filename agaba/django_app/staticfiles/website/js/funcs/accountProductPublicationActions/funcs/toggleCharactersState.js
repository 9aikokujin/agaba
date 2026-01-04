export function toggleCharactersState() {
  const state = {};

  const updateView = (buttonGroup, activeIndex) => {
    if (!buttonGroup) return;

    const buttons = buttonGroup.querySelectorAll('.toggle__char_btn');
    if (buttons.length === 0) return;
    
    buttons.forEach((button, index) => {
      button.classList.toggle('_active', index === activeIndex);
    });
  };

  const handleButtonClick = (e) => {
    const button = e.target;
    const buttonGroup = button.closest('.seller__product_char_field');
    if (!buttonGroup) return;

    const groupId = buttonGroup.getAttribute('data-product-button');
    if (!groupId) return;

    const buttons = Array.from(buttonGroup.querySelectorAll('.toggle__char_btn'));
    const activeIndex = buttons.indexOf(button);
    if (activeIndex === -1) return;
    
    state[groupId] = activeIndex;

    updateView(buttonGroup, activeIndex);
  };

  const init = () => { 
    const buttonGroups = document.querySelectorAll('.seller__product_char_field');
    if (!buttonGroups.length) return;

    buttonGroups.forEach(buttonGroup => {
      const groupId = buttonGroup.getAttribute('data-product-button');
      if (!groupId) return;

      buttonGroup.addEventListener('click', e => {
        if (e.target.classList.contains('toggle__char_btn')) {
          handleButtonClick(e);
        }
      });

      // Не включать!!! Сия миссия выполняется при рендере шаблона Django
      // updateView(buttonGroup, 0);
    });
  };
  init();
}
