export const starRatingAction = () => {
    const starContainer = document.querySelector('.stars__cntr');
    const starInputs = Array.from({ length: 5 }, (_, i) => document.getElementById(`commentRating_modal_${i + 1}`));
  
    // состояние
    let rating = 0;
  
    const setRating = (newRating) => {
      rating = newRating;
    };
  
    // обновляет состояени звездочек
    const updateStars = () => {
      starInputs.forEach((star, index) => {
        if (star) {
          star.checked = (index < rating);
        }
      });
    };
  
    // рендер
    const render = () => {
      updateStars();
    };
  
    // контроллер
    const handleStarClick = (e) => {
      const starValue = parseInt(e.target.id.split('_')[2], 10);
      if (!isNaN(starValue)) {
        setRating(starValue);
        render();
      }
    };
  
    if (starContainer) {
      starContainer.addEventListener('click', handleStarClick);
      render();
    }
  };