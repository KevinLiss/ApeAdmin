(function ($) {
  "use strict";
  function testAnim(x) {
    $("#animation-box")
      .removeClass()
      .addClass(x + " animated")
      .one(
        "webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend",
        function () {
          $(this).removeClass();
        }
      );
  }
  var animate_custom = {
    init: function () {
      $(".js-triggeraNimation").on('click', function (e) {
        e.preventDefault();
        var anim = $(".js-animations").val();
        testAnim(anim);
      });
      $(".js-animations").change(function () {
        var anim = $(this).val();
        testAnim(anim);
      });
    },
  };
  animate_custom.init();
})(jQuery);
