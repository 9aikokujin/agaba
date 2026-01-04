import { toggleTab } from './funcs/toggleTab.js';
import { selectChooseCharacters } from './funcs/selectChooseCharacters.js';
import { toggleCharactersState } from './funcs/toggleCharactersState.js';
import { additionalOptionActions } from './funcs/additionalOptionActions.js';
import { uploadImageActions } from './funcs/uploadImageActions.js';
import { linkIFrameActions } from './funcs/linkIFrameActions.js';
import { saveProduct } from './funcs/saveProduct.js';

export const accountProductPublicationActions = [
    toggleTab,
    selectChooseCharacters,
    toggleCharactersState,
    additionalOptionActions,
    uploadImageActions,
    linkIFrameActions,
    saveProduct,
];