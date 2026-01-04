export function uploadImageActions() {
  // Модель состояния
  const state = {
    images: {},
    maxImages: 20
  };

  // Вспомогательные функции
  function createImageItem(src, alt, originalSrc) {
    const newImageItem = document.createElement('li');
    newImageItem.className = 'upload__image_item _164 _flex_column_center _pos_rel _uploaded';
    newImageItem.innerHTML = `
      <button class="upload__delete_file_btn" type="button">
        <img src="/static/website/img/accPublication/closeSvg.svg" alt="">
      </button>
      <div class="upload__img_cntr _uploaded">
        <img class="upload__file_picture" src="${src}" alt="${alt}" data-original-src="${originalSrc}">
      </div>
    `;
    return newImageItem;
  }

  function addImageItem(picturesList, newImageItem) {
    const uploadFormItem = picturesList.querySelector('.upload__image_item:not(._uploaded)');
    if (uploadFormItem) {
      picturesList.insertBefore(newImageItem, uploadFormItem);
    } else {
      picturesList.appendChild(newImageItem);
    }
  }

  function restoreUploadForm(picturesList) {
    let uploadFormItem = picturesList.querySelector('.upload__image_item:not(._uploaded)');
    if (!uploadFormItem) {
      uploadFormItem = document.createElement('li');
      uploadFormItem.className = 'upload__image_item _164 _flex_column_center _pos_rel _default';
      uploadFormItem.innerHTML = `
        <button class="upload__delete_file_btn" type="button" style="display: none;">
          <img src="/static/website/img/accPublication/closeSvg.svg" alt="">
        </button>
        <div class="upload__img_cntr">
          <img class="upload__file_picture" src="/static/website/img/accPublication/addPictures.png" alt="add picture place">
        </div>
        <label class="upload__file_label" for="uploadFront">
          <input class="upload__file_input" type="file" name="uploadPictures" id="uploadFront" multiple>
        </label>
        <p class="_color_006">Добавить</p>
      `;
      picturesList.appendChild(uploadFormItem);

      const newFileInput = uploadFormItem.querySelector('.upload__file_input');
      newFileInput.addEventListener('change', handleFileUpload);
    }
  }

  // Контроллеры
  function handleFileUpload(event) {
    const fileInput = event.target;
    const files = Array.from(fileInput.files);
    handleFiles(files, fileInput);
  }

  function handleFiles(files, fileInput) {
    const imageItem = fileInput.closest('.upload__image_item');
    const imgContainer = imageItem.querySelector('.upload__img_cntr');
    const defaultImage = imgContainer.querySelector('.upload__file_picture');
    const isMultiple = fileInput.hasAttribute('multiple');

    if (isMultiple) {
      const picturesList = imageItem.closest('[data-pictures-list]');
      const currentImages = picturesList.querySelectorAll('.upload__image_item._uploaded').length;

      files.forEach((file, index) => {
        if (currentImages + index < state.maxImages) {
          const reader = new FileReader();
          reader.onload = function(e) {
            const newImageItem = createImageItem(e.target.result, file.name, defaultImage.dataset.originalSrc);
            const deleteButton = newImageItem.querySelector('.upload__delete_file_btn');
            deleteButton.addEventListener('click', handleDeleteImage);
            addImageItem(picturesList, newImageItem);

            if (currentImages + index + 1 === state.maxImages) {
              const defaultItem = picturesList.querySelector('.upload__image_item._default');
              if (defaultItem) {
                defaultItem.remove();
              }
            }
          };
          reader.readAsDataURL(file);
        }
      });
    } else {
      const file = files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
          if (!defaultImage.dataset.originalSrc) {
            defaultImage.dataset.originalSrc = defaultImage.src;
          }
          defaultImage.src = e.target.result;
          defaultImage.alt = file.name;
          imageItem.querySelector('.upload__delete_file_btn').style.display = 'block';
          imageItem.querySelector('.upload__file_label').style.display = 'none';
          imageItem.querySelector('p').style.display = 'none';
          state.images[fileInput.id] = file;

          imgContainer.classList.add('_uploaded');
          imgContainer.removeEventListener('click', handleImageContainerClick);
        };
        reader.readAsDataURL(file);
      }
    }
  }

  function handleDeleteImage(event) {
    const deleteButton = event.target.closest('.upload__delete_file_btn');
    const imageItem = deleteButton.closest('.upload__image_item');
    const imgContainer = imageItem.querySelector('.upload__img_cntr');
    const defaultImage = imgContainer.querySelector('.upload__file_picture');
    const fileInput = imageItem.querySelector('.upload__file_input');
    const picturesList = imageItem.closest('[data-pictures-list]');

    if (fileInput && !fileInput.hasAttribute('multiple')) {
      defaultImage.src = defaultImage.dataset.originalSrc;
      defaultImage.alt = 'original picture';
      deleteButton.style.display = 'none';
      imageItem.querySelector('.upload__file_label').style.display = 'block';
      imageItem.querySelector('p').style.display = 'block';
      fileInput.value = '';
      delete state.images[fileInput.id];

      imgContainer.classList.remove('_uploaded');
      imgContainer.addEventListener('click', handleImageContainerClick);
    } else {
      imageItem.remove();
    }

    const currentImages = picturesList.querySelectorAll('.upload__image_item._uploaded').length;
    if (currentImages < state.maxImages) {
      restoreUploadForm(picturesList);
    }
  }

  function handleImageContainerClick(event) {
    const imgContainer = event.currentTarget;
    const fileInput = imgContainer.closest('.upload__image_item').querySelector('.upload__file_input');
    fileInput.click();
  }

  function handleDragOver(event) {
    event.preventDefault();
    event.currentTarget.classList.add('drag-over');
  }

  function handleDragLeave(event) {
    event.currentTarget.classList.remove('drag-over');
  }

  function handleDrop(event) {
    event.preventDefault();
    event.currentTarget.classList.remove('drag-over');
    const files = Array.from(event.dataTransfer.files);
    const fileInput = event.currentTarget.closest('.upload__image_item').querySelector('.upload__file_input');
    handleFiles(files, fileInput);
  }

  function preventDragStart(event) {
    event.preventDefault();
  }

  // Инициализация
  function init() {
    const fileInputs = document.querySelectorAll('.upload__file_input');
    const deleteButtons = document.querySelectorAll('.upload__delete_file_btn');
    const imgContainers = document.querySelectorAll('.upload__img_cntr');

    fileInputs.forEach(input => {
      input.addEventListener('change', handleFileUpload);
    });

    deleteButtons.forEach(button => {
      button.addEventListener('click', handleDeleteImage);
      // button.style.display = 'none';
    });

    imgContainers.forEach(container => {
      container.addEventListener('click', handleImageContainerClick);
      container.addEventListener('dragover', handleDragOver);
      container.addEventListener('dragleave', handleDragLeave);
      container.addEventListener('drop', handleDrop);
      container.addEventListener('dragstart', preventDragStart);
    });
  }

  init();
}
