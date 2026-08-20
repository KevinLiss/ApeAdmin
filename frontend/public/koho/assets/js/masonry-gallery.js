(function ($) {
  "use strict";
  var masonry_gallery = {
    init: function () {
      $(".grid").isotope({
        itemSelector: ".grid-item",
      });
    },
  };
  masonry_gallery.init();
})(jQuery);
