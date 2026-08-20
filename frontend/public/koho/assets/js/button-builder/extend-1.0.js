"use strict";
function customRadio(radioName){
    var radioButton = $('input[name="'+ radioName +'"]');
    $(radioButton).each(function(){
        $(this).wrap( "<span class='custom-radio'></span>" );
        if($(this).is(':checked')){
            $(this).parent().addClass("selected");
        }
    });
    $(radioButton).click(function(){
        if($(this).is(':checked')){
            $(this).parent().addClass("selected");
        }
        $(radioButton).not(this).each(function(){
            $(this).parent().removeClass("selected");
        });
    });
}
function customCheckbox(checkboxName){
    var checkBox = $('input[name="'+ checkboxName +'"]');
    $(checkBox).each(function(){
        $(this).wrap( "<span class='custom-checkbox'></span>" );
        if($(this).is(':checked')){
            $(this).parent().addClass("selected");
        }
    });
    $(checkBox).click(function(){
        $(this).parent().toggleClass("selected");
    });
}
function setColor(){
    // Getting current color values
    var btnSelector = "";
    var resultButton = $("#result").children("a, input, button");
    var btnClass = resultButton.attr("class");
    var btnClass = btnClass.replace("  "," ");
    var strTrim = $.trim(btnClass);
    var btnSelector = "." + strTrim.split(" ").join('.');
    
    //alert(btnClass);
    if(resultButton.hasClass("btn-xs")){
        var classStr = btnClass.replace(" btn-xs","");
        var strTrim = $.trim(classStr);
        var btnSelector = "." + strTrim.split(" ").join('.');
    }
    if(resultButton.hasClass("btn-sm")){
        var classStr = btnClass.replace(" btn-sm","");
        var strTrim = $.trim(classStr);
        var btnSelector = "." + strTrim.split(" ").join('.');
    }
    if(resultButton.hasClass("btn-lg")){
        var classStr = btnClass.replace(" btn-lg","");
        var strTrim = $.trim(classStr);
        var btnSelector = "." + strTrim.split(" ").join('.');
    }
    if(resultButton.hasClass("btn-block")){
        var btnSelector = btnSelector.replace(".btn-block","");
    }
    
    //alert(btnSelector);
    
    // Default button style
    if(btnSelector == ".btn.btn-default" || btnSelector == ".btn.btn-default.disabled"){
        $("#textColor").val("333333");
        $("#bgColor").val("FFFFFF");
        $("#topColor").val("FFFFFF");
        $("#bottomColor").val("E0E0E0");            
        $("#borderTopColor").val("CCCCCC");
        $("#borderHrColor").val("CCCCCC");
        $("#borderBottomColor").val("CCCCCC");
    }
    if(btnSelector == ".btn.btn-default.active"){
        $("#textColor").val("333333");
        $("#bgColor").val("E0E0E0");
        $("#topColor").val("E0E0E0");
        $("#bottomColor").val("E0E0E0");            
        $("#borderTopColor").val("DBDBDB");
        $("#borderHrColor").val("DBDBDB");
        $("#borderBottomColor").val("DBDBDB");
    }
    
    // Primary button style
    if(btnSelector == ".btn.btn-primary" || btnSelector == ".btn.btn-primary.disabled"){
        $("#textColor").val("ffffff");
        $("#bgColor").val("428BCA");
        $("#topColor").val("428BCA");
        $("#bottomColor").val("2D6CA2");                    
        $("#borderTopColor").val("2B669A");
        $("#borderHrColor").val("2B669A");
        $("#borderBottomColor").val("2B669A");
    }
    if(btnSelector == ".btn.btn-primary.active"){
        $("#textColor").val("ffffff");
        $("#bgColor").val("2D6CA2");
        $("#topColor").val("2D6CA2");
        $("#bottomColor").val("2D6CA2");
        $("#borderTopColor").val("2B669A");
        $("#borderHrColor").val("2B669A");
        $("#borderBottomColor").val("2B669A");
    }
    
    // Info button style
    if(btnSelector == ".btn.btn-info"  || btnSelector == ".btn.btn-info.disabled"){
        $("#textColor").val("ffffff");
        $("#bgColor").val("5BC0DE");
        $("#topColor").val("5BC0DE");
        $("#bottomColor").val("2AABD2");                    
        $("#borderTopColor").val("28A4C9");
        $("#borderHrColor").val("28A4C9");
        $("#borderBottomColor").val("28A4C9");
    }
    if(btnSelector == ".btn.btn-info.active"){
        $("#textColor").val("ffffff");
        $("#bgColor").val("2AABD2");
        $("#topColor").val("2AABD2");
        $("#bottomColor").val("2AABD2");                    
        $("#borderTopColor").val("28A4C9");
        $("#borderHrColor").val("28A4C9");
        $("#borderBottomColor").val("28A4C9");
    }
    
    // Success button style
    if(btnSelector == ".btn.btn-success" || btnSelector == ".btn.btn-success.disabled"){
        $("#textColor").val("ffffff");
        $("#bgColor").val("00c292");
        $("#topColor").val("00c292");
        $("#bottomColor").val("00ebb1");
        $("#borderTopColor").val("00c292");
        $("#borderHrColor").val("00c292");
        $("#borderBottomColor").val("00c292");
    }
    if(btnSelector == ".btn.btn-success.active"){
        $("#textColor").val("ffffff");
        $("#bgColor").val("00ebb1");
        $("#topColor").val("00ebb1");
        $("#bottomColor").val("00ebb1");                    
        $("#borderTopColor").val("00c292");
        $("#borderHrColor").val("00c292");
        $("#borderBottomColor").val("00c292");
    }
    
    // Warning button style
    if(btnSelector == ".btn.btn-warning" || btnSelector == ".btn.btn-warning.disabled"){
        $("#textColor").val("ffffff");
        $("#bgColor").val("F0AD4E");
        $("#topColor").val("F0AD4E");
        $("#bottomColor").val("EB9316");                    
        $("#borderTopColor").val("E38D13");
        $("#borderHrColor").val("E38D13");
        $("#borderBottomColor").val("E38D13");
    }
    if(btnSelector == ".btn.btn-warning.active"){
        $("#textColor").val("ffffff");
        $("#bgColor").val("EB9316");
        $("#topColor").val("EB9316");
        $("#bottomColor").val("EB9316");                    
        $("#borderTopColor").val("E38D13");
        $("#borderHrColor").val("E38D13");
        $("#borderBottomColor").val("E38D13");
    }
    
    // Danger button style
    if(btnSelector == ".btn.btn-danger" || btnSelector == ".btn.btn-danger.disabled"){
        $("#textColor").val("ffffff");
        $("#bgColor").val("D9534F");
        $("#topColor").val("D9534F");
        $("#bottomColor").val("C12E2A");                    
        $("#borderTopColor").val("B92C28");
        $("#borderHrColor").val("B92C28");
        $("#borderBottomColor").val("B92C28");
    }
    if(btnSelector == ".btn.btn-danger.active"){
        $("#textColor").val("ffffff");
        $("#bgColor").val("C12E2A");
        $("#topColor").val("C12E2A");
        $("#bottomColor").val("C12E2A");                    
        $("#borderTopColor").val("B92C28");
        $("#borderHrColor").val("B92C28");
        $("#borderBottomColor").val("B92C28");
    }
    
    // Setting background of color selector
    $(".custom-button-color input").each(function(){
        var colorValue = $(this).val();
        //alert(colorValue);
        $(this).next(".color-slelector").css("background", "#"+colorValue);
    });
    
    var txtColor = $("#textColor").val();
    var bgColor = $("#bgColor").val();
    var topColor = $("#topColor").val();
    var bottomColor = $("#bottomColor").val();            
    var borderTopColor = $("#borderTopColor").val();
    var borderHrColor = $("#borderHrColor").val();
    var borderBottomColor = $("#borderBottomColor").val();
    
    var btnBg = "background-color: " + "#" + bgColor + ";";            
    var btnGradient = "background-image: linear-gradient(to bottom, " + "#" + topColor + "," + " " + "#" + bottomColor + ");";
    var btnBgPosition = "background-position: 0 0;";
    var btnText = "color: " + "#" + txtColor + ";";
    var btnBorder = "border-color: " + "#" + borderTopColor + " " + "#" + borderHrColor + " " + "#" + borderBottomColor +";";
    
    var btnBgHover = "background-color: " + "#" + bottomColor + ";";
    var btnGradientHover = "background-image: linear-gradient(to bottom, " + "#" + bottomColor + "," + " " + "#" + bottomColor + ");";
    
    // Setting CSS
    var resultButton = $("#result").find("a, input, button");
    
    if(resultButton.hasClass("active") || resultButton.hasClass("disabled")){
        //alert(btnSelector);
        var btnStyle = "<style type='text/css'>" + "#result" + " " + btnSelector + "," + " " + "#result" + " " + btnSelector + ":hover {" + btnText + " " + btnBg + " " + btnGradient + " " + btnBgPosition + " " + btnBorder + "}</style>";
        
        var btnCSS = btnSelector + "," + " " + "\n" + btnSelector + ":hover {\n" + "&nbsp;&nbsp;&nbsp;&nbsp;"+ btnText + "\n" + "&nbsp;&nbsp;&nbsp;&nbsp;"+ btnBg + "\n" + "&nbsp;&nbsp;&nbsp;&nbsp;"+ btnGradient + "\n" + "&nbsp;&nbsp;&nbsp;&nbsp;"+btnBgPosition + "\n" + "&nbsp;&nbsp;&nbsp;&nbsp;"+ btnBorder + "\n}";
        
        $("style").remove();
        $(btnStyle).appendTo("head");
        $(".button-css").empty();
        $(".button-css").html(btnCSS);
    }
    else{
        //alert(btnSelector);
        var btnStyle = "<style type='text/css'>" + "#result" + " " + btnSelector + " {" + btnText + " " + btnBg + " " + btnGradient + " " + btnBorder + "}" + "#result" + " " + btnSelector + ":hover {" + btnText + " " + btnBgHover + " " + btnGradientHover + " " + btnBorder + "}" + "</style>";
    
        var btnCSS = btnSelector + " {\n" + "&nbsp;&nbsp;&nbsp;&nbsp;"+ btnText + "\n" + "&nbsp;&nbsp;&nbsp;&nbsp;"+ btnBg + "\n" + "&nbsp;&nbsp;&nbsp;&nbsp;"+ btnGradient + "\n" + "&nbsp;&nbsp;&nbsp;&nbsp;"+ btnBorder + "\n}\n" + btnSelector + ":hover {\n" + "&nbsp;&nbsp;&nbsp;&nbsp;"+ btnText + "\n" + "&nbsp;&nbsp;&nbsp;&nbsp;"+ btnBgHover + "\n" + "&nbsp;&nbsp;&nbsp;&nbsp;"+ btnGradientHover + "\n" + "&nbsp;&nbsp;&nbsp;&nbsp;"+ btnBorder + "\n}";
        
        $("style").remove();
        $(btnStyle).appendTo("head");
        $(".button-css").empty();
        $(".button-css").html(btnCSS);
    }
}
(function($) {
    "use strict";
    customRadio("color-option");
    customCheckbox("border-all");
    setColor();
    
    // Show hide border options
    $('.border-all input[type="checkbox"]').each(function(){
        if($(this).prop('checked') == true){ 
            var borderTopColor = $("#borderTopColor").val();
            $("#borderHrColor").val(borderTopColor);
            $("#borderBottomColor").val(borderTopColor);
            $("#borderHrColor, #borderBottomColor").next(".color-slelector").css("background", "#"+borderTopColor);
            $(".border-color-separate").hide();
            $(this).parents(".controls").prev().text("Border Color");
        }
        if($(this).prop('checked') == false){
            $(".border-color-separate").show();
            $(this).parents(".controls").prev().text("Border Top Color");
        }
    });
    $('.border-all, .border-all input[type="checkbox"]').click(function(){
        if($(this).prop('checked') == true){ 
            var borderTopColor = $("#borderTopColor").val();
            $("#borderHrColor").val(borderTopColor);
            $("#borderBottomColor").val(borderTopColor);
            $("#borderHrColor, #borderBottomColor").next(".color-slelector").css("background", "#"+borderTopColor);
            $(".border-color-separate").hide();
            $(this).parents(".controls").prev().text("Border Color");
        }
        if($(this).prop('checked') == false){
            $(".border-color-separate").show();
            $(this).parents(".controls").prev().text("Border Top Color");
        }
    });
    
	// HTML copy to clipboard
    var copyHTML = new Clipboard("#copyHTML");

    copyHTML.on("success", function(e) {
        $("#htmlAlert").fadeIn("fast").delay(500).queue(function() {
            $(this).fadeOut("fast");
            $(this).dequeue();
        });  
    });
    
    // HTML copy to clipboard
    var copyCSS = new Clipboard("#copyCSS");

    copyCSS.on("success", function(e) {
        $("#cssAlert").fadeIn("fast").delay(500).queue(function() {
            $(this).fadeOut("fast");
            $(this).dequeue();
        }); 
    });
    
    // Show hide icon option
    $('.element-type button[value="a"]').click(function(){
        $("#iconOption").show();
        $(".include-icon button").each(function(){
            if($('button[value="1"]').hasClass("active")){
                $(".toggle").show();
            }
            if($('button[value="0"]').hasClass("active")){
                $(".toggle").hide();
            }
        });
    });
    $('.element-type button[value="button"]').click(function(){
        $("#iconOption").show();
        $(".include-icon button").each(function(){
            if($('button[value="1"]').hasClass("active")){
                $(".toggle").show();
            }
            if($('button[value="0"]').hasClass("active")){
                $(".toggle").hide();
            }
        });
    });
    $('.element-type button[value="input"]').click(function(){
        $("#iconOption, .toggle").hide();
    });
    
    // Show hide color option
    $('.button-color-option input[type="radio"]').each(function(){
        if($(this).is(':checked')){
            if($(this).attr("value")=="bootstrap"){
                $(".custom-button-color").hide();
                $(".bootstrap-inbuilt-style").show();
                $(".wrapper").removeClass("adjust");
                $("#cssBox").hide();
                $("style").remove();
            }
            if($(this).attr("value")=="custom"){
                $(".bootstrap-inbuilt-style").hide();
                $(".custom-button-color").show();
                $(".wrapper").addClass("adjust");
                $("#cssBox").show();
                setColor();
            }
        }
    });
    $('.button-color-option input[type="radio"]').click(function(){
        if($(this).attr("value")=="bootstrap"){
            $(".custom-button-color").hide();                
            $(".bootstrap-inbuilt-style").show();
            $(".wrapper").removeClass("adjust");
            $("#cssBox").hide();
            $("style").remove();
        }
        if($(this).attr("value")=="custom"){
            $(".bootstrap-inbuilt-style").hide();
            $(".custom-button-color").show();
            $(".wrapper").addClass("adjust");
            $("#cssBox").show();
            setColor();
        }
    });
    
    var colorInput = $('#textColor, #topColor, #bottomColor, #bgColor, #borderTopColor, #borderHrColor, #borderBottomColor');
    $(colorInput).each(function(){
        var defautColor = $(this).val();
        //alert(defautColor);
        $(this).ColorPicker({
            color: defautColor,
            onSubmit: function(hsb, hex, rgb, el) {
                $(el).val(hex);
                $(el).ColorPickerHide();
            }
        })
        .bind('keyup', function(){
            $(this).ColorPickerSetColor(this.value);
        });
    });
    
    $(".colorpicker-submit").click(function(){
        $(".custom-button-color input").each(function(){
            var colorValue = $(this).val();
            //alert(colorValue);
            $(this).next(".color-slelector").css("background", "#"+colorValue);
            $(this).attr("value", colorValue);
        });
    });
    var colorSelector = $('#colorSelector1, #colorSelector2, #colorSelector3, #colorSelector4, #colorSelector5, #colorSelector6, #colorSelector7');
    $(colorSelector).each(function(){
        var selectorColor = $(this).prev().val();
        $(this).ColorPicker({
            color: selectorColor,
            onSubmit: function(hsb, hex, rgb, el) {
                $(el).val(hex);
                $(el).ColorPickerHide();
                $(el).css("background", "#"+hex);
                $(el).prev().val(hex);
            }
        }).bind('click', function(){
            var selectorColor = $(this).prev().val();
            $(this).ColorPickerSetColor(selectorColor);
        });
    });
    
    // Inserting CSS
    $('.colorpicker-submit, .button-state button, .border-all input[type="checkbox"]').click(function(){
        if($('.button-color-option input[value="custom"]').is(':checked')){
            
            // Getting current color values
            var btnSelector = "";
            var resultButton = $("#result").children("a, input, button");
            var btnClass = resultButton.attr("class");
            var strTrim = $.trim(btnClass);
            var btnSelector = "." + strTrim.split(" ").join('.');
            
            //alert(btnClass);
            if(resultButton.hasClass("btn-xs")){
                var classStr = btnClass.replace(" btn-xs","");
                var strTrim = $.trim(classStr);
                var btnSelector = "." + strTrim.split(" ").join('.');
            }
            if(resultButton.hasClass("btn-sm")){
                var classStr = btnClass.replace(" btn-sm","");
                var strTrim = $.trim(classStr);
                var btnSelector = "." + strTrim.split(" ").join('.');
            }
            if(resultButton.hasClass("btn-lg")){
                var classStr = btnClass.replace(" btn-lg","");
                var strTrim = $.trim(classStr);
                var btnSelector = "." + strTrim.split(" ").join('.');
            }
            
            //alert(btnSelector);

            $('.border-all input[type="checkbox"]').each(function(){
                if($(this).is(':checked')){
                    var borderTopColor = $("#borderTopColor").val();
                    $("#borderHrColor").val(borderTopColor);
                    $("#borderBottomColor").val(borderTopColor);
                    $("#borderHrColor, #borderBottomColor").next(".color-slelector").css("background", "#"+borderTopColor);
                }
            });
            
            var txtColor = $("#textColor").val();
            var bgColor = $("#bgColor").val();
            var topColor = $("#topColor").val();
            var bottomColor = $("#bottomColor").val();            
            var borderTopColor = $("#borderTopColor").val();
            var borderHrColor = $("#borderHrColor").val();
            var borderBottomColor = $("#borderBottomColor").val();
            
            var btnBg = "background-color: " + "#" + bgColor + ";";            
            var btnGradient = "background-image: linear-gradient(to bottom, " + "#" + topColor + "," + " " + "#" + bottomColor + ");";
            var btnBgPosition = "background-position: 0 0;";
            var btnText = "color: " + "#" + txtColor + ";";
            var btnBorder = "border-color: " + "#" + borderTopColor + " " + "#" + borderHrColor + " " + "#" + borderBottomColor +";";
            
            var btnBgHover = "background-color: " + "#" + bottomColor + ";";
            var btnGradientHover = "background-image: linear-gradient(to bottom, " + "#" + bottomColor + "," + " " + "#" + bottomColor + ");";
            
            // Setting CSS
            var resultButton = $("#result").find("a, input, button");
            
            if(resultButton.hasClass("active") || resultButton.hasClass("disabled")){
                //alert(btnSelector);
                var btnStyle = "<style type='text/css'>" + "#result" + " " + btnSelector + "," + " " + "#result" + " " + btnSelector + ":hover {" + btnText + " " + btnBg + " " + btnGradient + " " + btnBgPosition + " " + btnBorder + "}</style>";
            
                var btnCSS = btnSelector + "," + " " + "\n" + btnSelector + ":hover {\n" + "&nbsp;&nbsp;&nbsp;&nbsp;"+ btnText + "\n" + "&nbsp;&nbsp;&nbsp;&nbsp;"+ btnBg + "\n" + "&nbsp;&nbsp;&nbsp;&nbsp;"+ btnGradient + "\n" + "&nbsp;&nbsp;&nbsp;&nbsp;"+btnBgPosition + "\n" + "&nbsp;&nbsp;&nbsp;&nbsp;"+ btnBorder + "\n}";
                
                $("style").remove();
                $(btnStyle).appendTo("head");
                $(".button-css").empty();
                $(".button-css").html(btnCSS);
            }
            else{
                //alert(btnSelector);
                var btnStyle = "<style type='text/css'>" + "#result" + " " + btnSelector + " {" + btnText + " " + btnBg + " " + btnGradient + " " + btnBorder + "}" + "#result" + " " + btnSelector + ":hover {" + btnText + " " + btnBgHover + " " + btnGradientHover + " " + btnBorder + "}" + "</style>";
            
                var btnCSS = btnSelector + " {\n" + "&nbsp;&nbsp;&nbsp;&nbsp;"+ btnText + "\n" + "&nbsp;&nbsp;&nbsp;&nbsp;"+ btnBg + "\n" + "&nbsp;&nbsp;&nbsp;&nbsp;"+ btnGradient + "\n" + "&nbsp;&nbsp;&nbsp;&nbsp;"+ btnBorder + "\n}\n" + btnSelector + ":hover {\n" + "&nbsp;&nbsp;&nbsp;&nbsp;"+ btnText + "\n" + "&nbsp;&nbsp;&nbsp;&nbsp;"+ btnBgHover + "\n" + "&nbsp;&nbsp;&nbsp;&nbsp;"+ btnGradientHover + "\n" + "&nbsp;&nbsp;&nbsp;&nbsp;"+ btnBorder + "\n}";
                
                $("style").remove();
                $(btnStyle).appendTo("head");
                $(".button-css").empty();
                $(".button-css").html(btnCSS);
            }
        }
    });
})(jQuery);