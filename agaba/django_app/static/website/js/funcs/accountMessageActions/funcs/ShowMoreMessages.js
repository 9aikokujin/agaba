export const ShowMoreMessages = () => {
    const messageBlocks = document.querySelectorAll('._message_block');
    const showMoreButton = document.querySelector('.show_more_massages_btn');
    const INITIAL_VISIBLE = 5;
    const LOAD_MORE_COUNT = 4;
    const DELAY_MS = 300; 
    let currentlyShown = INITIAL_VISIBLE;
    let isLoading = false;

    if(!messageBlocks || !showMoreButton) return;

    const updateMessagesVisibility = () => {
        messageBlocks.forEach((block, index) => {
            if (index < currentlyShown) {
                block.style.display = 'block';
            } else {
                block.style.display = 'none';
            }
        });
    };

    const updateButtonVisibility = () => {
        const buttonContainer = document.querySelector('._show_more_cntr');
        if (messageBlocks.length <= INITIAL_VISIBLE || currentlyShown >= messageBlocks.length) {
            buttonContainer.style.display = 'none';
        } else {
            buttonContainer.style.display = 'block';
        }
    };

    const handleShowMore = async () => {
        if (isLoading) return;
        
        isLoading = true;
        showMoreButton.disabled = true;
        
        try {
            await new Promise(resolve => setTimeout(resolve, DELAY_MS));
            currentlyShown = Math.min(currentlyShown + LOAD_MORE_COUNT, messageBlocks.length);
            updateMessagesVisibility();
            updateButtonVisibility();
        } catch (error) {
            console.error('Error loading more messages:', error);
        } finally {
            isLoading = false;
            showMoreButton.disabled = false; 
        }
    };

    const init = () => {
        if (showMoreButton) {
            showMoreButton.addEventListener('click', handleShowMore);
            updateMessagesVisibility();
            updateButtonVisibility();
        }
    };

    init();
};
