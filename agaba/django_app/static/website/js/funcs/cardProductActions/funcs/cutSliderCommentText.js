export async function cutSliderCommentText() {
    const descriptions = document.querySelectorAll('.comment_content_list.slider_wrap .comment_content-description');
    const maxChars = window.innerWidth < 800 ? 80 : 225;

    descriptions.forEach(description => {
        const textElement = description.querySelector('.comment_content-text');
        const originalText = textElement.textContent;

        if (originalText.length > maxChars) {
            const truncatedText = originalText.substring(0, maxChars) + '...';
            textElement.textContent = truncatedText;
        }
    });
}
