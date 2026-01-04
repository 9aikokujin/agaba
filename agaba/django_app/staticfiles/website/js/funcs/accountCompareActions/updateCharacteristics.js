// Модель (Model)
const createModel = () => {
  let state = {
    wrappers: []
  };

  const initializeWrappers = (wrappers) => {
    state.wrappers = Array.from(wrappers);
  };

  const getState = () => state;

  return {
    initializeWrappers,
    getState
  };
};

// Представление (View)
const createView = (model) => {
  const render = () => {
    model.getState().wrappers.forEach(wrapper => {
      const characteristics = wrapper.querySelectorAll('.__characteristic');
      characteristics.forEach(characteristic => {
        if (!characteristic.textContent.trim()) {
          characteristic.textContent = '—';
        }
      });
    });
  };

  return {
    render
  };
};

// Контроллер
const setupController = (model, view) => {
  try {
    view.render();
  } catch (error) {
    console.error('Error rendering characteristics:', error);
  }
};

export function updateCharacteristics() {
  const wrappers = document.querySelectorAll('.compare__characters_wrp');

  const model = createModel();
  model.initializeWrappers(wrappers);

  const view = createView(model);

  setupController(model, view);
}
