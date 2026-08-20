(function ($) {
  function testAnim(x) {
    $(".modal .modal-dialog").attr(
      "class",
      "modal-dialog  " + x + "  animated"
    );
  }
  var modal_animate_custom = {
    init: function () {
      $("#myModal").on("show.bs.modal", function (e) {
        var anim = $("#entrance").val();
        testAnim(anim);
      });
      $("#myModal").on("hide.bs.modal", function (e) {
        var anim = $("#exit").val();
        testAnim(anim);
      });
    },
  };
  modal_animate_custom.init();
})(jQuery);
