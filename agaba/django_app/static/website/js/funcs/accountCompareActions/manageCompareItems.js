// Модель (Model)
const createModel = (compareItems) => {
  let state = {
    currentIndex: 0,
    itemsPerPage: 3,
    items: Array.from(compareItems),
  };

  const getState = () => state;

  const nextSlide = () => {
    if (state.currentIndex < state.items.length - state.itemsPerPage) {
      state.currentIndex++;
    }
  };

  const prevSlide = () => {
    if (state.currentIndex > 0) {
      state.currentIndex--;
    }
  };

  const updateCurrentIndex = () => {
    if (state.currentIndex >= state.items.length) {
      state.currentIndex = Math.max(0, state.items.length - state.itemsPerPage);
    }
  };

  const removeItem = (item) => {
    const index = state.items.indexOf(item);
    if (index !== -1) {
      state.items.splice(index, 1);

      if (state.currentIndex > state.items.length - state.itemsPerPage) {
        state.currentIndex = Math.max(
          0,
          state.items.length - state.itemsPerPage,
        );
      }
    }
  };

  return {
    getState,
    nextSlide,
    prevSlide,
    updateCurrentIndex,
    removeItem,
  };
};

// Представление (View)
const createView = (model, nextButton, prevButton, itemCounter) => {
  const render = () => {
    const { currentIndex, itemsPerPage, items } = model.getState();
    items.forEach((item, index) => {
      item.style.display =
        index >= currentIndex && index < currentIndex + itemsPerPage
          ? "flex"
          : "none";
    });

    const totalItems = items.length;
    itemCounter.textContent = totalItems;

    if (totalItems <= itemsPerPage) {
      nextButton.style.pointerEvents = "none";
      prevButton.style.pointerEvents = "none";
    } else {
      nextButton.style.pointerEvents =
        currentIndex >= totalItems - itemsPerPage ? "none" : "";
      prevButton.style.pointerEvents = currentIndex === 0 ? "none" : "";
    }
  };

  const removeItemFromView = (item) => {
    try {
      item.remove();
      render();
    } catch (error) {
      console.error("Error removing item from view:", error);
    }
  };

  return {
    render,
    removeItemFromView,
  };
};

// Контроллер (Controller)
const setupController = (
  model,
  view,
  nextButton,
  prevButton,
  deleteButtons,
  swipeContainer,
) => {
  const updateView = () => {
    model.updateCurrentIndex();
    view.render();
  };

  nextButton.addEventListener("click", () => {
    model.nextSlide();
    updateView();
  });

  prevButton.addEventListener("click", () => {
    model.prevSlide();
    updateView();
  });

  deleteButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const itemToRemove = button.closest("._compare__item");
      if (itemToRemove) {
        model.removeItem(itemToRemove);
        view.removeItemFromView(itemToRemove);
      }
    });
  });

  // Swipe functionality
  let startX = 0;
  let endX = 0;

  swipeContainer.addEventListener("touchstart", (e) => {
    startX = e.touches[0].clientX;
  });

  swipeContainer.addEventListener("touchmove", (e) => {
    endX = e.touches[0].clientX;
  });

  swipeContainer.addEventListener("touchend", () => {
    if (startX > endX + 50) {
      model.nextSlide();
    } else if (startX < endX - 50) {
      model.prevSlide();
    }
    updateView();
  });
};

const updateItemsPerPage = (model) => {
  const width = window.innerWidth;
  model.getState().itemsPerPage = width <= 1300 ? 2 : 3;
};

export function manageCompareItems() {
  const lists = document.querySelectorAll(
    ".acc__order_delivery.catalog_list._compare__list",
  );
  const nextButton = document.querySelector(".compare__next_slider");
  const prevButton = document.querySelector(".compare__prev_slider");
  const tabButtons = document.querySelectorAll(".order__tab_btn");

  if (!nextButton || !prevButton || !tabButtons.length) return;

  tabButtons.forEach((button) => {
    button.addEventListener("click", () => {
      tabButtons.forEach((btn) => btn.classList.remove("active"));
      button.classList.add("active");
      const tabIndex = button.getAttribute("tab-index");

      lists.forEach((list) => {
        list.style.display =
          list.getAttribute("tab-index") === tabIndex ? "flex" : "none";
      });

      initializeList(tabIndex);
    });
  });

  const initializeList = (tabIndex) => {
    const activeList = document.querySelector(
      `.catalog_list[tab-index="${tabIndex}"]`,
    );
    if (!activeList) return;

    const items = Array.from(
      activeList.querySelectorAll(".catalog_item._compare__item"),
    );
    const itemCounter = document.querySelector(
      `.order__tab_btn[tab-index="${tabIndex}"] ._item_counter`,
    );
    const deleteButtons = activeList.querySelectorAll(".compare__delete_btn");

    if (!itemCounter) return;

    const model = createModel(items);
    updateItemsPerPage(model);
    const view = createView(model, nextButton, prevButton, itemCounter);

    setupController(
      model,
      view,
      nextButton,
      prevButton,
      deleteButtons,
      activeList,
    );
    view.render();

    window.addEventListener("resize", () => {
      updateItemsPerPage(model);
      view.render();
    });
  };

  const activeTabButton = Array.from(tabButtons).find((button) =>
    button.classList.contains("active"),
  );
  if (activeTabButton) {
    const initialTabIndex = activeTabButton.getAttribute("tab-index");
    initializeList(initialTabIndex);
  }
}
