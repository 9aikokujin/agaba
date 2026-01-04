export async function toggleTabCardProductDescription() {
    const tabButtons = document.querySelectorAll('.chars_tab-btn');
    const tabContentItems = document.querySelectorAll('.chars_tab-content_item');

    tabButtons.forEach((button, index) => {
        button.addEventListener('click', () => {
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContentItems.forEach(item => item.classList.remove('active'));

            button.classList.add('active');
            tabContentItems[index].classList.add('active');
        });
    });
}
