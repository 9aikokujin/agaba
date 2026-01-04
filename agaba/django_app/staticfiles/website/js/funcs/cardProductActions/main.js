import { showPricePopover } from './funcs/showPricePopover.js';
import { showMoreCharacters } from './funcs/showMoreCharacters.js';
import { switchPhoto } from './funcs/switchPhoto.js';
import { hiddenNotification } from './funcs/hiddenNotification.js';
import { cutSliderCommentText } from './funcs/cutSliderCommentText.js';
import { toggleTabCardProductDescription } from './funcs/toggleTabCardProductDescription.js';
import { showMoreOptionsCard } from './funcs/showMoreOptionsCard.js'; 
import { incrementPriceCount } from './funcs/incrementPriceCount.js'
// Рабочая
import { comparisonAction } from './funcs/comparison.js';
import { favoriteProductsActions } from './funcs/favorite.js'
// Не нужна
import { comparisonProductsActions__2 } from '../cardProductActions/funcs/comparisonProduct.js';

export const cardProductActions = [
    showPricePopover,
    showMoreCharacters,
    switchPhoto,
    hiddenNotification,
    cutSliderCommentText,
    toggleTabCardProductDescription,
    showMoreOptionsCard,
    incrementPriceCount,
    // 
    // comparisonAction,
    // favoriteProductsActions,
    // 
    comparisonProductsActions__2,
];
