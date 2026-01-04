export function saveProduct(event) {

    const handleSaveClick = async () => {

        console.log("Save product clicked");

        const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
        // event.preventDefault();

        // console.log("Save product");

        const href = window.location.href;
        // console.log(href);

        // GET ATTR FIELDS DATA
        // Attr type TEXT
        const textInputs = Array.from(document.querySelectorAll('input[data-id], textarea[data-id]'))
        .reduce((acc, input) => {
            acc[input.dataset.id] = input.value;
            return acc;
        }, {});

        // console.log(textInputs);

        // Attr type RADIO
        const radioInputs = Array.from(document.querySelectorAll('div[data-product-button]'))
        .reduce((acc, div) => {
            const activeButton = div.querySelector('button._active');
            acc[div.dataset.productButton] = [activeButton.dataset.optId, activeButton.textContent];
            return acc;
        }, {});

        // Attr type DROPDOWN
        const dropdownInputs = Array.from(document.querySelectorAll('select[data-id]'))
        .reduce((acc, select) => {
            acc[select.dataset.id] = [select.value, select.options[select.selectedIndex].text];
            return acc;
        }, {});

        // console.log(dropdownInputs);

        const attrInputsData = {textInputs, radioInputs, dropdownInputs};

        // GET IMAGES DATA
        const imageInputsData = Array.from(document.querySelectorAll('div.upload__img_cntr._uploaded'))
            .reduce((acc, div) => {
                const img = div.querySelector('img.upload__file_picture');
                const input = div.closest('li.upload__image_item')?.querySelector('input.upload__file_input');
                
                if (img && input) {
                    const inputId = input.id;
                    const imgSrc = img.src;
                    
                    if (inputId && imgSrc) {
                        acc[inputId] = imgSrc;
                    }
                }
                
                return acc;
            }, {});

        // GET ADDITIONAL OPTIONS DATA
        const additionalOptionsData = Array.from(document.querySelectorAll('div[data-id="additional_option"]'))
        .reduce((acc, div) => {
            const strongTag = div.querySelector('strong');
            const iTag = div.querySelector('i');
            
            if (strongTag && iTag) {
                acc[strongTag.textContent] = iTag.textContent.match(/\d+/g).join('');
            }
            
            return acc;
        }, {});

        // console.log(additionalOptionsData);

        // SAVE PRODUCT
   
        try {
            const response = await fetch(href, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                },
                body: JSON.stringify({ attrInputsData, imageInputsData, additionalOptionsData })
            });

            const data = await response.json();

            if (data.status === 'success') {
                alert('Товар успешно создан.');
                const redirect_href = new URL('account/products/', window.location.origin);
                window.location.href = redirect_href;
                
            } else if (data.status === 'error') {
                alert('Во время создания товара произошла ошибка!');
            }

        } catch (error) {
            console.error('Error:', error);
        }
    }

    const saveButton = document.querySelector('.seller__product_publication_btn');
    console.log(saveButton);
    saveButton.addEventListener('click', () => handleSaveClick());
}