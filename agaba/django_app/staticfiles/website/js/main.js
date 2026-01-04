import { toggleLangSelect } from "./funcs/toggleLangSelect.js";
import { cutDescriptionCatalogText } from "./funcs/cutDescriptionCatalogText.js";
// import { findNumRadioStar } from './funcs/findNumRadioStar.js';
import { itemsSelectHoverShow } from "./funcs/itemsSelectHoverShow.js";
import { toggleSelectCatalog } from "./funcs/toggleSelectCatalog.js";
import { filterModalFuncs } from "./funcs/filterModalFuncs/main.js";
import { commentSellerFuncs } from "./funcs/commentSeller/main.js";
import { cardProductActions } from "./funcs/cardProductActions/main.js";
import { authorizationActions } from "./funcs/authorizationActions/main.js";
import { productReviewQuestions } from "./funcs/productReviewQuestions/main.js";
import { orderFuncs } from "./funcs/orderFuncs/main.js";
import { headerActions } from "./funcs/headerActions/main.js";
import { mobileMenuActions } from "./funcs/mobileMenuActions/main.js";
import { orderCashlessPageActions } from "./funcs/orderCashlessPageActions/main.js";
import { accountOrderDeliveryActions } from "./funcs/accountOrderDeliveryActions/main.js";
// Для чата
import { accountMessageActions } from "./funcs/accountMessageActions/main.js";
import { accountItemMessageActions } from "./funcs/accountItemMessageActions/main.js";

import { modalActions } from "./funcs/modalActions/main.js";
import { accBalanceActions } from "./funcs/accBalanceActions/main.js";
import { accReviewQuestionActions } from './funcs/accReviewQuestionActions/main.js';
import { accountProductPublicationActions } from './funcs/accountProductPublicationActions/main.js';
// import { favoriteProductsActions } from './funcs/cardProductActions/funcs/favorite.js';	
import { showModal } from './funcs/accBalanceActions/funcs/showModal.js';
// 
// import { comparisonAction } from "./funcs/cardProductActions/funcs/comparison.js";

document.addEventListener("DOMContentLoaded", async () => {

	// if (document.getElementById("nujnaya-btn")) {
	// 	await comparisonAction();
	// }
	
	if (document.getElementById("show-modal-btn")) {
		await showModal();
	}
	
	// if (document.getElementById("for_fav-btn")) {
	// 	await favoriteProductsActions();
	// }
	
	if (document.querySelector(".filter__item.select .filter_feature-btn")) {
		await toggleSelectCatalog();
	}

	if (
		document.querySelector(".filter_feature-btn.filters") &&
		document.querySelector(".filters_sidebar")
	) {
		for (const func of filterModalFuncs) {
			await func();
		}
	}

	if (document.querySelector(".card_product-card")) {
		for (const func of cardProductActions) {
			await func();
		}
	}

	if (document.querySelector(".header")) {
		if (document.querySelector(".header")) {
			for (const func of headerActions) {
				await func();
			}
		}
	}

	if (document.querySelector(".lang_select")) {
		await toggleLangSelect();
	}

	if (document.querySelector(".catalog_item .catalog_description")) {
		await cutDescriptionCatalogText();
	}

	// if (document.querySelector(".catalog_section.main .catalog_item .catalog_rating")) {
	//     await findNumRadioStar();
	// }

	if (document.querySelector(".car_nav-link.select")) {
		await itemsSelectHoverShow();
	}

	// if (document.querySelector(".filter__item.select .filter_feature-btn")) {
	//     await toggleSelectCatalog();
	// }

	if (document.querySelector(".seller_comment-section")) {
		for (const func of commentSellerFuncs) {
			await func();
		}
	}

	// if (document.querySelector(".header")) {
	// 	for (const func of headerActions) {
	// 		await func();
	// 		console.log("Привет гребаный django");
	// 	}
	// }

	// if (document.querySelector(".seller_comment-section")) {
	// 	for (const func of commentSellerFuncs) {
	// 		await func();
	// 		if (document.querySelector(".header")) {
	// 			for (const func of headerActions) {
	// 				await func();
	// 				console.log('Привет гребаный django');
	// 			}
	// 		}
	// 	}
	// }

	// if (document.querySelector(".card_product-card")) {
	//     for (const func of cardProductActions) {
	//         await func();
	//     }
	// }

	if (document.querySelector(".autorization_sect")) {
		for (const func of authorizationActions) {
			await func();
		}
	}

	if (document.querySelector(".seller_comment-section.RMP")) {
		for (const func of productReviewQuestions) {
			await func();
		}
	}

	if (document.querySelector(".order_form")) {
		for (const func of orderFuncs) {
			await func();
		}
	}

	if (document.querySelector(".mobile__menu")) {
		for (const func of mobileMenuActions) {
			await func();
		}
	}

	if (document.querySelector(".order_cashless-page")) {
		for (const func of orderCashlessPageActions) {
			func();
		}
	}

	if (document.querySelector(".acc_main-cntr._acc_order_delivery")) {
		for (const func of accountOrderDeliveryActions) {
			func();
		}
	}

	if (document.querySelector(".account_sect._messages_sect")) {
		for (const func of accountMessageActions) {
			func();
		}
	}

	if (document.querySelector(".account_sect._item_messages_sect")) {
		for (const func of accountItemMessageActions) {
			func();
		}
	}

	if (
		document.querySelector(".account_sect._acc-profile") ||
		document.querySelector(".acc_main-cntr._notification_sect")
	) {
		for (const func of modalActions) {
			func();
		}
	}

	if (document.querySelector(".account_sect._acc-balance")) {
		for (const func of accBalanceActions) {
			func();
		}
	}

	// Call the function to initialize checkboxes when the DOM content is fully loaded
    if (document.querySelector(".catalog_filters-cntr")) {
		await initCheckboxes();
    }

    if (document.querySelector(".account_sect._acc__RMP_section")) {
			for (const func of accReviewQuestionActions) {
				await func();
			}
    }

	if (document.querySelector(".seller__product_sect")) {
		for (const func of accountProductPublicationActions) {
			func();
		}
	}
	
});


// Proceed go back/forward in browser history
window.addEventListener('popstate', function() {
    window.location.reload();
});