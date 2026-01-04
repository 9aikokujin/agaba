export async function tabReviewQuestion() {
    
    const tabButtons = document.querySelectorAll('.RMP-tab_btn');
    const contentBlocks = document.querySelectorAll('.RMP_comment-question_block');

    function activateTab(tabNumber) {
        tabButtons.forEach(button => button.classList.remove('active'));
        contentBlocks.forEach(block => block.classList.remove('_active'));

        document.querySelector(`.RMP-tab_btn[data-tab="${tabNumber}"]`).classList.add('active');
        document.querySelector(`.RMP_comment-question_block[data-tab="${tabNumber}"]`).classList.add('_active');
    }

    activateTab(1);

    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const tabNumber = this.getAttribute('data-tab');
            activateTab(tabNumber);
        });
    });
}
