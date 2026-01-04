export async function itemsSelectHoverShow() {
    const navLinks = document.querySelectorAll('.car_nav-link.select');
    let activeIndex = null;
    let activeContainer = null;

    const showSelectItem = (index, container) => {
        hideAllSelectItems();
        hideAllContainers();
        
        const item = container.querySelector(`.select__item[data-index="${index}"]`);
        
        if (item) {
            item.classList.add('active');
        }
    };

    const toggleSelectItem = (index, link, container) => {
        if (activeIndex === index && activeContainer === container) {
            hideAllSelectItems();
            container.style.display = 'none';
            activeIndex = null;
            activeContainer = null;
            resetNavLinkStyles();
        } else {
            hideAllSelectItems();
            hideAllContainers();
            showSelectItem(index, container);
            activeIndex = index;
            activeContainer = container;
            setActiveNavLinkStyles(link);
            container.style.display = 'block';
        }
    };

    const hideAllSelectItems = () => {
        document.querySelectorAll('.select__item').forEach(item => item.classList.remove('active'));
    };

    const hideAllContainers = () => {
        document.querySelectorAll('.select__container').forEach(container => container.style.display = 'none');
    };

    const resetNavLinkStyles = () => {
        navLinks.forEach(link => link.classList.remove('active'));
    };

    const setActiveNavLinkStyles = (link) => {
        resetNavLinkStyles();
        link.classList.add('active');
    };

    navLinks.forEach(link => {
        const index = link.getAttribute('data-index');
        const container = link.closest('.header__nav_pop-item').querySelector('.select__container');
        
        link.addEventListener('click', (e) => {
            e.preventDefault();
            toggleSelectItem(index, link, container);
        });
    });

    document.addEventListener('click', (e) => {
        if (!e.target.closest('.select__container') && 
            !e.target.closest('.car_nav-link.select')) {
            hideAllSelectItems();
            hideAllContainers();
            resetNavLinkStyles();
            activeIndex = null;
            activeContainer = null;
        }
    });
}
