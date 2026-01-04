export function fillFieldsInputData() {
    const modalLists = document.querySelectorAll('.modal__content_list._modal_balance_list');

    if (!modalLists) return;

    // // modalLists.forEach(modalList => {
    // //     const companyItems = modalList.querySelectorAll('.balance_company_data');

    //     companyItems.forEach(item => {
    //         item.addEventListener('click', () => {
    //             const companyName = item.querySelector('.company_name').textContent;
    //             const innValue = item.querySelector('._inn_value').textContent;
    //             const kppValue = item.querySelector('._kpp_value').textContent;

    //             const nameInput = modalList.querySelector('.modal__form_value_input._main_input');
    //             const innInput = modalList.querySelector('.modal__form_value_input._inn');
    //             const kppInput = modalList.querySelector('.modal__form_value_input._kpp');

    //             nameInput.value = companyName;
    //             innInput.value = innValue;
    //             kppInput.value = kppValue;

    //             [nameInput, innInput, kppInput].forEach(input => {
    //                 input.dispatchEvent(new Event('input', { bubbles: true }));
    //             });
    //         });
    //     });
    // });
}
