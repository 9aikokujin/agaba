export function changeNumberActions() {
    const modalLists = document.querySelectorAll('.modal__content_list');
    const phoneInput = document.querySelector('.modal__input._change_number');
    const codeBtn = document.querySelector('.modal__btn._code');
    const codeInputs = document.querySelectorAll('.modal__code_input');
    const codeRepeatBtn = document.querySelector('.modal__btn._code_repeat');
    const codeConfirmBtn = document.querySelector('.modal__btn._code_confirm');

    if(!modalLists || !phoneInput || !codeBtn 
                   || !codeInputs || !codeRepeatBtn 
                   || !codeConfirmBtn) return;

    modalLists[0].classList.add('_current');

    const isValidPhone = (phone) => {
        const phoneRegex = /^\+7\d{10}$/;
        return phoneRegex.test(phone.replace(/\s/g, ''));
    };

    codeBtn.addEventListener('click', () => {
        if (isValidPhone(phoneInput.value)) {
            modalLists[0].classList.remove('_current');
            modalLists[1].classList.add('_current');
            codeInputs[0].focus();
        } else {
            alert('Введите корректный номер телефона');
        }
    });

    codeInputs.forEach((input, index) => {
        input.setAttribute('maxlength', '1');
        
        input.addEventListener('input', (e) => {
            if (e.target.value.length > 1) {
                e.target.value = e.target.value.slice(0, 1);
            }
            
            if (e.target.value.length === 1) {
                if (index < codeInputs.length - 1) {
                    codeInputs[index + 1].focus();
                }
            }
        });
    
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Backspace' && !e.target.value && index > 0) {
                codeInputs[index - 1].focus();
            }
        });
    });

    const clearCodeInputs = () => {
        codeInputs.forEach(input => input.value = '');
        codeInputs[0].focus();
    };

    codeRepeatBtn.addEventListener('click', clearCodeInputs);

    codeConfirmBtn.addEventListener('click', () => {
        const isCodeComplete = Array.from(codeInputs).every(input => input.value.length === 1);
        
        if (isCodeComplete) {
            modalLists[1].classList.remove('_current');
            modalLists[2].classList.add('_current');
        } else {
            alert('Пожалуйста, введите код полностью');
        }
    });
};
