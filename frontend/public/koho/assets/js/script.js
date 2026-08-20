(function ($) {
  "use strict";
  // 更多下载：http://www.bootstrapmb.com
  // Loader
  $(".loader-wrapper").fadeOut("slow", function () {
    setTimeout(function () {
      $(this).remove();
    }, 100);
  });

  // Tap To Top Button
  $(".tap-top").on("click", function () {
    $("html, body").animate(
      {
        scrollTop: 0,
      },
      600
    );
    return false;
  });

  // Scroll Function
  $(window).on("scroll", function () {
    if ($(this).scrollTop() > 600) {
      $(".tap-top").fadeIn();
    } else {
      $(".tap-top").fadeOut();
    }
  });

  // active link

  $(".chat-menu-icons .toogle-bar").on("click", function () {
    $(".chat-menu").toggleClass("show");
  });

  $(".mobile-title svg").on("click", function () {
    $(".header-mega").toggleClass("d-block");
  });

  $(".onhover-dropdown").on("click", function () {
    $(this).children(".onhover-show-div").toggleClass("active");
  });

  $("#flip-btn").on("click", function () {
    $(".flip-card-inner").addClass("flipped");
  });

  $("#flip-back").on("click", function () {
    $(".flip-card-inner").removeClass("flipped");
  });

  //landing header
  $(".toggle-menu").on("click", function () {
    $(".landing-menu").toggleClass("open");
  });
  $(".menu-back").on("click", function () {
    $(".landing-menu").toggleClass("open");
  });

  $(".md-sidebar-toggle").on("click", function () {
    $(".md-sidebar-aside").toggleClass("open");
  });

  // color selector
  $(".color-selector ul li ").on("click", function (e) {
    $(".color-selector ul li").removeClass("active");
    $(this).addClass("active");
  });

  $(document).on("click", function (e) {
    var outside_space = $(".outside");
    if (
      !outside_space.is(e.target) &&
      outside_space.has(e.target).length === 0
    ) {
      $(".menu-to-be-close").removeClass("d-block");
      $(".menu-to-be-close").css("display", "none");
    }
  });

  if ($(".page-wrapper").hasClass("horizontal-wrapper")) {
    $(".sidebar-list").hover(
      function () {
        $(this).addClass("hoverd");
      },
      function () {
        $(this).removeClass("hoverd");
      }
    );
    $(window).on("scroll", function () {
      if ($(this).scrollTop() < 600) {
        $(".sidebar-list").removeClass("hoverd");
      }
    });
  }

  /*----------------------------------------
     passward show hide
     ----------------------------------------*/
  $(".show-hide").show();
  $(".show-hide span").addClass("show");

  $(".show-hide span").on("click", function () {
    if ($(this).hasClass("show")) {
      $('input[name="login[password]"]').attr("type", "text");
      $(this).removeClass("show");
    } else {
      $('input[name="login[password]"]').attr("type", "password");
      $(this).addClass("show");
    }
  });
  $('form button[type="submit"]').on("click", function () {
    $(".show-hide span").addClass("show");
    $(".show-hide")
      .parent()
      .find('input[name="login[password]"]')
      .attr("type", "password");
  });

  /*=====================
      02. Background Image js
      ==========================*/
  $(".bg-center").parent().addClass("b-center");
  $(".bg-img-cover").parent().addClass("bg-size");
  $(".bg-img-cover").each(function () {
    var el = $(this),
      src = el.attr("src"),
      parent = el.parent();
    parent.css({
      "background-image": "url(" + src + ")",
      "background-size": "cover",
      "background-position": "center",
      display: "block",
    });
    el.hide();
  });

  $(".mega-menu-container").css("display", "none");
  $(".header-search").on("click", function () {
    $(".search-full").addClass("open");
  });
  $(".close-search").on("click", function () {
    $(".search-full").removeClass("open");
    $("body").removeClass("offcanvas");
  });
  $(".mobile-toggle").on("click", function () {
    $(".nav-menus").toggleClass("open");
  });
  $(".bookmark-search").on("click", function () {
    $(".form-control-search").toggleClass("open");
  });
  $(".filter-toggle").on("click", function () {
    $(".product-sidebar").toggleClass("open");
  });
  $(".toggle-data").on("click", function () {
    $(".product-wrapper").toggleClass("sidebaron");
  });

  $(".mobile-search").on("click", function () {
    $(".form-control").toggleClass("open");
  });

  $(".form-control-search input").keyup(function (e) {
    if (e.target.value) {
      $(".page-wrapper").addClass("offcanvas-bookmark");
    } else {
      $(".page-wrapper").removeClass("offcanvas-bookmark");
    }
  });
  $(".search-full input").keyup(function (e) {
    console.log(e.target.value);
    if (e.target.value) {
      $("body").addClass("offcanvas");
    } else {
      $("body").removeClass("offcanvas");
    }
  });

  $("body").keydown(function (e) {
    if (e.keyCode == 27) {
      $(".search-full input").val("");
      $(".form-control-search input").val("");
      $(".page-wrapper").removeClass("offcanvas-bookmark");
      $(".search-full").removeClass("open");
      $(".search-form .form-control-search").removeClass("open");
      $("body").removeClass("offcanvas");
    }
  });
  $(".mode").on("click", function () {
    $(".mode i").toggleClass("fa-moon-o").toggleClass("fa-lightbulb-o");
    $("body").toggleClass("dark-only");
    var color = $(this).attr("data-attr");
    localStorage.setItem("body", "dark-only");
  });

  // Language

  var tnum = "en";

  $(document).ready(function () {
    if (localStorage.getItem("primary") != null) {
      var primary_val = localStorage.getItem("primary");
      $("#ColorPicker1").val(primary_val);
      var secondary_val = localStorage.getItem("secondary");
      $("#ColorPicker2").val(secondary_val);
    }

    $(document).on("click", function (e) {
      $(".translate_wrapper, .more_lang").removeClass("active");
    });
    $(".translate_wrapper .current_lang").on("click", function (e) {
      e.stopPropagation();
      $(this).parent().toggleClass("active");

      setTimeout(function () {
        $(".more_lang").toggleClass("active");
      }, 5);
    });

    /*TRANSLATE*/
    translate(tnum);

    $(".more_lang .lang").on("click", function () {
      $(this).addClass("selected").siblings().removeClass("selected");
      $(".more_lang").removeClass("active");

      var i = $(this).find("i").attr("class");
      var lang = $(this).attr("data-value");
      var tnum = lang;
      translate(tnum);

      $(".current_lang .lang-txt").text(lang);
      $(".current_lang i").attr("class", i);
    });
  });

  var trans = [
    {
      en: "General",
      pt: "Geral",
      es: "Generalo",
      fr: "GÃ©nÃ©rale",
      de: "Generel",
      cn: "ä¸€èˆ¬",
      ae: "Ø­Ø¬Ù†Ø±Ø§Ù„ Ù„ÙˆØ§Ø¡",
    },
    {
      en: "Dashboards,widgets & layout.",
      pt: "PainÃ©is, widgets e layout.",
      es: "Paneloj, fenestraÄµoj kaj aranÄo.",
      fr: "Tableaux de bord, widgets et mise en page.",
      de: "Dashboards, widgets en lay-out.",
      cn: "ä»ªè¡¨æ¿ï¼Œå°å·¥å…·å’Œå¸ƒå±€ã€‚",
      ae: "Ù„ÙˆØ­Ø§Øª Ø§Ù„Ù…Ø¹Ù„ÙˆÙ…Ø§Øª ÙˆØ§Ù„Ø£Ø¯ÙˆØ§Øª ÙˆØ§Ù„ØªØ®Ø·ÙŠØ·.",
    },
    {
      en: "Dashboards",
      pt: "PainÃ©is",
      es: "Paneloj",
      fr: "Tableaux",
      de: "Dashboards",
      cn: " ä»ªè¡¨æ¿ ",
      ae: "ÙˆØ­Ø§Øª Ø§Ù„Ù‚ÙŠØ§Ø¯Ø© ",
    },
    {
      en: "Default",
      pt: "PadrÃ£o",
      es: "Vaikimisi",
      fr: "DÃ©faut",
      de: "Standaard",
      cn: "é›»å­å•†å‹™",
      ae: "ÙˆØ¥ÙØªØ±Ø§Ø¶ÙŠ",
    },
    {
      en: "Ecommerce",
      pt: "ComÃ©rcio eletrÃ´nico",
      es: "Komerco",
      fr: "Commerce Ã©lectronique",
      de: "E-commerce",
      cn: "é›»å­å•†å‹™",
      ae: "ÙˆØ§Ù„ØªØ¬Ø§Ø±Ø© Ø§Ù„Ø¥Ù„ÙƒØªØ±ÙˆÙ†ÙŠØ©",
    },
    {
      en: "Widgets",
      pt: "Ferramenta",
      es: "Vidin",
      fr: "Widgets",
      de: "Widgets",
      cn: "å°éƒ¨ä»¶",
      ae: "ÙˆØ§Ù„Ø­Ø§Ø¬ÙŠØ§Øª",
    },
    {
      en: "Page layout",
      pt: "Layout da pÃ¡gina",
      es: "PaÄa aranÄo",
      fr: "Tableaux",
      de: "Mise en page",
      cn: "é é¢ä½ˆå±€",
      ae: "ÙˆØªØ®Ø·ÙŠØ· Ø§Ù„ØµÙØ­Ø©",
    },
    {
      en: "Applications",
      pt: "FormulÃ¡rios",
      es: "Aplikoj",
      fr: "Applications",
      de: "Toepassingen",
      cn: "æ‡‰ç”¨é ˜åŸŸ",
      ae: "ÙˆØ§Ù„ØªØ·Ø¨ÙŠÙ‚Ø§Øª",
    },
    {
      en: "Ready to use Apps",
      pt: "Pronto para usar aplicativos",
      es: "Preta uzi Apps",
      fr: " Applications prÃªtes Ã  lemploi ",
      de: "Klaar om apps te gebruiken",
      cn: "ä»ªè¡¨æ¿",
      ae: "Ø¬Ø§Ù‡Ø² Ù„Ø§Ø³ØªØ®Ø¯Ø§Ù… Ø§Ù„ØªØ·Ø¨ÙŠÙ‚Ø§Øª",
    },
  ];

  function translate(tnum) {
    for (var i = 1; i < 9; i++) {
      $(".lan-" + i).text(trans[i - 1][tnum]);
    }
  }
})(jQuery);

function toggleFullScreen() {
  if (
    (document.fullScreenElement && document.fullScreenElement !== null) ||
    (!document.mozFullScreen && !document.webkitIsFullScreen)
  ) {
    if (document.documentElement.requestFullScreen) {
      document.documentElement.requestFullScreen();
    } else if (document.documentElement.mozRequestFullScreen) {
      document.documentElement.mozRequestFullScreen();
    } else if (document.documentElement.webkitRequestFullScreen) {
      document.documentElement.webkitRequestFullScreen(
        Element.ALLOW_KEYBOARD_INPUT
      );
    }
  } else {
    if (document.cancelFullScreen) {
      document.cancelFullScreen();
    } else if (document.mozCancelFullScreen) {
      document.mozCancelFullScreen();
    } else if (document.webkitCancelFullScreen) {
      document.webkitCancelFullScreen();
    }
  }
}
