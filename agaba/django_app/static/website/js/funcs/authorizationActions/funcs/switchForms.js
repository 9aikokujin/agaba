export async function switchForms() {
    const switchButtonElement = document.querySelectorAll('.switch_form-btn');
    const buyerFormElement = document.querySelector('.autorization_form.buyer');
    const sellerFormElement = document.querySelector('.autorization_form.seller');
    const confirmFormElement = document.querySelector('.confirm_form');
    const autorizationButtonElements = document.querySelectorAll('.autorization_btn');
    const authBackButtonElement = document.querySelector('.auth_back-btn');
    const allAutorizationFormsElements = document.querySelectorAll('.autorization_form');

    const formHistory = [];

    const toggleForms = (formToShow, formToHide) => {
        formToHide.classList.remove('_show');
        formToShow.classList.add('_show');
    };

    buyerFormElement.classList.add('_show');

    switchButtonElement.forEach(button => {
        button.addEventListener('click', () => {
            const [formToShow, formToHide] = buyerFormElement.classList.contains('_show')
                ? [sellerFormElement, buyerFormElement]
                : [buyerFormElement, sellerFormElement];
            toggleForms(formToShow, formToHide);
        });
    });

    autorizationButtonElements.forEach(button => {
        button.addEventListener('click', () => {
            const currentForm = document.querySelector('.auth_form._show');
            formHistory.push(currentForm);

            if (!validateAuthorizationForm(currentForm)) {
                return;
            }

            allAutorizationFormsElements.forEach(form => form.classList.remove('_show'));
            confirmFormElement.classList.add('_show');
        });
    });

    authBackButtonElement.addEventListener('click', () => {
        if (formHistory.length > 0) {
            const currentForm = document.querySelector('.auth_form._show');
            currentForm.classList.remove('_show');

            const previousForm = formHistory.pop();
            previousForm.classList.add('_show');
        }
    });

    // add validation for form buyer
    function validateAuthorizationForm(currentForm) {

        window.formValid = false;

        if (currentForm.id === 'sellerForm') {
            var sellerCompanyName = document.getElementById('sellerCompanyName').value;
            if (!sellerCompanyName) {
                alert('Пожалуйста, введите название компании.');
                return;
            }

            var sellerINN = document.getElementById('sellerINN').value;
            if (sellerINN.length !== 10) {
                alert('Пожалуйста, введите ИНН содержащий 10 цифр.');
                return;
            }

        } 
        
        if (currentForm.id === 'buyerForm') {
            var mobileNumber = document.getElementById('buyerMobileNumber').value;
            var agreeCheckbox = document.getElementById('buyerPersonalDataInp').checked;
        } else if (currentForm.id === 'sellerForm'){
            var mobileNumber = document.getElementById('sellerMobileNumber').value;
            var agreeCheckbox = document.getElementById('sellerPersonalDataInp').checked;
        }

        // Validate mobile number (simple example: check if it starts with +7 and has at least 11 digits)
        if (!mobileNumber.startsWith('+7') || mobileNumber.length !== 12) {
            alert('Пожалуйста, введите корректный номер телефона, начинающийся с +7 и содержащий 11 цифр.');
            return;
        }

        // Validate checkbox
        if (!agreeCheckbox) {
            alert('Пожалуйста, согласитесь на обработку персональных данных.');
            return;
        }

        window.formValid = true;
        return true;

    }
}

