  $('.pro-slide-single').slick({
    slidesToShow: 1,
    slidesToScroll: 1,
    arrows: false,
    fade: true,
    asNavFor: '.pro-slide-right'
  });
  if ($(window).width() > 1200) {
    $('.pro-slide-right').slick({
      vertical: true,
      verticalSwiping: true,
      slidesToShow: 3,
      slidesToScroll: 1,
      asNavFor: '.pro-slide-single',
      arrows: false,
      infinite: true,
      dots: false,
      centerMode: false,
      focusOnSelect: true
    });
  }else{
    $('.pro-slide-right').slick({
      vertical: false,
      verticalSwiping: false,
      slidesToShow: 3,
      slidesToScroll: 1,
      asNavFor: '.pro-slide-single',
      arrows: false,
      infinite: true,
      centerMode: false,
      dots: false,
      focusOnSelect: true,
      responsive: [
        {
          breakpoint: 1199,
          settings: {
            slidesToShow: 3,
            slidesToScroll: 1,                      
          }
        },
        {
          breakpoint: 576,
          settings: {
            slidesToShow: 3,
            slidesToScroll: 1
          }
        }
      ]
    });
  }