export async function showMenuItems() {
    const mobileMenuBtns = document.querySelectorAll('.mobile__nav-link');
    const mobileContentContainers = document.querySelectorAll('.mobile__menu-hidden-cntr');

    if (!mobileMenuBtns || !mobileContentContainers) return;

    function toggleMenu(index) {
        mobileContentContainers.forEach((container, idx) => {
            const hiddenList = container.querySelector('.mobile__menu-hidden_list');
            if (idx === index) {
                container.classList.toggle('show');
                if (container.classList.contains('show')) {
                    hiddenList.style.transition = 'opacity 0.1s';
                    setTimeout(() => {
                        hiddenList.style.opacity = '1';
                    }, 400);
                } else {
                    hiddenList.style.transition = 'opacity 0.1s';
                    hiddenList.style.opacity = '0';
                    setTimeout(() => {
                        container.classList.remove('show');
                    }, 100);
                }
            } else {
                container.classList.remove('show');
                if (hiddenList) {
                    hiddenList.style.opacity = '0';
                }
            }
        });
    }

    mobileMenuBtns.forEach((btn, index) => {
        btn.addEventListener('click', (event) => {
            event.stopPropagation();
            toggleMenu(index);
        });
    });
}
