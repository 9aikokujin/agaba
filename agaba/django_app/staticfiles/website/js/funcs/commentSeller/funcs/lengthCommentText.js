export async function lengthCommentText() {
    const comments = document.querySelectorAll('.comment_content-text');

    comments.forEach(comment => {
        const originalText = comment.textContent;
        let maxLength;

        if (window.innerWidth > 1200) {
            maxLength = 250;
        } else if (window.innerWidth > 768) {
            maxLength = 150;
        } else {
            maxLength = 80;
        }

        if (originalText.length > maxLength) {
            comment.textContent = originalText.substring(0, maxLength) + '...';
        }
    });
}