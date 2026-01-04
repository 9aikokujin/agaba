const parseRussianDate = (dateString) => {
    const monthsRu = {
        'января': 0, 'февраля': 1, 'марта': 2, 'апреля': 3,
        'мая': 4, 'июня': 5, 'июля': 6, 'августа': 7,
        'сентября': 8, 'октября': 9, 'ноября': 10, 'декабря': 11
    };

    const [datePart, timePart] = dateString.split(', ');
    const [day, month] = datePart.split(' ');
    const [hours, minutes] = timePart.split(':');

    return new Date(
        new Date().getFullYear(),
        monthsRu[month],
        parseInt(day),
        parseInt(hours),
        parseInt(minutes)
    );
};

const getDateFromOperation = (operation) => {
    const dateElement = operation.querySelectorAll('._operation_time');
    return dateElement ? parseRussianDate(dateElement.textContent) : new Date(0);
};

const getSortedOperations = (operations, sortDirection) => {
    if (!sortDirection) {
        return [...operations].sort((a, b) => 
            Number(a.dataset.originalIndex) - Number(b.dataset.originalIndex)
        );
    }

    return [...operations].sort((a, b) => {
        const dateA = getDateFromOperation(a).getTime();
        const dateB = getDateFromOperation(b).getTime();
        return sortDirection === 'desc' ? dateB - dateA : dateA - dateB;
    });
};

const getNextSortDirection = (current) => {
    const states = { null: 'desc', 'desc': 'asc', 'asc': null };
    return states[current];
};

export const sortDateOperations = () => {
    let sortDirection = null;
    const operationsList = document.querySelector('.operation__body_list');
    const dateButton = document.querySelector('.operation__header_item_btn._date');
    
    dateButton.addEventListener('click', () => {
        sortDirection = getNextSortDirection(sortDirection);
        const operations = Array.from(operationsList.children);
        const sortedOperations = getSortedOperations(operations, sortDirection);
        
        sortedOperations.forEach(operation => operationsList.append(operation));
    });
};

export const initializeOperations = () => {
    const operations = document.querySelectorAll('.operation_body_item');
    operations.forEach((operation, index) => {
        operation.dataset.originalIndex = index;
    });
};
