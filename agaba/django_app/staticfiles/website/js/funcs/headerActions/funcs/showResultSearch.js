const model = (() => {
  const asyncSearchResult = async (productName) => {
    if (!productName) {
      // console.log("Пустой запрос: поиск не выполняется.");
      return;
    }

    try {
      console.log(`Выполняется запрос к серверу для поиска: "${productName}"`);
      const response = await fetch(`/search/?q=${encodeURIComponent(productName)}`);
      if (!response.ok) throw new Error(`Ошибка HTTP: ${response.status}`);
      const html = await response.text();
      // console.log(`Получен ответ от сервера для запроса: "${productName}"`);
      return html;
    } catch (error) {
      console.error("Ошибка при выполнении запроса:", error);
      return [];
    }
  };

  return { asyncSearchResult };
})();

const view = (() => {
  const searchInput = document.querySelector(".header_search");
  const searchContainer = document.querySelector(".search__result-container");

  const getSearchWrap = () => {
    const searchWrap = document.querySelector(".search__result-wrap");
    if (!searchWrap) {
      console.warn("Элемент .search__result-wrap не найден в DOM.");
    } else {
      // console.log("Элемент .search__result-wrap успешно найден в DOM.");
    }
    return searchWrap;
  };

  const clearResult = () => {
    if (searchContainer) {
      // console.log("Очищаем результаты поиска.");
      searchContainer.innerHTML = "";
    }
  };

  const updateResult = (html) => {
    if (searchContainer) {
      // console.log("Обновляем результаты поиска в контейнере.");
      searchContainer.innerHTML = html;
    }
  };

  const updateContainerHeight = () => {
    const searchWrap = getSearchWrap();
    if (!searchContainer || !searchWrap) {
      console.warn("Не удалось обновить высоту контейнера: элементы не найдены.");
      return;
    }

    // console.log("Сбрасываем maxHeight перед расчетом новой высоты.");
    searchContainer.style.maxHeight = "0px";

    setTimeout(() => {
      const { paddingTop, paddingBottom } = window.getComputedStyle(searchContainer);
      const totalHeight = searchWrap.scrollHeight + parseFloat(paddingTop) + parseFloat(paddingBottom);

      // console.log(`Количество дочерних элементов в .search__result-wrap: ${searchWrap.children.length}`);
      // console.log(`scrollHeight: ${searchWrap.scrollHeight}, totalHeight: ${totalHeight}`);

      if (totalHeight === 0) {
        console.error("Высота контейнера равна 0. Проверьте содержимое .search__result-wrap.");
      } else {
        searchContainer.style.maxHeight = `${totalHeight}px`;
      }
    }, 50);
  };

  const toggleContainerVisibility = (isVisible) => {
    if (!searchContainer) {
      console.error("Элемент .search__result-container не найден в DOM.");
      return;
    }

    if (isVisible) {
      // console.log("Показываем контейнер с результатами поиска.");
      searchContainer.classList.add("_active");
      updateContainerHeight();
      const searchWrap = getSearchWrap();
      if (searchWrap) {
        searchWrap.classList.add("_show");
      }
    } else {
      // console.log("Скрываем контейнер с результатами поиска.");
      const searchWrap = getSearchWrap();
      if (searchWrap) {
        searchWrap.classList.remove("_show");
      }
      setTimeout(() => {
        searchContainer.style.maxHeight = "0px";
        searchContainer.classList.remove("_active");
      }, 200);
    }
  };

  return {
    searchInput,
    clearResult,
    updateResult,
    toggleContainerVisibility,
    updateContainerHeight,
    getSearchWrap,
  };
})();

export const showResultSearch = () => {
  let isContainerVisible = false;

  const handleInput = async (event) => {
    const productName = event.target.value.trim();
    // console.log(`Ввод в поле поиска: "${productName}"`);
  
    if (productName.length < 1) {
      handleEmptyInput();
      return;
    }
  
    console.log(`Запрос на поиск: "${productName}"`);
    const html = await model.asyncSearchResult(productName);
    if (html) {
      handleSearchResults(html, productName);
    } else {
      // console.log(`Результаты поиска для запроса "${productName}" отсутствуют.`);
    }
  };
  
  const handleEmptyInput = () => {
    // console.log("Поле поиска пустое. Очищаем результаты и скрываем контейнер.");
    view.clearResult();
    view.toggleContainerVisibility(false);
    isContainerVisible = false;
  };
  
  const handleSearchResults = (html, productName) => {
    // console.log(`Результаты поиска получены для запроса: "${productName}"`);
    view.updateResult(html);
    const searchWrap = view.getSearchWrap();
    if (!searchWrap) return;
  
    observeDOMChanges(searchWrap);
    view.updateContainerHeight();
  
    if (!isContainerVisible) {
      // console.log("Контейнер с результатами поиска еще не виден. Показываем его.");
      view.toggleContainerVisibility(true);
      isContainerVisible = true;
    }
  };
  
  const observeDOMChanges = (searchWrap) => {
    return new Promise((resolve) => {
      const observer = new MutationObserver(() => {
        // console.log("DOM обновлен после изменения содержимого.");
        observer.disconnect();
        resolve();
      });
      observer.observe(searchWrap, { childList: true });
    });
  };

  const handleFocus = () => {
    const productName = view.searchInput.value.trim();
    // console.log(`Фокус на поле поиска. Текущий запрос: "${productName}"`);

    if (productName.length >= 1 && !isContainerVisible) {
      // console.log(`Запрос в поле поиска: "${productName}". Показываем контейнер с результатами.`);
      view.updateContainerHeight();
      view.toggleContainerVisibility(true);
      isContainerVisible = true;
    } else {
      // console.log("Контейнер уже виден или поле поиска пустое.");
    }
  };

  const handleClickOutside = (e) => {
    if (!e.target.closest(".search_cntr")) {
      // console.log("Клик вне области поиска. Скрываем контейнер.");
      view.toggleContainerVisibility(false);
      isContainerVisible = false;
    }
  };

  const handleResize = () => {
    if (isContainerVisible) {
      // console.log("Изменение размера окна. Обновляем высоту контейнера.");
      view.updateContainerHeight();
    }
  };

  if (view.searchInput) {
    // console.log("Инициализация обработчиков событий для поля поиска.");
    view.searchInput.addEventListener("input", handleInput);
    view.searchInput.addEventListener("focus", handleFocus);
    document.addEventListener("click", handleClickOutside);
    window.addEventListener("resize", handleResize);
  } else {
    console.error("Элемент .header_search не найден в DOM.");
  }
};
