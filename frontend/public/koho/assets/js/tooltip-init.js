(function ($) {
  "use strict";
  $(document).ready(function () {
    var tooltip_init = {
      init: function () {
        $("button").tooltip();
        $("a").tooltip();
        $("input").tooltip();
      },
    };
    tooltip_init.init();
  });

  var tooltipTriggerList = [].slice.call(
    document.querySelectorAll('[data-bs-toggle="tooltip"]')
  );
  var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });
})(jQuery);
