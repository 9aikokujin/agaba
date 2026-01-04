$(".card_comment-slider_list").slick({
    dots: false,
    infinite: true,
    arrows : true,
    centerMode: true,
    swipe: true,
    speed: 500,
    autoplay:false,
    slidesToShow: 2,
    slidesToScroll: 1,
    responsive: [
        {
            breakpoint: 600,
            settings: {
                slidesToShow: 1,
                slidesToScroll: 1,
                arrows : false,
                centerMode: true,
            }
        },
    ]
});

$(".order_items-slider-list").slick({
    dots: false,
    infinite: true,
    arrows : true,
    centerMode: false,
    swipe: true,
    speed: 500,
    autoplay:false,
    slidesToShow: 3,
    slidesToScroll: 1,
    responsive: [
        {
            breakpoint: 1200,
            settings: {
                slidesToShow: 2,
                slidesToScroll: 1
            }
        },
        {
            breakpoint: 1024,
            settings: {
                slidesToShow: 1,
                slidesToScroll: 1
            }
        },
        {
            breakpoint: 768,
            settings: {
                slidesToShow: 2,
                slidesToScroll: 1
            }
        },
        {
            breakpoint: 600,
            settings: {
                slidesToShow: 2,
                slidesToScroll: 1
            },
            infinite: true,
        }
    ]
});

$(document).ready(function() {
    function initializeSlick() {
        const slider = $('.header__nav._pop-list');
        if ($(window).width() <= 1200) {
            if (!slider.hasClass('slick-initialized')) {
                slider.slick({
                    dots: false,
                    infinite: false,
                    arrows: false,
                    centerMode: false,
                    swipe: true,
                    speed: 500,
                    autoplay: false,
                    slidesToShow: 6,
                    slidesToScroll: 3,
                    variableWidth: true,
                    responsive: [
                        {
                            breakpoint: 1200,
                            settings: {
                                slidesToShow: 4,
                                slidesToScroll: 1
                            }
                        },
                        {
                            breakpoint: 1023.98,
                            settings: {
                                slidesToShow: 3,
                                slidesToScroll: 1
                            }
                        }
                    ]
                });
            }
        } else {
            if (slider.hasClass('slick-initialized')) {
                slider.slick('unslick');
                slider.removeAttr('style');
                slider.find('.slick-slide').removeAttr('style');
            }
        }
    }

    initializeSlick();

    $(window).resize(function() {
        initializeSlick();
    });
});