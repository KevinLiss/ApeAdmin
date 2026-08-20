function filterHTML(strInput){
    strInput = strInput.replace(new RegExp(['<'],"g"), "&lt;");
    strInput = strInput.replace(new RegExp(['>'],"g"), "&gt;");
    return strInput;
}
$(function(){
    $(".button-text").keyup(function(){
        var btnText = $(this).val();
        if($("#result a.btn, #result button.btn").length){
            if($("#result a.btn span, #result button.btn span").length){
                var iconCode = $("#result a.btn span, #result button.btn span").clone();
                innerCode = btnText;
                $("#result .btn").html(filterHTML(btnText));
                $("#result .btn").prepend(" ");
                $("#result .btn").prepend(iconCode);
                var btnHTML = $("#result").html();
                $(".button-html").html(filterHTML(btnHTML));
            }
            else{
                $("#result .btn").html(filterHTML(btnText));
                var btnHTML = $("#result").html();
                $(".button-html").html(filterHTML(btnHTML));
            }
        }
        else if($("#result input.btn").length){
            $("#result .btn").attr("value", filterHTML(btnText));
            var btnHTML = $("#result").html();
            $(".button-html").html(filterHTML(btnHTML));
        }
    });
    $(".button-color label").click(function(){
        var btnColor = $(this).children("input").attr("value");
        var btnSize = $(".button-size label.active").children("input").attr("value");
        var btnState = $(".button-state label.active").children("input").attr("value");
        var btnWidth = $(".button-width label.active").children("input").attr("value");
        if(btnState == "active" || btnState == "disabled"){
            var className = btnColor + " " + btnSize + " " + btnState;
            if(btnWidth.length){
                var className = btnColor + " " + btnSize + " " + btnState + " " + btnWidth;
            }
            $("#result .btn").attr("class", className);
            var btnHTML = $("#result").html();
            $(".button-html").html(filterHTML(btnHTML));
        }
        if(btnState == "normal"){
            var className = btnColor + " " + btnSize;
            if(btnWidth.length){
                var className = btnColor + " " + btnSize + " " + btnWidth;
            }
            $("#result .btn").attr("class", className);
            var btnHTML = $("#result").html();
            $(".button-html").html(filterHTML(btnHTML));
        }
    });
    $(".button-size label").click(function(){
        var btnSize = $(this).children("input").attr("value");
        var btnColor = $(".button-color label.active").children("input").attr("value");
        var btnState = $(".button-state label.active").children("input").attr("value");
        var btnWidth = $(".button-width label.active").children("input").attr("value");
        if(btnSize.length){
            if(btnState == "active" || btnState == "disabled"){
                var className = btnColor + " " + btnSize + " " + btnState;
                if(btnWidth.length){
                    var className = btnColor + " " + btnSize + " " + btnState + " " + btnWidth;
                }
                $("#result .btn").attr("class", className);
                var btnHTML = $("#result").html();
                $(".button-html").html(filterHTML(btnHTML));
            }
            if(btnState == "normal"){
                var className = btnColor + " " + btnSize;
                if(btnWidth.length){
                    var className = btnColor + " " + btnSize + " " + btnWidth;
                }
                $("#result .btn").attr("class", className);
                var btnHTML = $("#result").html();
                $(".button-html").html(filterHTML(btnHTML));
            }
        }
        else{
            if(btnState == "active" || btnState == "disabled"){
                var className = btnColor + " " + btnState;
                if(btnWidth.length){
                    var className = btnColor + " " + btnState + " " + btnWidth;
                }
                $("#result .btn").attr("class", className);
                var btnHTML = $("#result").html();
                $(".button-html").html(filterHTML(btnHTML));
            }
            if(btnState == "normal"){
                var className = btnColor;
                if(btnWidth.length){
                    var className = btnColor + " " + btnWidth;
                }
                $("#result .btn").attr("class", className);
                var btnHTML = $("#result").html();
                $(".button-html").html(filterHTML(btnHTML));
            }
        }
        $("#result .btn").attr("class", className);
        var btnHTML = $("#result").html();
        $(".button-html").html(filterHTML(btnHTML));
    });
    $(".element-type label").click(function(){
        var iconCode = "";
        var currentClass = $("#result .btn").attr("class");
        if($("#result a.btn span").length){
            var iconCode = $("#result a.btn span, #result button.btn span").clone();
        }
        if($("#result a.btn span").length === 0 && $('.include-icon label.active input').val() == 1){
            var iconName = $(".the-icons li.active span").attr("class");
            iconCode = '<span class="'+iconName+ '"></span>';
        }
        if($("#result a.btn, #result button.btn").length){
            var btnStr = $("#result .btn").text();
            var btnText = $.trim(btnStr);
        }
        else if($("#result input.btn").length){
            var btnStr = $("#result .btn").attr("value");
            var btnText = $.trim(btnStr);
        }
        if($(this).children("input").attr("value")=="a"){
            $("#result").empty();
            var btnCode = '<a href="javascript:void(0)"' + " " + 'class="' + currentClass + '">' + btnText + '</a>';
            $("#result a").remove();
            $("#result").append(btnCode);
            if(iconCode.length){
                if($('.fa-position label.active input').val() == "left"){
                    $("#result .btn").prepend(" ");
                    $("#result .btn").prepend(iconCode);
                }
                if($('.fa-position label.active input').val() == "right"){
                    $("#result .btn").append(" ");
                    $("#result .btn").append(iconCode);
                }
            }
            var btnHTML = $("#result").html();
            $(".button-html").html(filterHTML(btnHTML));
            if($(".include-icon label.active").children("input").attr("value")=="1"){
                $(".toggle").add("#iconOption").show();
            }
            if($(".include-icon label.active").children("input").attr("value")=="0"){
                $("#iconOption").show();
            }
        }
        else if($(this).children("input").attr("value")=="button"){
            $("#result").empty();
            var btnCode = '<button type="button"' + " " + 'class="' + currentClass + '">' + btnText + '</button>';
            $("#result button").remove();
            $("#result").append(btnCode);
            if(iconCode.length){
                if($('.fa-position label.active input').val() == "left"){
                    $("#result .btn").prepend(" ");
                    $("#result .btn").prepend(iconCode);
                }
                if($('.fa-position label.active input').val() == "right"){
                    $("#result .btn").append(" ");
                    $("#result .btn").append(iconCode);
                }
            }
            var btnHTML = $("#result").html();
            $(".button-html").html(filterHTML(btnHTML));
            if($(".include-icon label.active").children("input").attr("value")=="1"){
                $(".toggle").add("#iconOption").show();
            }
            if($(".include-icon label.active").children("input").attr("value")=="0"){
                $("#iconOption").show();
            }
        }
        else if($(this).children("input").attr("value")=="input"){
            $("#result").empty();
            var btnCode = '<input type="button"' + " " + 'class="' + currentClass + '" value="' + btnText + '">';
            $("#result button").remove();
            $("#result").append(btnCode);
            // Only applicable for input case
            $(".button-html").html(filterHTML(btnCode));
            $(".toggle").add("#iconOption").hide();
        }
        else if($(this).children("input").attr("value")=="submit"){
            $("#result").empty();
            var btnCode = '<input type="submit"' + " " + 'class="' + currentClass + '" value="' + btnText + '">';
            $("#result button").remove();
            $("#result").append(btnCode);
            var btnHTML = $("#result").html();
            $(".button-html").html(filterHTML(btnHTML));
        }
    });
    $(".button-state label").click(function(){
        if($(this).children("input").attr("value")=="active"){
            if($("#result a.btn").length){
                if($("#result a.disabled").length){
                    $("#result a.btn").removeClass("disabled");
                    $("#result a.btn").addClass("active");
                    var btnHTML = $("#result").html();
                    $(".button-html").html(filterHTML(btnHTML));
                }
                else{
                    $("#result a.btn").addClass("active");
                    var btnHTML = $("#result").html();
                    $(".button-html").html(filterHTML(btnHTML));
                }
            }
            if($("#result button.btn, #result input.btn").length){
                if($("#result button.disabled, #result input.disabled").length){
                    $("#result button.btn, #result input.btn").removeClass("disabled");
                    //$("#result button.btn, #result input.btn").removeAttr("disabled");
                    $("#result button.btn, #result input.btn").addClass("active");
                    var btnHTML = $("#result").html();
                    $(".button-html").html(filterHTML(btnHTML));
                }
                else{
                    $("#result button.btn, #result input.btn").addClass("active");
                    var btnHTML = $("#result").html();
                    $(".button-html").html(filterHTML(btnHTML));
                }
            }
        }
        if($(this).children("input").attr("value")=="disabled"){
            if($("#result a.btn").length){
                if($("#result a.active").length){
                    $("#result a.btn").removeClass("active");
                    $("#result a.btn").addClass("disabled");
                    var btnHTML = $("#result").html();
                    $(".button-html").html(filterHTML(btnHTML));
                }
                else{
                    $("#result a.btn").addClass("disabled");
                    var btnHTML = $("#result").html();
                    $(".button-html").html(filterHTML(btnHTML));
                }
            }
            if($("#result button.btn, #result input.btn")){
                if($("#result button.active, #result input.active").length){
                    $("#result button.btn, #result input.btn").removeClass("active");
                    $("#result button.btn, #result input.btn").addClass("disabled");
                    //$("#result button.btn, #result input.btn").attr("disabled","disabled");
                    var btnHTML = $("#result").html();
                    $(".button-html").html(filterHTML(btnHTML));
                }
                else{
                    $("#result button.btn, #result input.btn").addClass("disabled");
                    //$("#result button.btn, #result input.btn").attr("disabled","disabled");
                    var btnHTML = $("#result").html();
                    $(".button-html").html(filterHTML(btnHTML));
                }
            }
        }
        if($(this).children("input").attr("value")=="normal"){
            if($("#result .btn.active").length){
                $("#result .btn").removeClass("active");
                var btnHTML = $("#result").html();
                $(".button-html").html(filterHTML(btnHTML));
            }
            if($("#result .btn.disabled").length){
                $("#result .btn").removeClass("disabled");
                //$("#result .btn").removeAttr("disabled");
                var btnHTML = $("#result").html();
                $(".button-html").html(filterHTML(btnHTML));
            }
        }
    });
    $(".button-width label").click(function(){
        if($(this).children("input").attr("value")==""){
            if($("#result .btn").hasClass("btn-block")){
                $("#result .btn").removeClass("btn-block");
                var btnHTML = $("#result").html();
                $(".button-html").html(filterHTML(btnHTML));
            }
        }
        if($(this).children("input").attr("value")=="btn-block"){
            if(!$("#result .btn").hasClass("btn-block")){
                $("#result .btn").addClass("btn-block");
                var btnHTML = $("#result").html();
                $(".button-html").html(filterHTML(btnHTML));
            }
        }
    });
    $(".the-icons li").click(function(){
        $(".the-icons li").removeClass("active");
        $(this).addClass("active");
        if($('.include-icon label.active input').val() == 1){
            if($("#result .btn span").length){
                var iconClass = $(this).children("span").attr("class");
                iconCode = ' <span class="'+iconClass+'"></span> ';
                //alert(iconCode);
                $("#result .btn span").remove();
                if($('.fa-position label.active input').val() == "left"){
                    $("#result .btn").prepend(iconCode);
                }
                if($('.fa-position label.active input').val() == "right"){
                    $("#result .btn").append(iconCode);
                }
                var btnHTML = $("#result").html();
                $(".button-html").html(filterHTML(btnHTML));
            }
        }
    });
    $('.include-icon label').click(function(){
        if($(this).children("input").attr("value") == 0){
            if($("#result .btn span").length){
                var btnStr = $("#result .btn").text();
                var btnText = $.trim(btnStr);
                $("#result .btn").html(btnText);
                var btnHTML = $("#result").html();
                $(".button-html").html(filterHTML(btnHTML));
            }
            $(".toggle").hide();
        }
        if($(this).children("input").attr("value") == 1){
            $(".toggle").show();
            var iconName = $(".the-icons li.active span").attr("class");
            iconCode = '<span class="'+iconName+ '"></span>';
            if(iconCode.length){
                if($('.fa-position label.active input').val() == "left"){
                    $("#result .btn").prepend(" ");
                    $("#result .btn").prepend(iconCode);
                }
                if($('.fa-position label.active input').val() == "right"){
                    $("#result .btn").append(" ");
                    $("#result .btn").append(iconCode);
                }
                var btnHTML = $("#result").html();
                $(".button-html").html(filterHTML(btnHTML));
            }
        }

    });
    $(".fa-position label").click(function(){
        if($(this).children("input").attr("value") == "left"){
            if($("#result .btn span").length){
                var iconCode = $("#result .btn span").clone();
                var btnStr = $("#result .btn").text();
                var btnText = $.trim(btnStr);
                $("#result .btn").html(iconCode);
                $("#result .btn").append(" ");
                $("#result .btn").append(btnText);
                var btnHTML = $("#result").html();
                $(".button-html").html(filterHTML(btnHTML));
            }

        }
        if($(this).children("input").attr("value") == "right"){
            if($("#result .btn span").length){
                var iconCode = $("#result .btn span").clone();
                var btnStr = $("#result .btn").text();
                var btnText = $.trim(btnStr);
                $("#result .btn").html(iconCode);
                $("#result .btn").prepend(" ");
                $("#result .btn").prepend(btnText);
                var btnHTML = $("#result").html();
                $(".button-html").html(filterHTML(btnHTML));
            }
        }

    });
    $(".the-icons li").each(function(){
        var iconName = $(this).text().trim();
        $(this).attr("title",iconName);
    });
    $(".the-icons li").tooltip();

    //Print Button HTML
    $(".print-html").click(function(){
        var btnHTML = $("#result").html();
        alert(filterHTML(btnHTML));
        $(".button-html").html(filterHTML(btnHTML));
    });
});