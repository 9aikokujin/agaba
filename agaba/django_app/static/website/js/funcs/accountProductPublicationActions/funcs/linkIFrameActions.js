// Модель состояния
const state = {
  link: '',
  isLinkValid: false
};

// Представление
const view = {
  init() {
    this.cacheDOM();
    this.removeInitialElements();
  },
  cacheDOM() {
    this.productItem = document.querySelector('.seller__product_item[data-link-handler]');
    if (!this.productItem) {
      console.error('Element with data-link-handler not found');
      return;
    }
    this.input = this.productItem.querySelector('.seller__product_input');
    this.selectBtn = this.productItem.querySelector('.seller__product_select_btn');
    this.deleteLinkBtn = this.productItem.querySelector('.seller__product_delete_link');
    this.uploadedLinkCntr = this.productItem.querySelector('.uploaded__link_cntr');
    this.previewLink = this.productItem.querySelector('.uploaded__preview_link');
    this.charField = this.productItem.querySelector('.seller__product_char_field');
    this.charName = this.productItem.querySelector('.seller__product_char_name');
  },
  removeInitialElements() {
    this.deleteLinkBtn?.remove();
    this.uploadedLinkCntr?.remove();
  },
  update() {
    state.isLinkValid ? this.showValidLink() : this.showErrorMessage();
  },
  showValidLink() {
    if (!this.charField || !this.uploadedLinkCntr || !this.previewLink || !this.charName) return;
    this.charField.remove();
    this.productItem.appendChild(this.uploadedLinkCntr);
    this.previewLink.href = state.link;
    this.previewLink.setAttribute('target', '_blank');
    this.charName.appendChild(this.deleteLinkBtn);
  },
  showErrorMessage() {
    if (!this.charField) return;
    if (!this.charField.querySelector('p.error__message')) {
      const errorMessage = document.createElement('p');
      errorMessage.style.color = 'red';
      errorMessage.classList.add('error__message');
      errorMessage.textContent = 'некорректная ссылка';
      this.charField.appendChild(errorMessage);
      setTimeout(() => errorMessage.remove(), 2000);
    }
    this.deleteLinkBtn?.remove();
  }
};

// Контроллер
const controller = {
  init() {
    view.init();
    this.bindEvents();
  },
  bindEvents() {
    view.selectBtn?.addEventListener('click', this.handleSelectBtnClick.bind(this));
    view.deleteLinkBtn?.addEventListener('click', this.handleDeleteLinkClick.bind(this));
  },
  handleSelectBtnClick() {
    const link = view.input?.value || '';
    state.isLinkValid = this.isValidLink(link);
    if (state.isLinkValid) {
      state.link = link;
    }
    view.update();
  },
  handleDeleteLinkClick() {
    state.link = '';
    state.isLinkValid = false;
    view.uploadedLinkCntr?.remove();
    view.deleteLinkBtn?.remove();
    view.charField && view.productItem.appendChild(view.charField);
  },
  isValidLink(link) {
    const validLinkPattern = /^(https?:\/\/)?(www\.)?(rutube\.ru|vk\.com|dzen\.ru)\/.+$/;
    return validLinkPattern.test(link);
  }
};

// Инициализация
export function linkIFrameActions() {
  controller.init();
}
