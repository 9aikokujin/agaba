export async function switchCodeConfirmationField() {
    const inputElements = document.querySelectorAll('.confirm_input');

    inputElements.forEach((input, index) => {
        input.addEventListener('input', handleInput);
        input.addEventListener('keydown', handleBackspace);

        function handleInput() {
            if (input.value.length === input.maxLength) {
                focusNextInput(index);
            }
        }

        function handleBackspace(event) {
            if (event.key === 'Backspace' && input.value.length === 0) {
                focusPreviousInput(index);
            }
        }
    });

    function focusNextInput(index) {
        const nextInput = inputElements[index + 1];
        if (nextInput) {
            nextInput.focus();
        }
        // else {
        //     inputElements[index].blur();
        // }
    }

    function focusPreviousInput(index) {
        const previousInput = inputElements[index - 1];
        if (previousInput) {
            previousInput.focus();
        }
    }
}
