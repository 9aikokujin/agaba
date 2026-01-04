export function showModal() {
    console.log('23425');
    const elements = {
        modal: document.querySelector('.modal'),
        accountList: document.querySelector('.modal__content_list._account_replenishment'),
        withdrawalList: document.querySelector('.modal__content_list._withdrawal_fund'),
        balanceBtn: document.querySelectorAll('.acc_balance_btn'),
        withdrawalBtn: document.querySelector('.withdrawal_btn'),
        closeButtons: document.querySelectorAll('.modal__close_btn'),
        overlay: document.querySelector('.modal__overlay')
    };

    if(!elements.modal || !elements.accountList || !elements.withdrawalList 
                       || !elements.balanceBtn 
                       || !elements.withdrawalBtn) return;

    function switchList(activeList) {
        elements.accountList.classList.remove('_current');
        elements.withdrawalList.classList.remove('_current');
        activeList.classList.add('_current');
    }

    function closeModal() {
        elements.modal.classList.remove('_active');
        elements.accountList.classList.remove('_current');
        elements.withdrawalList.classList.remove('_current');
    }

    function openModal(listToShow) {
        elements.modal.classList.add('_active');
        switchList(listToShow);
    }

    elements.balanceBtn.forEach(btn => {
        btn.addEventListener('click', () => openModal(elements.accountList));
    })

    elements.withdrawalBtn.addEventListener('click', () => openModal(elements.withdrawalList));
    elements.overlay.addEventListener('click', closeModal);
    elements.closeButtons.forEach(btn => btn.addEventListener('click', closeModal));
}
