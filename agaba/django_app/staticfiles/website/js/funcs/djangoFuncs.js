async function fetchMain(event, show_more = false) {
    // Prevent the default action (e.g., navigating to the href)
    event.preventDefault();

    const eventFetch = new CustomEvent('mainFetchComplete');

    // Get the href attribute of the clicked element
    let href = event.currentTarget.getAttribute('href');
    if (!href) {
        href = event.target.parentElement.getAttribute('href');
    }

    if (href.startsWith('?page=')) {
        href = new URL(href, window.location.href);

        const urlParams = new URLSearchParams(window.location.search);
        const filters = urlParams.get('filters');
        console.log(filters);
        if (filters) {
            href.searchParams.append('filters', filters);
        }

    } else {
        href = new URL(href, window.location.origin);
    }

    // document.title = tab_title;
    history.pushState({}, '', href);
    href.searchParams.append('fetch', 'true');
    if (show_more) {
        href.searchParams.append('show_more', 'true');
    }

    try {
        const response = await fetch(href);
        const data = await response.json();

        document.title = data.browser_tab_name;

        if (!show_more) {
            document.getElementById('main_fetch').innerHTML = data.main_content;
            document.dispatchEvent(eventFetch);
        } else {
            document.getElementById('showmore_placeholder').outerHTML = data.main_content;
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

async function processFilter(event, refresh = false) {
    // refresh is option for simple refreshing catalog page without adding new search parameters
    
    // Create a URL object from the current URL
    const url = new URL(window.location.href);
    
    if (!refresh) {

        // get filter property name
        const filter = event.target.getAttribute('data-filter');
    
        // searching all checked checkboxes of this property
        const checkboxes = document.querySelectorAll(`input[data-filter=${filter}]:checked`);
            
        // get values from them
        const values = Array.from(checkboxes).map(checkbox => checkbox.value);
        if (filter === 'in_stock' && checkboxes.length === 0) {
            values.push('False');
        }
    
        // Collect all query parameters into an object
        const queryParams = Object.fromEntries(url.searchParams.entries());
    
        // Initialize the 'filters' object if it doesn't exist
        if (!queryParams.filters) {
            queryParams.filters = {};
        } else {
            // Parse the existing 'filters' string into an object
            queryParams.filters = JSON.parse(queryParams.filters);
        }
    
        // Update the 'filters' object with the new values
        if (values.length > 0) {
            queryParams.filters[filter] = values; // Set the values of the filter
        } else {
            delete queryParams.filters[filter]; // Remove the filter if no values are selected
        }
    
        // Convert the 'filters' object back to a string
        queryParams.filters = JSON.stringify(queryParams.filters);
    
        // Convert the query parameters object back to a query string
        const newQueryString = new URLSearchParams(queryParams).toString();
    
        // Update the URL with the new query string without reloading the page
        url.search = newQueryString;
        // console.log(`${newQueryString}`)

    } else {
        await initCheckboxes();
    }
    
    // Use history.pushState to update the URL without reloading the page
    history.pushState({}, '', url);
    // window.location.href = url;

    url.searchParams.append('fetch', 'true');
    url.searchParams.append('processFilter', 'true');
    try {
        const response = await fetch(url);
        const data = await response.json();

        document.title = data.browser_tab_name;

        filterPlaceholder = document.getElementById('filter_placeholder');

        // Clear previous filter results and placeholders
        while (filterPlaceholder.nextElementSibling) {
            const sibling = filterPlaceholder.nextElementSibling;
            const id = sibling.id;
    
            sibling.remove(); // Remove the next sibling
    
            if (id === "showmore_placeholder") {
                break;
            }
        }

        // Update the page content with new products
        filterPlaceholder.outerHTML = data.main_content;
        
    } catch (error) {
        console.error('Error:', error);
    }
}

// Function to initialize checkboxes based on query parameters
async function initCheckboxes() {
    // Create a URL object from the current URL
    const url = new URL(window.location.href);
    // console.log(url);
    // Get the 'filters' query parameter
    const filtersParam = url.searchParams.get('filters');

    if (filtersParam) {
        // Parse the 'filters' parameter into an object
        const filters = JSON.parse(filtersParam);

        // Iterate over each filter in the 'filters' object
        for (const filter in filters) {
            if (filters.hasOwnProperty(filter)) { // Check if the property is directly on the object
                const values = filters[filter]; // Get the array of values for the current filter

                // Get all checkboxes for the current filter
                const checkboxes = document.querySelectorAll(`input[data-filter=${filter}]`);

                // Iterate over each checkbox and check if it should be checked
                checkboxes.forEach(checkbox => {
                    if (values.includes(checkbox.value)) {
                        checkbox.checked = true;
                    } else {
                        checkbox.checked = false;
                    }
                });
            }
        }
    }
}

function createOrder(event) {
    // Предотвращаем стандартное действие (например, переход по ссылке)
    event.preventDefault();

    // Получаем текущий URL
    let href = window.location.href;

    // Заменяем 'product' на 'create_order' в URL
    href = href.replace('product', 'create_order');

    // Создаем новый URL-объект
    href = new URL(href, window.location.origin);

    // Добавляем параметры запроса
    href.searchParams.append('fetch', 'true');

    // Получаем все выбранные опции
    const selectedOptionsButtons = document.querySelectorAll('button[data-option-id].active');
    const selectedOptions = [];

    // Собираем идентификаторы выбранных опций
    selectedOptionsButtons.forEach(button => {
        const optionId = button.getAttribute('data-option-id');
        selectedOptions.push(optionId);
    });

    // Добавляем выбранные опции в параметры запроса
    href.searchParams.append('selected_options', selectedOptions.join(','));

    // Переходим на новую страницу
    window.location.href = href;
}

// async function createOrderStep2(event) {

//     event.preventDefault();

//     let href = window.location.href;
//     href = href.replace('product', 'create_order_step_2');
//     href = new URL(href);

//     const eventFetch = new CustomEvent('mainFetchComplete');

//     href.searchParams.append('fetch', 'true');

//     href.searchParams.append('selected_options', window.selectedOptions);

//     const downPaymentPercent = document.getElementById('sliderInputProcent').value;
//     href.searchParams.append('down_payment_percent', downPaymentPercent);

//     const user_name = document.getElementById('user_name').value;
//     const inn_org_number = document.getElementById('inn_org_number').value;
//     const email = document.getElementById('email').value;
//     const personalDataInp = document.getElementById('personalDataInp').checked;

//     if (!personalDataInp) {
//         alert('Вы должны согласиться на обработку персональных данных!');
//         return;
//     }

//     const formData = {
//         user_name: user_name,
//         inn_org_number: inn_org_number,
//         email: email,
//         personalDataInp: personalDataInp
//     };

//     const formDataString = JSON.stringify(formData);

//     href.searchParams.append('form_data', formDataString);

//     href.searchParams.append('active_tab_id', window.orderTabValue);

//     try {
//         const response = await fetch(href);
//         const data = await response.json();

//         if (data.status === 'success') {
//             let redirect_href = new URL(`account/order/${data.order_number}`, window.location.origin);
//             window.location.href = redirect_href;
//         } else if (data.status === 'failed') {
//             location.reload();
//         }


//     } catch (error) {
//         console.error('Error:', error);
//     }

// }

