document.addEventListener("DOMContentLoaded", function () {
  // Находим контейнер с вкладками
  const tabs = document.getElementById("comment_tabs");

  // Находим все кнопки с классом RMP-tab_btn
  const tabButtons = tabs.querySelectorAll(".RMP-tab_btn");

  // Находим все контентные блоки
  const tabContents = tabs.querySelectorAll(".RMP_comment-question_block");
  console.log(tabContents);
  // Добавляем обработчик события для каждой кнопки
  tabButtons.forEach((button) => {
    button.addEventListener("click", function () {
      // Удаляем класс active со всех кнопок
      tabButtons.forEach((btn) => btn.classList.remove("active"));

      // Добавляем класс active к текущей кнопке
      this.classList.add("active");

      // Получаем значение атрибута data-tab текущей кнопки
      const tabId = this.getAttribute("data-tab");

      // Скрываем все контентные блоки
      tabContents.forEach((content) => content.classList.remove("_active"));

      // Показываем контентный блок, соответствующий выбранной вкладке
      const selectedContent = tabs.querySelector(
        `.RMP_comment-question_block[data-tab="${tabId}"]`,
      );
      if (selectedContent) {
        selectedContent.classList.add("_active");
      }
    });
  });
});

const state = {
  isModalShown: false,
};

const toggleModal = (shouldShow) => {
  state.isModalShown = shouldShow;

  updateView();
};

const showModal = () => toggleModal(true);

const hideModal = () => toggleModal(false);

const updateView = () => {
  const modal = document.querySelector(".modal");

  const modalContentList = document.querySelector(".modal__content_list");

  const modalContent = document.querySelector(".modal__add_new_comment");

  if (state.isModalShown) {
    modal.classList.add("_active");

    modalContentList.classList.add("_current");

    modalContent.setAttribute("data-modal", "isShown");
  } else {
    modal.classList.remove("_active");

    modalContentList.classList.remove("_current");

    modalContent.setAttribute("data-modal", "isHidden");
  }
};

const handleAccountReviewItemClick = (e) => {
  e.stopPropagation();

  const clickedItem = e.currentTarget;

  // Получаем название и другие данные продукта
  const productNameElement = clickedItem.querySelector(".account__review_item_name h4");
  const productName = productNameElement?.innerText.trim();

  const productImage = clickedItem.querySelector(".account__review_item_img img")?.src;

  // Получаем ID продукта из data-id
  const productId = productNameElement?.dataset.id; // Убедитесь, что элемент имеет атрибут data-id
  console.log("productId:", productId);

  if (!productId) {
      console.error("ID продукта не найден!");
      return;
  }

  // Обновляем информацию о продукте в модальном окне
  const modalProductName = document.querySelector(".modal__content .account__review_item_name h4");
  if (modalProductName) modalProductName.innerText = productName;

  const modalProductImage = document.querySelector(".modal__content .account__review_item_img img");
  if (modalProductImage) modalProductImage.src = productImage;

  // Находим скрытое поле product_id и устанавливаем его значение
  const productInput = document.querySelector('input[name="product_id"]');
  if (productInput) {
      productInput.value = productId; // Устанавливаем значение скрытого поля
      console.log("Скрытое поле product_id обновлено:", productInput.value);
  } else {
      console.error("Скрытое поле product_id не найдено!");
  }

  showModal();
};

const handleDocumentClick = (e) => {
  const modalContent = document.querySelector(".modal__add_new_comment");

  if (state.isModalShown) {
    // const clickedItem = e.currentTarget;
    // return null
  }

  if (!modalContent.contains(e.target) || e.target.closest(".modal__close_btn")) {
    // hideModal();
  }
    
};

const handleKeyDown = (e) => {
  if (e.key === "Escape") hideModal();
};

export const modalActions = () => {
  const reviewItems = document.querySelectorAll(
    '.account__review_item[data-modal="modal__add_new_comment"]',
  );

  reviewItems.forEach((item) =>
    item.addEventListener("click", handleAccountReviewItemClick),
  );

  document.addEventListener("click", handleDocumentClick);

  document.addEventListener("keydown", handleKeyDown);
};

function getCSRFToken() {
  const cookieValue = document.cookie
    .split("; ")
    .find((row) => row.startsWith("csrftoken="))
    ?.split("=")[1];
  return cookieValue || null;
}

export function removeFromComparison(productId) {
  fetch(`/account/remove_from_comparison/${productId}/`, {
    method: "DELETE",
    headers: {
      "X-CSRFToken": getCSRFToken(), // CSRF токен для Django
      "Content-Type": "application/json",
    },
    body: JSON.stringify({}),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.status === "success") {
        alert("Товар удален из сравнения!");
      }
    })
    .catch((error) => console.error("Ошибка:", error));
}

document.addEventListener("DOMContentLoaded", function () {
  const groupButtons = document.querySelectorAll(".order__tab_btn");
  const products = document.querySelectorAll(".catalog_item._compare__item");
  const characteristicsList = document.querySelector(".characters__list");
  const productsContainer = document.querySelector(
    ".acc__order_delivery ._compare__list",
  );

  function filterProducts(selectedGroup) {
    console.log("Выбрана группа:", selectedGroup);

    // Скрываем все товары
    products.forEach((product) => {
      product.style.display = "none";
    });

    // Показываем только товары выбранной группы
    const selectedProducts = Array.from(products).filter(
      (product) => product.getAttribute("data-group") === selectedGroup,
    );
    selectedProducts.forEach((product) => {
      product.style.display = "block";
    });

    updateCharacteristics(selectedProducts);
  }

  function updateCharacteristics(selectedProducts) {
    console.log("Обновление характеристик...");

    if (selectedProducts.length === 0) {
      characteristicsList.innerHTML =
        '<li class="characters__item"><h4>Параметры</h4></li>';
      return;
    }

    // Собираем все характеристики из всех товаров
    let allCharacteristics = new Set();
    selectedProducts.forEach((product) => {
      const charData = product.getAttribute("data-characteristics");
      if (charData) {
        try {
          const characteristics = JSON.parse(charData);
          characteristics.forEach((char) => allCharacteristics.add(char.name));
        } catch (error) {
          console.error("Ошибка парсинга характеристик:", error);
        }
      }
    });

    // Формируем список характеристик
    let characteristicsHTML =
      '<li class="characters__item"><h4>Параметры</h4></li>';
    allCharacteristics.forEach((charName) => {
      characteristicsHTML += `<li class="characters__item"><strong>${charName}</strong></li>`;
    });
    characteristicsList.innerHTML = characteristicsHTML;

    // Обновляем значения характеристик под каждым товаром
    selectedProducts.forEach((product) => {
      const productCharContainer = product.querySelector(
        ".product_characteristics",
      );
      productCharContainer.innerHTML = "";

      const charData = product.getAttribute("data-characteristics");
      if (charData) {
        try {
          const characteristics = JSON.parse(charData);
          allCharacteristics.forEach((charName) => {
            const char = characteristics.find((c) => c.name === charName);
            productCharContainer.innerHTML += `<li>${char ? char.value : "-"}</li>`;
          });
        } catch (error) {
          console.error("Ошибка обработки характеристик товара:", error);
        }
      }
    });
  }

  // Обработчик клика по кнопкам групп
  groupButtons.forEach((button) => {
    button.addEventListener("click", function () {
      const selectedGroup = this.getAttribute("data-group");

      groupButtons.forEach((btn) => btn.classList.remove("active"));
      this.classList.add("active");

      filterProducts(selectedGroup);
    });
  });

  // По умолчанию выбираем первую группу
  if (groupButtons.length > 0) {
    const firstGroupButton = groupButtons[0];
    const firstGroup = firstGroupButton.getAttribute("data-group");

    firstGroupButton.classList.add("active"); // Добавляем класс active первой кнопке
    filterProducts(firstGroup); // Показываем товары первой группы
  }
});

document.addEventListener("DOMContentLoaded", function () {
  try {
    const button = document.getElementById("chto-nibudi");
    if (!button) {
      throw new Error("Элемент с ID 'chto-nibudi' не найден.");
    }

    button.addEventListener("click", function () {
      const productId = button.getAttribute("data-product-id");
      console.log("Product ID:", productId);
      removeFromComparison(productId); // Вызов функции удаления
    });
  } catch (error) {
    console.error("Произошла ошибка:", error.message);
  }
});
