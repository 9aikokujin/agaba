export async function toggleLangSelect() {
    const langSelect = document.querySelector('.lang_select');
    const langCntr = document.querySelector('.lang_cntr');
    const langHiddenCntr = document.querySelector('.lang_hidden-cntr');

    function attachListeners() {
        const langItemCntr = langCntr.querySelector('.lang_item');

        langItemCntr.addEventListener('click', () => {
            langSelect.classList.toggle('hidden');
        });

        langHiddenCntr.querySelectorAll('.lang_item').forEach(item => {
            item.addEventListener('click', () => {
                const currentLangItem = langItemCntr.cloneNode(true);

                langCntr.replaceChild(item.cloneNode(true), langItemCntr);

                langHiddenCntr.replaceChild(currentLangItem, item);

                langSelect.classList.add('hidden');

                attachListeners();
            });
        });
    }

    attachListeners();
}
