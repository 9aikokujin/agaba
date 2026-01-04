export async function showFiltersAside() {
    const button = document.querySelector('.filter_feature-btn.filters');
    const sidebar = document.querySelector('.filters_sidebar');
    const showAllButton = document.querySelector('.show_all-btn');
    const filtersContainer = document.querySelector('.filters_cntr');

    const toggleSidebarVisibility = (event) => {
        if (!filtersContainer.contains(event.target) && !button.contains(event.target)) {
            sidebar.classList.remove('show');
        }
    };

    const showSidebar = () => {
        sidebar.classList.add('show');
    };

    const hideSidebar = () => {
        sidebar.classList.remove('show');
    };

    button.addEventListener('click', showSidebar);
    document.addEventListener('click', toggleSidebarVisibility);
    showAllButton.addEventListener('click', hideSidebar);
}
