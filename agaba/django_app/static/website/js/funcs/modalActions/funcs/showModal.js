export function showModal() {
    const cangeConfButton = document.querySelector('.change_conf_inf_btn._modal');
    const modal = document.querySelector('.modal');

    if (!cangeConfButton || !modal) return;

    cangeConfButton.addEventListener('click', (e) => {
        e.preventDefault();
        modal.classList.add('_active');
    });

    const closeButtons = document.querySelectorAll('.modal__close_btn, .modal__close_btn_2');
    const modalOverlay = document.querySelector('.modal__overlay');

    const closeModal = () => {
        modal.classList.remove('_active');
    };

    closeButtons.forEach(btn => {
        btn.addEventListener('click', closeModal);
    });

    modalOverlay.addEventListener('click', closeModal);
}