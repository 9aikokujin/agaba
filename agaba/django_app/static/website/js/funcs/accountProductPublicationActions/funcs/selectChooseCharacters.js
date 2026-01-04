export function selectChooseCharacters() {
  const state = {};

  const getElement = (selector) => document.querySelector(selector);

  const closeSelect = (id) => {
    try {
      const container = getElement(`.acc__all_orders_select[data-select-toggle="${id}"]`);
      const button = getElement(`.seller__product_select_btn[data-select-toggle="${id}"]`);
      const list = container.querySelector('.filter_select-list');
      container.style.maxHeight = null;
      list.classList.remove('_show');
      container.classList.remove('_open');
      button.classList.remove('_active');
      state[id].isOpen = false;
    } catch (error) {
      console.error(`Error closing select for id ${id}:`, error);
    }
  };

  const openSelect = (id, button, container, list) => {
    try {
      button.classList.add('_active');
      container.classList.add('_open');
      container.style.maxHeight = '253px';
      setTimeout(() => {
        list.classList.add('_show');
        state[id].isOpen = true;
      }, 200);
    } catch (error) {
      console.error(`Error opening select for id ${id}:`, error);
    }
  };

  const updateInputValue = (containerId) => {
    try {
      const container = getElement(`.acc__all_orders_select[data-select-toggle="${containerId}"]`);
      const input = container.closest('.seller__product_char_field').querySelector('.seller__product_input');
      const selectLabels = Array.from(container.querySelectorAll('.filter_select-checkbox:checked'))
        .map(checkbox => checkbox.nextElementSibling.textContent.trim());

      input.value = selectLabels.join(', ');

      container.querySelectorAll('.filter_select-checkbox').forEach(checkbox => {
        const label = checkbox.nextElementSibling.textContent.trim();
        checkbox.checked = selectLabels.includes(label);
      });
    } catch (error) {
      console.error(`Error updating input value for container ${containerId}:`, error);
    }
  };

  const syncCheckboxesWithInput = (containerId) => {
    try {
      const container = getElement(`.acc__all_orders_select[data-select-toggle="${containerId}"]`);
      const input = container.closest('.seller__product_char_field').querySelector('.seller__product_input');
      const inputValues = input.value.split(',').map(value => value.trim());

      container.querySelectorAll('.filter_select-checkbox').forEach(checkbox => {
        const label = checkbox.nextElementSibling.textContent.trim();
        checkbox.checked = inputValues.includes(label);
      });
    } catch (error) {
      console.error(`Error syncing checkboxes with input for container ${containerId}:`, error);
    }
  };

  const toggleSelect = (e) => {
    const toggleButton = e.target.closest('.seller__product_select_btn');
    if (!toggleButton) return;

    const toggleId = toggleButton.getAttribute('data-select-toggle');
    const selectContainer = getElement(`.acc__all_orders_select[data-select-toggle="${toggleId}"]`);
    if (!selectContainer) return;

    const selectList = selectContainer.querySelector('.filter_select-list');
    if (!selectList) return;

    Object.keys(state).forEach(id => {
      if (state[id].isOpen && id !== toggleId) {
        closeSelect(id);
      }
    });

    if (!state[toggleId]) {
      state[toggleId] = { isOpen: false };
    }

    if (state[toggleId].isOpen) {
      closeSelect(toggleId);
    } else {
      openSelect(toggleId, toggleButton, selectContainer, selectList);
    }
  };

  const closeAllSelects = () => {
    Object.keys(state).forEach(id => {
      if (state[id].isOpen) {
        closeSelect(id);
      }
    });
  };

  document.addEventListener('click', (e) => {
    const isClickInside = e.target.closest('.acc__all_orders_select') || e.target.closest('.seller__product_select_btn') || e.target.closest('.seller__product_input');
    if (!isClickInside) {
      closeAllSelects();
    } else {
      toggleSelect(e);
    }
  });

  document.addEventListener('change', (e) => {
    if (e.target.matches('.filter_select-checkbox')) {
      const container = e.target.closest('.acc__all_orders_select');
      if (container) {
        const containerId = container.getAttribute('data-select-toggle');
        updateInputValue(containerId);
      }
    }
  });

  document.addEventListener('input', (e) => {
    if (e.target.matches('.seller__product_input')) {
      const container = e.target.closest('.seller__product_char_field').querySelector('.acc__all_orders_select');
      if (container) {
        const containerId = container.getAttribute('data-select-toggle');
        syncCheckboxesWithInput(containerId);
      }
    }
  });
}
