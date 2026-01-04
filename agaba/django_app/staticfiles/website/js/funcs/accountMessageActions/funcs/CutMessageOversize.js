export function CutMessageOversize () {
    // const mediaQuery = window.matchMedia('(max-width: 768px)');

    // const handleScreenChange = (e) => {
    //     const messageText = document.querySelectorAll("._message_item");

    //     if(!messageText) return;
        
    //     const textCut = (text) => {
    //         if (text.length > 120) {
    //             return text.substring(0, 120) + '...';
    //         }
    //         return text;
    //     };

    //     if (e.matches) {
    //         messageText.forEach(item => {
    //             const origText = item.textContent.trim();
    //             item.textContent = textCut(origText);
    //         });
    //     } else {
    //         messageText.forEach(item => {
    //             const origText = item.getAttribute('data-original-text') || item.textContent;
    //             item.textContent = origText;
    //             if (!item.getAttribute('data-original-text')) {
    //                 item.setAttribute('data-original-text', origText);
    //             }
    //         });
    //     }
    // };

    // handleScreenChange(mediaQuery);
    // mediaQuery.addEventListener('change', handleScreenChange);
}