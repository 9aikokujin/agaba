import { focusHiddenModalInput } from './funcs/focusHiddenModalInput.js';
import { showModal } from './funcs/showModal.js';
import { showHiddenModalForm } from './funcs/showHiddenModalForm.js';
import { fillFieldsInputData } from './funcs/fillFieldsInputData.js';
import { filterTabActions } from './funcs/filterTabActions.js';
import { showMoreOperations } from './funcs/showMoreOperations.js'; 
import { cutButtonLenghtKek } from './funcs/cutButtonLenghtKek.js';
// filters
//import { sortDateOperations } from './funcs/sortDateOperations.js';

export const accBalanceActions = [
    focusHiddenModalInput,
    showModal,
    showHiddenModalForm,
    fillFieldsInputData,
    // sortDateOperations,
    () => {
        const handleTabChange = showMoreOperations();
        
        filterTabActions(handleTabChange);
    },
    cutButtonLenghtKek
];
