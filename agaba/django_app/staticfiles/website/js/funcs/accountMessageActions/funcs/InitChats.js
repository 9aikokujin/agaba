console.log("Sanity check from Я ТУТ!");
export function InitChat() {
    document.addEventListener("DOMContentLoaded", () => {

    // Получаем элементы интерфейса
    const roomName = JSON.parse(document.getElementById('roomName').textContent);
    const messageList = document.querySelector(".message__body_list");
    const messageTextarea = document.querySelector(".MP__message_textarea");
    const sendMessageButton = document.querySelector(".message_send_btn");

    // Подключаемся к WebSocket
    const socket = new WebSocket(`ws://${window.location.host}/ws/chat/${roomName}/`);

    socket.onopen = () => {
        console.log("WebSocket connected");
    };

    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        addMessage(data.sender, data.message, false); // Добавляем сообщение другого пользователя
    };

    socket.onclose = () => {
        console.log("WebSocket disconnected");
    };

    // Функция для добавления нового сообщения
    function addMessage(senderName, messageText, isCurrentUser = false) {
        // Создаем новый элемент <li>
        const newMessage = document.createElement("li");
        newMessage.className = `message__body_item ${isCurrentUser ? "_to" : "_from"}`;

        // Добавляем заголовок (имя отправителя и время)
        const header = document.createElement("h5");
        header.className = "MB__item_header";
        const currentTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        header.textContent = `${senderName}, ${currentTime}`;
        newMessage.appendChild(header);

        // Добавляем тело сообщения
        const body = document.createElement("div");
        body.className = "MB__item_body";
        const text = document.createElement("p");
        text.textContent = messageText;
        body.appendChild(text);
        newMessage.appendChild(body);

        // Добавляем сообщение в список
        messageList.appendChild(newMessage);

        // Прокручиваем чат вниз
        messageList.scrollTop = messageList.scrollHeight;
    }

    // Обработчик отправки сообщения
    function sendMessage() {
        const messageText = messageTextarea.value.trim();
        if (!messageText) return;

        // Отправляем сообщение через WebSocket
        socket.send(JSON.stringify({
            sender: "Вы",
            message: messageText,
        }));

        // Добавляем сообщение текущего пользователя
        addMessage("Вы", messageText, true);

        // Очищаем поле ввода
        messageTextarea.value = "";
    }

    // Добавляем обработчик клика на кнопку "Отправить"
    sendMessageButton.addEventListener("click", sendMessage);

    // Добавляем обработчик нажатия клавиши Enter
    messageTextarea.addEventListener("keyup", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault(); // Отменяем перенос строки
            sendMessage();
        }
    });

    // Обновление счетчика символов
    messageTextarea.addEventListener("input", () => {
        const counter = document.querySelector(".MP_footer_counter");
        const maxLength = 1000;
        const currentLength = messageTextarea.value.length;
        counter.textContent = `${currentLength} / ${maxLength} символов`;
    });
});
}