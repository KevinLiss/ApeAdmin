(function($) {
    "use strict";
    $('.icon-lists .d-flex').click( function() {

        $(".fa-fa-icon-show-div").show().removeClass('opecity-0');
        
        // for icon
        var svg_icon = $(this).html();
        $(".icon-first").html(svg_icon);

        // for data feather title
        var feather_name = $(this).children().children("h6").html();
        $("#fclass1").html(feather_name);
        
         // for data value
        var fafaclass1= '<i data-feather="'+ feather_name + '"></i>';
        $(".inp-val").val(fafaclass1);

    });
    $(".close-icon").click(function(){
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
