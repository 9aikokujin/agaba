const state = {
  isFileUploaded: false,
  uploadedFileSrc: '',
};

const uploadFile = (file) => {
  try {
    if (file && isValidFileType(file)) {
      const reader = new FileReader();
      reader.onload = (e) => {
        state.isFileUploaded = true;
        state.uploadedFileSrc = e.target.result;
        updateView();
      };
      reader.readAsDataURL(file);
    }
  } catch (e) {
    throw new Error(e);
  }
};

const deleteFile = () => {
  state.isFileUploaded = false;
  state.uploadedFileSrc = '';
  updateView();
};

const isValidFileType = (file) => {
  const validTypes = ['image/jpeg', 'image/jpg', 'image/png'];
  return validTypes.includes(file.type);
};

const updateView = () => {
  const fileLabel = document.querySelector('.file__label');
  const imgElement = fileLabel.querySelector('img');
  const deleteButton = document.querySelector('.delete__uploaded_screenshot');

  if (state.isFileUploaded) {
    fileLabel.setAttribute('upload-status', 'isUploaded');
    fileLabel.classList.add('_uploaded');
    imgElement.src = state.uploadedFileSrc;
    deleteButton.style.display = 'block';
  } else {
    fileLabel.setAttribute('upload-status', 'isEmpty');
    fileLabel.classList.remove('_uploaded');
    imgElement.src = '';
    deleteButton.style.display = 'none';
  }
};

const handleFileInputChange = (e) => {
  const fileLabel = document.querySelector('.file__label');

  if (fileLabel.classList.contains('_uploaded') && fileLabel.getAttribute('upload-status') === 'isUploaded') return;

  const file = e.target.files[0];
  uploadFile(file);
};

const handleDeleteButtonClick = () => {
  deleteFile();
};

export const uploadScreenshotActions = () => {
  const fileInput = document.querySelector('.file__input');
  const deleteButton = document.querySelector('.delete__uploaded_screenshot');
  deleteButton.style.display = 'none';

  fileInput.addEventListener('change', handleFileInputChange);
  deleteButton.addEventListener('click', handleDeleteButtonClick);
};
