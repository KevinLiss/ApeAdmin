(function ($) {
  "use strict";
  function equalizer() {
    var max = -1;
    $(".height-equal").css("min-height", "auto");
    $(".height-equal").each(function () {
      var minHeight = $(this).outerHeight();
      max = minHeight > max ? minHeight : max;
    });
    $(".height-equal").css("min-height", max);
    if ($(window).width() <= 991) {
      $(".height-equal").css("min-height", "auto");
    }
  }
  equalizer();
  $(window).resize(function () {
    equalizer();
  });
})(jQuery);
