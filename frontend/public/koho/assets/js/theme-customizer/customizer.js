if (localStorage.getItem("color"))
  $("#color").attr(
    "href",
    "../assets/css/" + localStorage.getItem("color") + ".css"
  );
if (localStorage.getItem("dark")) $("body").attr("class", "dark-only");
$('<div class="customizer-links"> <div class="nav flex-column nac-pills" id="c-pills-tab" role="tablist" aria-orientation="vertical"> <a class="nav-link" id="c-pills-layouts-tab" data-bs-toggle="pill" href="#c-pills-layouts" role="tab" aria-controls="c-pills-layouts" aria-selected="true" data-original-title="" title=""> <div class="settings"><i class="icon-paint-bucket"></i></div></a> <a class="nav-link" id="c-pills-home-tab" data-bs-toggle="pill" href="#c-pills-home" role="tab" aria-controls="c-pills-home" aria-selected="true" data-original-title="" title=""> <div class="settings"><i class="icon-settings"></i></div></a> </div></div><div class="customizer-contain"> <div class="tab-content" id="c-pills-tabContent"> <div class="customizer-header"> <i class="icofont-close icon-close"></i> <h5>Preview Settings</h5> <p class="mb-0">Try It Real Time <i class="fa fa-thumbs-o-up txt-primary"></i></p></div><div class="customizer-body custom-scrollbar"> <div class="tab-pane fade show active" id="c-pills-home" role="tabpanel" aria-labelledby="c-pills-home-tab"> <h6>Layout Type</h6> <ul class="main-layout layout-grid"> <li data-attr="ltr" class="active ltr"> <div class="header bg-light"> <ul> <li></li><li></li><li></li></ul> </div><div class="body"> <ul> <li class="bg-light sidebar"></li><li class="bg-light body"><span class="badge badge-primary">LTR</span></li></ul> </div></li><li data-attr="rtl"> <div class="header bg-light"> <ul> <li></li><li></li><li></li></ul> </div><div class="body"> <ul> <li class="bg-light body"><span class="badge badge-primary">RTL</span></li><li class="bg-light sidebar"></li></ul> </div></li><li data-attr="ltr" class="box-layout px-3"> <div class="header bg-light"> <ul> <li></li><li></li><li></li></ul> </div><div class="body"> <ul> <li class="bg-light sidebar"></li><li class="bg-light body"><span class="badge badge-primary">Box</span></li></ul> </div></li></ul> <h6 class="">Sidebar Type</h6> <ul class="sidebar-type layout-grid"> <li data-attr="normal-sidebar"> <div class="header bg-light"> <ul> <li></li><li></li><li></li></ul> </div><div class="body"> <ul> <li class="bg-dark sidebar"></li><li class="bg-light body"></li></ul> </div></li><li data-attr="compact-sidebar"> <div class="header bg-light"> <ul> <li></li><li></li><li></li></ul> </div><div class="body"> <ul> <li class="bg-dark sidebar compact"></li><li class="bg-light body"></li></ul> </div></li></ul> </div><div class="tab-pane fade" id="c-pills-layouts" role="tabpanel" aria-labelledby="c-pills-layouts-tab"> <h6 class="">Unlimited Color</h6> <ul class="layout-grid unlimited-color-layout"> <input id="ColorPicker1" type="color" value="#5c61f2" name="Background"/> <input id="ColorPicker2" type="color" value="#eeb82f" name="Background"/> <button type="button" class="color-apply-btn btn btn-primary color-apply-btn">Apply</button> </ul> <h6>Light layout</h6> <ul class="layout-grid customizer-color"> <li class="color-layout" data-attr="color-1" data-primary="#5c61f2" data-secondary="#eeb82f"> <div></div></li><li class="color-layout" data-attr="color-2" data-primary="#3B7CF5" data-secondary="#F53467"> <div></div></li><li class="color-layout" data-attr="color-3" data-primary="#247164" data-secondary="#8C633F"> <div></div></li><li class="color-layout" data-attr="color-4" data-primary="#6655e9" data-secondary="#8e49dd"> <div></div></li><li class="color-layout" data-attr="color-5" data-primary="#167A93" data-secondary="#50606C"> <div></div></li><li class="color-layout" data-attr="color-6" data-primary="#7F563A" data-secondary="#44B3E6"> <div></div></li></ul> <h6 class="">Dark Layout</h6> <ul class="layout-grid customizer-color dark"> <li class="color-layout" data-attr="color-1" data-primary="#5c61f2" data-secondary="#eeb82f"> <div></div></li><li class="color-layout" data-attr="color-2" data-primary="#3B7CF5" data-secondary="#c7d3d4"> <div></div></li><li class="color-layout" data-attr="color-3" data-primary="#247164" data-secondary="#8C633F"> <div></div></li><li class="color-layout" data-attr="color-4" data-primary="#6655e9" data-secondary="#8e49dd"> <div></div></li><li class="color-layout" data-attr="color-5" data-primary="#167A93" data-secondary="#50606C"> <div></div></li><li class="color-layout" data-attr="color-6" data-primary="#7F563A" data-secondary="#f2edd7"> <div></div></li></ul> <h6 class="">Mix Layout</h6> <ul class="layout-grid customizer-mix"> <li class="color-layout active" data-attr="light-only"> <div class="header bg-light"> <ul> <li></li><li></li><li></li></ul> </div><div class="body"> <ul> <li class="bg-light sidebar"></li><li class="bg-light body"></li></ul> </div></li><li class="color-layout" data-attr="dark-only"> <div class="header bg-dark"> <ul> <li></li><li></li><li></li></ul> </div><div class="body"> <ul> <li class="bg-dark sidebar"></li><li class="bg-dark body"></li></ul> </div></li></ul> </div></div></div></div>').appendTo($('body'));
(function () {})();

//live customizer js
$(document).ready(function () {
  $(".customizer-color li").on("click", function () {
    $(".customizer-color li").removeClass("active");
    $(this).addClass("active");
    var color = $(this).attr("data-attr");
    var primary = $(this).attr("data-primary");
    var secondary = $(this).attr("data-secondary");
    localStorage.setItem("color", color);
    localStorage.setItem("primary", primary);
    localStorage.setItem("secondary", secondary);
    localStorage.removeItem("dark");
    $("#color").attr("href", "../assets/css/" + color + ".css");
    $(".dark-only").removeClass("dark-only");
    location.reload(true);
  });

  $(".customizer-color.dark li").on("click", function () {
    $(".customizer-color.dark li").removeClass("active");
    $(this).addClass("active");
    $("body").attr("class", "dark-only");
    localStorage.setItem("dark", "dark-only");
  });

  if (localStorage.getItem("primary") != null) {
    document.documentElement.style.setProperty(
      "--theme-default",
      localStorage.getItem("primary")
    );
  }
  if (localStorage.getItem("secondary") != null) {
    document.documentElement.style.setProperty(
      "--theme-secondary",
      localStorage.getItem("secondary")
    );
  }
  $(
    ".customizer-links #c-pills-home-tab, .customizer-links #c-pills-layouts-tab"
  ).click(function () {
    $(".customizer-contain").addClass("open");
    $(".customizer-links").addClass("open");
  });

  $(".close-customizer-btn").on("click", function () {
    $(".floated-customizer-panel").removeClass("active");
  });

  $(".customizer-contain .icon-close").on("click", function () {
    $(".customizer-contain").removeClass("open");
    $(".customizer-links").removeClass("open");
  });

  $(".color-apply-btn").click(function () {
    location.reload(true);
  });

  var primary = document.getElementById("ColorPicker1").value;
  document.getElementById("ColorPicker1").onchange = function () {
    primary = this.value;
    localStorage.setItem("primary", primary);
    document.documentElement.style.setProperty("--theme-primary", primary);
  };

  var secondary = document.getElementById("ColorPicker2").value;
  document.getElementById("ColorPicker2").onchange = function () {
    secondary = this.value;
    localStorage.setItem("secondary", secondary);
    document.documentElement.style.setProperty("--theme-secondary", secondary);
  };

  $(".customizer-color.dark li").on("click", function () {
    $(".customizer-color.dark li").removeClass("active");
    $(this).addClass("active");
    $("body").attr("class", "dark-only");
    localStorage.setItem("dark", "dark-only");
  });

  $(".customizer-mix li").on("click", function () {
    $(".customizer-mix li").removeClass("active");
    $(this).addClass("active");
    var mixLayout = $(this).attr("data-attr");
    $("body").attr("class", mixLayout);
  });

  $(".sidebar-setting li").on("click", function () {
    $(".sidebar-setting li").removeClass("active");
    $(this).addClass("active");
    var sidebar = $(this).attr("data-attr");
    $(".sidebar-wrapper").attr("sidebar-layout", sidebar);
  });

  $(".sidebar-main-bg-setting li").on("click", function () {
    $(".sidebar-main-bg-setting li").removeClass("active");
    $(this).addClass("active");
    var bg = $(this).attr("data-attr");
    $(".sidebar-wrapper").attr("class", "sidebar-wrapper " + bg);
  });

  $(".sidebar-type li").on("click", function () {
    $("body").append("");
    console.log("test");
    var type = $(this).attr("data-attr");

    var boxed = "";
    if ($(".page-wrapper").hasClass("box-layout")) {
      boxed = "box-layout";
    }
    switch (type) {
      case "normal-sidebar": {
        $(".page-wrapper").attr(
          "class",
          "page-wrapper horizontal-wrapper " + boxed
        );
        $(".logo-wrapper")
          .find("img")
          .attr("src", "../assets/images/logo/logo.png");
        localStorage.setItem("page-wrapper", "horizontal-wrapper");
        break;
      }
      case "default-body": {
        $(".page-wrapper").attr("class", "page-wrapper  only-body" + boxed);
        localStorage.setItem("page-wrapper", "only-body");
        break;
      }
      case "dark-sidebar": {
        $(".page-wrapper").attr(
          "class",
          "page-wrapper compact-wrapper dark-sidebar" + boxed
        );
        localStorage.setItem("page-wrapper", "compact-wrapper dark-sidebar");
        break;
      }
      case "compact-wrap": {
        $(".page-wrapper").attr(
          "class",
          "page-wrapper compact-sidebar" + boxed
        );
        localStorage.setItem("page-wrapper", "compact-sidebar");
        break;
      }
      case "box-layout": {
        $(".page-wrapper").attr(
          "class",
          "page-wrapper compact-wrapper box-layout " + boxed
        );
        localStorage.setItem("page-wrapper", "compact-wrapper box-layout");
        break;
      }
      default: {
        $(".page-wrapper").attr(
          "class",
          "page-wrapper compact-wrapper " + boxed
        );
        localStorage.setItem("page-wrapper", "compact-wrapper");
        break;
      }
    }
    location.reload(true);
  });

  $(".main-layout li").on("click", function () {
    $(".main-layout li").removeClass("active");
    $(this).addClass("active");
    var layout = $(this).attr("data-attr");
    $("body").attr("class", layout);
    $("html").attr("dir", layout);
  });

  $(".main-layout .box-layout").on("click", function () {
    $(".main-layout .box-layout").removeClass("active");
    $(".sidebar-wrapper").addClass("close_icon");
    $(".page-header").addClass("close_icon");
    $(this).addClass("active");
    var layout = $(this).attr("data-attr");
    $("body").attr("class", "box-layout");
    $("html").attr("dir", layout);
    $(window).resize(function () {   
      $(".main-layout .box-layout").removeClass('active');
      $(".sidebar-wrapper").addClass("close_icon");
      $(".page-header").addClass("close_icon");
      $(this).addClass("active");
      var layout = $(this).attr("data-attr");
      $("body").attr("class", "box-layout"); 
    }); 
  });
  $('.main-layout .ltr').on('click', function () {
    $(".sidebar-wrapper").removeClass("close_icon");
    $(".page-header").removeClass("close_icon");
    $(window).resize(function () {   
       $(".sidebar-wrapper").removeClass("close_icon");
       $(".page-header").removeClass("close_icon");
    });
    
});
$('.main-layout .rtl').on('click', function () {
   $(".sidebar-wrapper").removeClass("close_icon");
   $(".page-header").removeClass("close_icon");
   $(window).resize(function () {   
      $(".sidebar-wrapper").removeClass("close_icon");
      $(".page-header").removeClass("close_icon");
   });      
});
  if ($("body").hasClass("box-layout")) {
    $(".sidebar-wrapper").addClass("close_icon");
    $(".page-header").addClass("close_icon");
  }
});

//  responsive sidebar
var $window = $(window);
var widthwindow = $window.width();
var $nav = $(".sidebar-wrapper");
var $header = $(".page-header");
var $toggle_nav_top = $(".toggle-sidebar");

(function ($) {
  "use strict";
  if (widthwindow <= 1400) {
    $toggle_nav_top.attr("checked", false);
    $nav.addClass("close_icon");
    $header.addClass("close_icon");
  }
})(jQuery);
$(window).resize(function () {
  var widthwindaw = $window.width();
  if (widthwindaw <= 1400) {
    $toggle_nav_top.attr("checked", false);
    $nav.addClass("close_icon");
    $header.addClass("close_icon");
  } 
  else if (widthwindaw => 1400) {
    $toggle_nav_top.attr("checked", true);
    $nav.removeClass("close_icon");
    $header.removeClass("close_icon");
  }
});