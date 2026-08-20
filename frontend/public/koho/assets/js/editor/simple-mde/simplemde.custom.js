
// first demo of simple mde
(function($) {
    id = "editable";
    var simplemde = new SimpleMDE({
        element: $("textarea#" + id)[0]
    });
    toolbarInitialTop = $('.editor-toolbar').offset().top;
    toolbarOuterHeight = $('.editor-toolbar').outerHeight();
    toolbarFixedTop = 0;
    cmPaperTop = toolbarFixedTop + toolbarOuterHeight;
    toolbarAffixAt = toolbarInitialTop - toolbarFixedTop;
    $(document).scroll(fnAffix);
    $(document).resize(fnSetWidth);
    function fnAffix() {
        // Fix toolbar at set distance from top
        // and adjust toolbar width
        if ($(document).scrollTop() > toolbarAffixAt) {
            $('.editor-toolbar').addClass('toolbar-fixed');
            $('.editor-toolbar').css({'top': toolbarFixedTop + 'px'});
            $('.CodeMirror.cm-s-paper.CodeMirror-wrap').css({'top': cmPaperTop + 'px'});
            fnSetWidth();
        }
        else {
            $('.editor-toolbar').removeClass('toolbar-fixed');
            $('.CodeMirror.cm-s-paper.CodeMirror-wrap').css({'top': ''});
        }
    }
    function fnSetWidth() {
        // Adjust fixed toolbar width to the width of CodeMirror
        $('.toolbar-fixed').width($('.CodeMirror.cm-s-paper.CodeMirror-wrap').width());
    }
})(jQuery);

// second demo of simple mde
var sample = [
    "### Instructions",
    "Enter text in the area on the left. For more info, click the ? (help) icon in the menu."
]
var simplemde = new SimpleMDE({element: $("#smde")[0], toolbar: ["bold", "italic", "heading", "|", "quote", "unordered-list", "ordered-list", "|", "link", "image", "|", "guide"]});
$(document).ready(function() {
    writeSample();
    simplemde.codemirror.on("change", function(){
        var renderedHTML = simplemde.options.previewRender(simplemde.value());
        $("#write_here").html(renderedHTML);
        $("#write_here").css("height", $(".row").height() +  "px" );
    });
});
function writeSample() {
    var s = "";
    s = getSample();
    simplemde.value(s);
    var renderedHTML = simplemde.options.previewRender(simplemde.value());
    $("#write_here").html(renderedHTML);
    $("#write_here").css("height", $(".row").height() +  "px" );
}
function getSample() {
    var s = "";
    $.each(sample, function( index, value ) {
        //alert( index + ": " + value );
        s = s + value + "\n\r";
    });
    return s;
}