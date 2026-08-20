(function ($) {
  "use strict";
  $(".icon-lists div").on('click', function() {
    $(".icon-lists").addClass("m-b-50");
    $(".icons-show-div").show();
    $(".icons-show-div").removeClass("opecity-0");
    var svg_icon = $(this).html();
    $(".icon-first").html(svg_icon);
    $(".inp-val").val(svg_icon);
  });
  $(".close-icon").on('click', function() {
    $(".icon-hover-bottom").addClass("opecity-0");
    $(".icons-show-div").hide();
    $(".icon-lists").removeClass("m-b-50");
  });
})(jQuery);
function myFunction() {
  var copyText = document.getElementById("input_copy");
  copyText.select();
  document.execCommand("Copy");
}
