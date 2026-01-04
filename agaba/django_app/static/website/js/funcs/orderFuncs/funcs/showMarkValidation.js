export async function showMarkValidation() {
    const inputs = document.querySelectorAll('.order_input[required]');

    inputs.forEach(input => {
        input.addEventListener('input', () => {
            const mark = input.closest('._mark');

            if (input.classList.contains('tel')) {
                formatPhoneNumber(input);
            }

            if (isValidInput(input)) {
                mark.style.setProperty('--visibility', 'visible');
                mark.style.setProperty('--opacity', '1');
                mark.style.setProperty('--transform', 'translate(0, -50%)');
            } else {
                mark.style.setProperty('--visibility', 'hidden');
                mark.style.setProperty('--opacity', '0');
                mark.style.setProperty('--transform', 'translate(100px, -50%)');
            }
        });
    });
}

function formatPhoneNumber(input) {
    let value = input.value.replace(/\D/g, '');
    if (value.startsWith('7')) {
        value = '+' + value;
    }
    input.value = value.replace(/(\d{1})(\d{3})(\d{3})(\d{2})(\d{2})/, '$1 $2 $3 $4 $5');
}

function isValidInput(input) {
    if (input.classList.contains('name')) {
        return input.value.trim().length >= 1;
    } else if (input.classList.contains('tel')) {
        return /^\+7 \d{3} \d{3} \d{2} \d{2}$/.test(input.value);
    } else if (input.classList.contains('email')) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(input.value);
    }
    return false;
}
