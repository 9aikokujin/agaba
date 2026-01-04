export async function showHiddenHeaderCatalog() {
  const catalogBtn = document.querySelector(".catalog_btn");
  const mobileCatalogBtn = document.querySelector(".mobile__nav-link._catalog");
  const catalogContainer = document.querySelector(".catalog__hidden-container");
  const catalogWrap = document.querySelector(".catalog__hidden-wrap");
  const mobileMenu = document.querySelector(".mobile__menu");

  if (
    !catalogBtn ||
    !mobileCatalogBtn ||
    !catalogContainer ||
    !catalogWrap ||
    !mobileMenu
  )
    return;

  const toggleCatalog = () => {
    const isActive = catalogContainer.classList.contains("_active");

    if (isActive) {
      catalogWrap.classList.remove("_show");
      catalogBtn.classList.remove("_opac");
      mobileCatalogBtn.classList.remove("_opac");
      catalogContainer.classList.add("_collapsing");

      setTimeout(() => {
        catalogContainer.classList.remove("_collapsing");
        catalogContainer.classList.remove("_active");
        catalogContainer.style.maxHeight = "0";
      }, 200);
    } else {
      catalogContainer.classList.add("_active");
      catalogContainer.style.maxHeight = `${catalogContainer.scrollHeight}px`;
      setTimeout(() => {
        catalogWrap.classList.add("_show");
        catalogBtn.classList.add("_opac");
        mobileCatalogBtn.classList.add("_opac");
      }, 200);
    }
  };

  const removeClasses = () => {
    catalogWrap.classList.remove("_show");
    catalogBtn.classList.remove("_opac");
    mobileCatalogBtn.classList.remove("_opac");
    catalogContainer.classList.remove("_active");
    catalogContainer.style.maxHeight = "0";
  };

  catalogBtn.addEventListener("click", (e) => {
    e.preventDefault();
    toggleCatalog();
  });

  mobileCatalogBtn.addEventListener("click", (e) => {
    e.preventDefault();
    toggleCatalog();
  });

  mobileMenu.addEventListener("click", (e) => {
    e.preventDefault();
    removeClasses();
  });

  document.addEventListener("click", (e) => {
    const isClickInsideCatalog = e.target.closest(".catalog__hidden-container");
    const isClickOnAnotherNavLink =
      e.target.closest(".mobile__nav-link") &&
      !e.target.closest(".mobile__nav-link._catalog");
    const isClickOnCatalogBtn = e.target.closest(".catalog_btn");

    if (
      !isClickInsideCatalog &&
      !isClickOnCatalogBtn &&
      (isClickOnAnotherNavLink ||
        catalogContainer.classList.contains("_active"))
    ) {
      removeClasses();
    }
  });
}
