export function SearchAndConnectRooms() {
    // redirect to '/room/<roomSelect>/'
    // document.querySelector("#roomSelect").onchange = function() {
    //     let roomName = document.querySelector("#roomSelect").value.split(" (")[0];
    //     window.location.pathname = "chat/" + roomName + "/";
    // }
    console.log("Sanity check from Я инициалзировался оунтик.");
    document.addEventListener("DOMContentLoaded", () => {

        // Находим все ссылки с классом 'agaba_message'
        const messageLinks = document.querySelectorAll(".agaba_message._message_item");

        // Добавляем обработчик клика для каждой ссылки
        messageLinks.forEach(link => {
            link.addEventListener("click", function(event) {
                event.preventDefault(); // Отменяем стандартное действие ссылки

                // Находим ближайший родительский элемент <li> (контейнер комнаты)
                const roomListItem = this.closest("li.acc_main-item");

                // Извлекаем название комнаты из текста <h4>
                const roomNameElement = roomListItem.querySelector("h4");
                if (!roomNameElement) return;

                const roomName = roomNameElement.textContent.trim();

                if (roomName) {
                    // Перенаправляем пользователя на страницу чата
                    window.location.pathname = `/chat/${encodeURIComponent(roomName)}/`;
                }
            });
        });
    });
}