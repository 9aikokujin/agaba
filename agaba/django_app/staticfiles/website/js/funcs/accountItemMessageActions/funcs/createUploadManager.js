export function createUploadManager(config = {}) {
    const defaultConfig = {
        MAX_FILE_SIZE: 20 * 1024 * 1024,
        ALLOWED_TYPES: new Set(['image/jpeg', 'image/png', 'application/pdf']),
        MAX_FILES: 10
    };

    const CONFIG = { ...defaultConfig, ...config };

    return function initialize(elements) {
        if (!elements || !Object.values(elements).every(Boolean)) {
            throw new Error('Required elements not provided');
        }

        function resetUploadState() {
            elements.uploadedFilesList.innerHTML = '';
            elements.uploadedFilesCntr.style.display = 'none';
            elements.uploadText.style.display = 'block';
            elements.fileInput.disabled = false;
            elements.fileInput.value = '';
        }

        function validateFile(file) {
            const errors = [];
            
            if (!CONFIG.ALLOWED_TYPES.has(file.type)) {
                errors.push(`Файл "${file.name}" имеет неподдерживаемый формат`);
            }
            if (file.size > CONFIG.MAX_FILE_SIZE) {
                errors.push(`Файл "${file.name}" превышает допустимый размер 20MB`);
            }

            return errors;
        }

        function getCurrentFilesCount() {
            return elements.uploadedFilesList.querySelectorAll('.MP__footer_uploaded_item').length;
        }

        function createFileElement(file) {
            const listItem = document.createElement('li');
            listItem.className = 'MP__footer_uploaded_item';

            const viewDiv = document.createElement('div');
            viewDiv.className = 'MP__footer_uploaded_view';

            const img = document.createElement('img');
            img.className = 'MT__UploadedFileIcon';
            img.src = '/img/messages_img/uploadedDocument.png';
            img.alt = 'uploaded document icon';

            const deleteButton = document.createElement('button');
            deleteButton.type = 'button';
            deleteButton.className = 'MP__footer_delete_file_btn';

            function handleDelete() {
                listItem.remove();
                const currentCount = getCurrentFilesCount();
                
                if (currentCount < CONFIG.MAX_FILES) {
                    elements.fileInput.disabled = false;
                }

                if (currentCount === 0) {
                    elements.uploadedFilesCntr.style.display = 'none';
                    elements.uploadText.style.display = 'block';
                }
            }

            deleteButton.addEventListener('click', handleDelete, { once: true });

            viewDiv.append(img, deleteButton);
            listItem.appendChild(viewDiv);
            return listItem;
        }

        function handleFileSelect(event) {
            const files = Array.from(event.target.files);
            const currentFilesCount = getCurrentFilesCount();
            const remainingSlots = CONFIG.MAX_FILES - currentFilesCount;
            
            if (remainingSlots <= 0) return;

            const filesToProcess = files.slice(0, remainingSlots);
            const validFiles = filesToProcess.filter(file => validateFile(file).length === 0);

            if (validFiles.length > 0) {
                elements.uploadedFilesCntr.style.display = 'block';
                elements.uploadText.style.display = 'none';
                
                validFiles.forEach(file => {
                    const fileElement = createFileElement(file);
                    elements.uploadedFilesList.appendChild(fileElement);
                });

                if (getCurrentFilesCount() >= CONFIG.MAX_FILES) {
                    elements.fileInput.disabled = true;
                }
            }

            elements.fileInput.value = '';
        }

        resetUploadState();
        elements.fileInput.addEventListener('change', handleFileSelect);

        return {
            reset: resetUploadState,
            cleanup: () => elements.fileInput.removeEventListener('change', handleFileSelect),
            getCurrentFiles: () => Array.from(elements.uploadedFilesList.querySelectorAll('.MT__UploadedFileIcon'))
        };
    };
}
