import { createUploadManager } from './createUploadManager.js';

export function initializeMessageHandling() {
    function createMessageSystem(elements) {
        if (!elements || !Object.values(elements).every(Boolean)) {
            throw new Error('[Message System] Required DOM elements not found');
        }

        const uploadManager = createUploadManager()(
            {
                fileInput: document.querySelector('.message__input_upload'),
                uploadedFilesCntr: document.querySelector('.MP__footer_uploaded_files_cntr'),
                uploadedFilesList: document.querySelector('.MP__footer_uploaded_files_list'),
                uploadText: document.querySelector('.MP__footer_upload_text'),
                uploadFooter: document.querySelector('.MP__footer_upload')
            }
        );

        function createMessageElement(text, files) {
            if (!text.trim() && files.length === 0) return null;

            const messageItem = document.createElement('li');
            messageItem.className = 'message__body_item _to';

            const header = createMessageHeader();
            messageItem.appendChild(header);

            if (text.trim()) {
                const bodyDiv = createMessageBody(text);
                messageItem.appendChild(bodyDiv);
            }

            if (files.length > 0) {
                const footerDiv = createMessageFooter(files);
                messageItem.appendChild(footerDiv);
            }

            return messageItem;
        }

        function createMessageHeader() {
            const header = document.createElement('h5');
            header.className = 'MB__item_header';
            const currentTime = new Date();
            const formattedDate = new Intl.DateTimeFormat('ru', {
                day: '2-digit',
                month: 'long',
                hour: '2-digit',
                minute: '2-digit'
            }).format(currentTime);
            header.innerHTML = `Вы, <time datetime="${currentTime.toISOString()}">${formattedDate}</time>`;
            return header;
        }

        function createMessageBody(text) {
            const bodyDiv = document.createElement('div');
            bodyDiv.className = 'MB__item_body';
            const paragraph = document.createElement('p');
            paragraph.textContent = text.trim();
            bodyDiv.appendChild(paragraph);
            return bodyDiv;
        }

        function createMessageFooter(files) {
            const footerDiv = document.createElement('div');
            footerDiv.className = 'MB__item_footer';
            
            files.forEach(() => {
                const fileLink = document.createElement('a');
                fileLink.className = 'MB_added_document';
                fileLink.href = '#';
                fileLink.target = '_blank';

                const fileImg = document.createElement('img');
                fileImg.src = '/img/messages_img/uploadedDocument.png';
                fileImg.alt = 'uploaded Document';

                const formatSpan = document.createElement('span');
                formatSpan.className = 'message_doc_format';
                formatSpan.textContent = 'pdf';

                fileLink.append(fileImg, formatSpan);
                footerDiv.appendChild(fileLink);
            });

            return footerDiv;
        }

        function handleSubmit(event) {
            if (event) event.preventDefault();

            const messageText = elements.messageTextarea.value;
            const uploadedFiles = uploadManager.getCurrentFiles();

            if (!messageText.trim() && uploadedFiles.length === 0) return;

            const messageElement = createMessageElement(messageText, uploadedFiles);

            if (messageElement) {
                elements.messageList.appendChild(messageElement);
                uploadManager.reset();
                elements.messageTextarea.value = '';

                // messageElement.scrollIntoView({
                //     behavior: 'smooth',
                //     block: 'end'
                // })
            }
        }

        function bindEvents() {
            const boundHandleSubmit = handleSubmit.bind(null);
            elements.sendButton.addEventListener('click', boundHandleSubmit);
            elements.messageTextarea.addEventListener('keydown', event => {
                if (event.key === 'Enter' && !event.shiftKey) {
                    event.preventDefault();
                    boundHandleSubmit(event);
                }
            });

            return () => {
                elements.sendButton.removeEventListener('click', boundHandleSubmit);
                elements.messageTextarea.removeEventListener('keydown', boundHandleSubmit)();
            };
        }

        return bindEvents();
    }

    const elements = {
        messageTextarea: document.querySelector('.MP__message_textarea'),
        messageList: document.querySelector('.message__body_list'),
        sendButton: document.querySelector('.message_send_btn'),
        uploadText: document.querySelector('.MP__footer_upload_text')
    };

    return createMessageSystem(elements);
}
