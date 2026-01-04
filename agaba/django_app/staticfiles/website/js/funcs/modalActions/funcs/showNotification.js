export function showNotification() {
  const notificationChars = document.querySelectorAll('.notification__chars');
  const modal = document.querySelector('.modal._notification_modal');
  const modalContents = document.querySelectorAll('.modal__content._notification_content');
  const closeButton = document.querySelectorAll('.modal__close_btn');

  function openModal(index) {
    modalContents.forEach(modalContent => {
      if (modalContent.getAttribute('data-index') === index) {
        modalContent.style.display = 'flex';
        modal.classList.add('_active');
      } else {
        modalContent.style.display = 'none';
      }
    });
  }

  function closeModal() {
    modalContents.forEach(modalContent => {
      setTimeout(() => {
        modalContent.style.display = '';
      }, 300);
    });
    modal.classList.remove('_active');
  }

  notificationChars.forEach(notificationChar => {
    notificationChar.addEventListener('click', (event) => {
      event.preventDefault();
      const index = notificationChar.getAttribute('data-index');
      openModal(index);
    });
  });

  modal.addEventListener('click', (event) => {
    if (!event.target.closest('.modal__content._notification_content')) {
      closeModal();
    }
  });

  closeButton.forEach(button => {
    button.addEventListener('click', (event) => {
      event.preventDefault();
      closeModal();
    });
  });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
      closeModal();
    }
  });
}
