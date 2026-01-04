const state = {
  fields: {},
};

const updateFieldState = (fieldId, hasContent) => {
  state.fields[fieldId] = hasContent;
  updateView(fieldId);
};

const updateView = (fieldId) => {
  const field = document.getElementById(fieldId);
  const parent = field.closest('.modal__form_input_cntr');
  if (state.fields[fieldId]) {
    parent.classList.add('_focus');
  } else {
    parent.classList.remove('_focus');
  }
};

const handleInputChange = (e) => {
  const fieldId = e.target.id;
  const hasContent = e.target.value.length > 0;
  updateFieldState(fieldId, hasContent);
};

export const inputFieldsFocusActions = () => {
  try {
    const inputFields = document.querySelectorAll('.modal__form_value_input._focus_eff');
    inputFields.forEach(field => {
      state.fields[field.id] = field.value.length > 0;
      field.addEventListener('input', handleInputChange);
    });
  } catch (error) {
    console.error('Error initializing input fields focus actions:', error);
  }
};