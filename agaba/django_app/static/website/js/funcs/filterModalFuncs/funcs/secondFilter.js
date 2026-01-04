export function initSecondFilter() {
   // Обработчики для всех чекбоксов
    document.querySelectorAll('.off_checkbox').forEach(function (checkbox) {
        checkbox.addEventListener('change', function () {
            updateURL();
        });
    });

    // мой пиздюк
    let startUrl = window.location.href;
    console.log(startUrl);
    let urlParts = startUrl.split('/');
    let category = urlParts[4]; 
    console.log(category); 
    
    // Обработчики для полей ввода (цена и год)
    document.querySelectorAll('.off-input').forEach(function (input) {
        input.addEventListener('input', function () {
            updateURL();
        });
    });

    function updateURL() {
    const urlParams = new URLSearchParams(window.location.search);

    // Примерная структура для нового фильтра
    let filters = {};

    // Преобразуем параметры в нужный формат
    document.querySelectorAll('.category-checkbox:checked').forEach(function (checkbox) {
        filters['group'] = filters['group'] || [];
        filters['group'].push(parseInt(checkbox.value)); // Преобразуем в число
    });

    document.querySelectorAll('.subcategory-checkbox:checked').forEach(function (checkbox) {
        filters['subgroup'] = filters['subgroup'] || [];
        filters['subgroup'].push(parseInt(checkbox.value)); // Преобразуем в число
    });

    document.querySelectorAll('.condition-checkbox:checked').forEach(function (checkbox) {
        filters['condition'] = filters['condition'] || [];
        filters['condition'].push(checkbox.value);
    });

    document.querySelectorAll('.brand-checkbox:checked').forEach(function (checkbox) {
        filters['brand'] = filters['brand'] || [];
        filters['brand'].push(checkbox.value);
    });

    document.querySelectorAll('.delivery-checkbox:checked').forEach(function (checkbox) {
        filters['delivery_time_days'] = filters['delivery_time_days'] || [];
        filters['delivery_time_days'].push(checkbox.value);
    });
    
    const group = document.querySelectorAll('.group_item').forEach(item => {
        if (item.querySelector('input').checked) {
            item.getAttribute('data-link');
            console.log(item.getAttribute('data-link'));
        }
    });
    

    
    // для цены
    const priceFrom = document.querySelector('.cur_price-from')?.value;
    const priceTo = document.querySelector('.cur_price-to')?.value;

    if (priceFrom || priceTo) {
        filters['cur_price'] = {};  
        if (priceFrom) filters['cur_price']['from'] = Number(parseFloat(priceFrom).toFixed(2)); 
        if (priceTo) filters['cur_price']['to'] = Number(parseFloat(priceTo).toFixed(2));
    }
    console.log(filters);

    // Пример для года
    const yearFrom = document.querySelector('.year-from').value;
    const yearTo = document.querySelector('.year-to').value;
    if (yearFrom || yearTo) {
        filters['prod_year'] = [];
        if (yearFrom) filters['prod_year'].push(yearFrom);
        if (yearTo) filters['prod_year'].push(yearTo);
    }

    // Сериализуем объект в строку JSON
    const filtersString = JSON.stringify(filters);

    // Теперь закодируем его для URL
    const encodedFilters = encodeURIComponent(filtersString);

    
        

        let groupLink = '';
        document.querySelectorAll('.group_item').forEach(item => {
            if (item.querySelector('input').checked) {
                groupLink = item.getAttribute('data-link');
            }
        });

        // Формируем новый URL
        if (groupLink) {
            const newUrl = `${window.location.origin}/catalog/${groupLink}/all/?filters=${encodedFilters}`;
            window.history.replaceState({}, '', newUrl);
        } else {
            console.error('Категория не выбрана');
            const newUrl = `${window.location.origin}/catalog/${category}/all/?filters=${encodedFilters}`;
            window.history.replaceState({}, '', newUrl);
        }
    }
}