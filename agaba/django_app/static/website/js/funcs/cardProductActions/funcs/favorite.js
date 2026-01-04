function getCSRFToken() {
    const cookieValue = document.cookie
      .split('; ')
      .find(row => row.startsWith('csrftoken='))
      ?.split('=')[1];
    return cookieValue || null;
   }
  
  export async function favoriteProductsActions() {
      
      const link = document.getElementById("for_fav-btn");
      link.addEventListener("click", async function (event) {
          event.preventDefault(); // Предотвращаем переход по ссылке
          let productUrl = window.location.pathname; // Получаем URL товара
          let productLink = productUrl.split("/").slice(-2, -1)[0]; // Извлекаем ID из URL
          console.log(productLink);
          console.log("oipsdfnojngfpowqgf");
          
          fetch(`/account/add_to_favorites/${productLink}/`, {
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
                  alert("Товар добавлен в избранное!");
              }
          })
          .catch(error => console.error("Ошибка:", error));
      });
  }