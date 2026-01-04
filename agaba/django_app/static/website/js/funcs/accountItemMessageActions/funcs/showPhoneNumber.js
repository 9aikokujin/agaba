export const showPhoneNumber = () => {
    const phoneLinks = document.querySelectorAll('.message__show_phone');
    const mobileBreakpoint = 768;

    if (!phoneLinks) return;
    
    const formatPhoneForMobile = () => {
        return '+7...';
    };

    const handlePhoneDisplay = () => {
        phoneLinks.forEach(link => {
            if (window.innerWidth < mobileBreakpoint) {
                link.textContent = formatPhoneForMobile();
            }
        });
    };

    handlePhoneDisplay();

    window.addEventListener('resize', handlePhoneDisplay);
    
    phoneLinks.forEach(link => {
        let isNumberRevealed = false;

        link.addEventListener('click', function(e) {
            if (window.innerWidth < mobileBreakpoint) {
                return;
            }

            if (!isNumberRevealed) {
                e.preventDefault();
                const phoneNumber = this.getAttribute('href').replace('tel:', '');
                this.textContent = phoneNumber;
                isNumberRevealed = true;
            }
        });
    });
};
