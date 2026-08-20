(function ($) {
  "use strict";
  $(window).scroll(function () {
    if ($(this).scrollTop() > 100) {
      $(".page-header").fadeOut();
      $(".page-body-wrapper").addClass("scorlled");
    } else {
      $(".page-header").fadeIn();
      $(".page-body-wrapper").removeClass("scorlled");
    }
  });
})(jQuery);
