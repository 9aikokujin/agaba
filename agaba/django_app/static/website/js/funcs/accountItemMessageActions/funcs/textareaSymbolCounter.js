export function textareaSymbolCounter () {
    const textareaField = document.querySelector('.MP__footer_textarea textarea');
    const symbolCounter = document.querySelector('.MP_footer_counter');
    const maxSymbolLength = 1000;

    if(!textareaField || !symbolCounter) return;

    textareaField.addEventListener('input', function() {
        const currentLength = this.value.length;

        if(currentLength > maxSymbolLength) {
            this.value = this.value.slice(0, maxSymbolLength);
        }

        symbolCounter.textContent = `${this.value.length} / ${maxSymbolLength} символов`;
    })
}