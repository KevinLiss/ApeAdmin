(function($) {
    "use strict";
    $('.icon-lists div').on('click', function() {
        $(".icon-lists").addClass('m-b-50');
        $(".fa-fa-icon-show-div").show();
        $(".fa-fa-icon-show-div").removeClass('opecity-0');
        var font_class = ($(this).children().attr('class'));
        var fafaclass= '&lt;i class="'+ font_class + '"&gt';
        var fafaclass1= '<i class="'+ font_class + '"></i>';
        $("#fclass").html(fafaclass);
        $("#fclass1").html(font_class);
        $("#icon_main").removeClass();
        $("#icon_main").addClass(font_class);
        $("#icon_main").addClass("fa-2x");
        $(".inp-val").val(fafaclass1);
    });
    $(".close-icon").on('click', function() {
        $(".icon-hover-bottom").addClass("opecity-0");
        $(".fa-fa-icon-show-div").hide();
        $(".icon-lists").removeClass('m-b-50');
    });
})(jQuery);
function myFunction() {
    var copyText = document.getElementById("input_copy");
    copyText.select();
    document.execCommand("Copy");
};