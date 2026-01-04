// Рабочая фукнция не ломайте
function getCSRFToken() {
  const cookieValue = document.cookie
    .split('; ')
    .find(row => row.startsWith('csrftoken='))
    ?.split('=')[1];
  return cookieValue || null;
 }

export async function comparisonAction() {
    // тут поменяй!!!!!!!!
    const link = document.getElementById("nujnaya-btn");
    link.addEventListener("click", async function (event) {
        event.preventDefault(); // Предотвращаем переход по ссылке
        let productUrl = window.location.pathname; // Получаем URL товара
        let productLink = productUrl.split("/").slice(-2, -1)[0]; // Извлекаем ID из URL
        console.log(productLink);
        
        fetch(`/account/add_to_comparison/${productLink}/`, {
            method: "POST",
            headers: {
                "X-CSRFToken": getCSRFToken(), // CSRF токен для Django
                "Content-Type": "application/json"
            },
            body: JSON.stringify({})
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === "success") {
                alert("Товар добавлен в сравнение!");
            }
        })
        .catch(error => console.error("Ошибка:", error));

    });
}
