export async function sliderPrice() {
    const sliderInput = document.getElementById('sliderInputProcent');
    const sliderLabel = document.querySelector('.slider_label-procent');
    const sliderMinElement = document.querySelector('.slider_min');
    const sliderMaxElement = document.querySelector('.slider_max');

    const minDownPaymentPercentage = parseInt(
        document.getElementById('min_down_payment_percentage').textContent.replace(/\D/g, ''), 10);
    
    console.log(minDownPaymentPercentage);

    const initialMinValue = parseInt(sliderMinElement.textContent.replace(/\D/g, ''), 10);
    const maxValue = parseInt(sliderMaxElement.textContent.replace(/\D/g, ''), 10);

    const updateSlider = (value) => {

        if (value < minDownPaymentPercentage) {
            value = minDownPaymentPercentage;
            sliderInput.value = value;
        }

        const percentage = (value / 100) * (maxValue - initialMinValue) + initialMinValue;
        sliderLabel.textContent = `${value}%`;

        const sliderWidth = sliderInput.offsetWidth;
        const thumbWidth = 20;
        const labelWidth = sliderLabel.offsetWidth;
        const offset = ((sliderWidth - thumbWidth) / 100) * value - (labelWidth / 2) + (thumbWidth / 2);
        sliderLabel.style.left = `${offset}px`;

        sliderInput.style.background = `linear-gradient(to right, var(--color000) ${value}%, var(--color001) ${value}%)`;
        sliderMinElement.textContent = `${Math.max(initialMinValue, Math.round(percentage)).toLocaleString('ru-RU', {
            style: 'currency',
            currency: 'RUB',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        })}`;
    };

    sliderMaxElement.textContent = `${
            maxValue.toLocaleString('ru-RU', {
                style: 'currency',
                currency: 'RUB',
                minimumFractionDigits: 0,
                maximumFractionDigits: 0
            })}`;

    sliderInput.addEventListener('input', () => updateSlider(parseInt(sliderInput.value, 10)));
    sliderInput.addEventListener('resize', () => updateSlider(parseInt(sliderInput.value, 10)));

    updateSlider(minDownPaymentPercentage);

}
