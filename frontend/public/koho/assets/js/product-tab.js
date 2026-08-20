(function ($) {
  //list layout view
  $(".grid-layout-view").on("click", function (e) {
    $(".product-wrapper-grid").removeClass("list-view");
    $(".product-wrapper-grid").children().children().removeClass("col-xl-12");
  });
  $(".list-layout-view").on("click", function (e) {
    $(".collection-grid-view").css("opacity", "0");
    $(".product-wrapper-grid").css("opacity", "0.2");
    $(".product-wrapper-grid").addClass("list-view");
    $(".product-wrapper-grid").children().children();
    $(".product-wrapper-grid").children().children().addClass("col-xl-12");
    setTimeout(function () {
      $(".product-wrapper-grid").css("opacity", "1");
    }, 500);
  });

  // owl carousl
  $(document).ready(function () {
    $("#testimonial").owlCarousel({
      items: 1,
      margin: 30,
      loop: true,
      pagination: true,
      navigationText: true,
      dots: false,
      nav: true,
    });
  });

  // grid options
  $(".product-2-layout-view").on("click", function (e) {
    if ($(".product-wrapper-grid").hasClass("list-view")) {
    } else {
      $(".product-wrapper-grid").children().children().removeClass();
      $(".product-wrapper-grid").children().children().addClass("col-xl-6");
      $(".product-wrapper-grid").children().children().addClass("col-sm-6");
      $(".left-filter").removeClass("filter-view custom-scrollbar");
    }
  });
  $(".product-3-layout-view").on("click", function (e) {
    if ($(".product-wrapper-grid").hasClass("list-view")) {
    } else {
      $(".product-wrapper-grid").children().children().removeClass();
      $(".product-wrapper-grid").children().children().addClass("col-xl-4");
      $(".product-wrapper-grid").children().children().addClass("col-sm-4");
      $(".left-filter").removeClass("filter-view custom-scrollbar");
    }
  });
  $(".product-4-layout-view").on("click", function (e) {
    if ($(".product-wrapper-grid").hasClass("list-view")) {
    } else {
      $(".product-wrapper-grid").children().children().removeClass();
      $(".product-wrapper-grid").children().children().addClass("col-xl-3");
      $(".product-wrapper-grid").children().children().addClass("col-sm-3");
      $(".left-filter").removeClass("filter-view custom-scrollbar");
    }
  });
  $(".product-6-layout-view").on("click", function (e) {
    if ($(".product-wrapper-grid").hasClass("list-view")) {
    } else {
      $(".product-wrapper-grid").children().children().removeClass();
      $(".product-wrapper-grid").children().children().addClass("col-xl-2");
      $(".left-filter").addClass("filter-sidebar custom-scrollbar");
    }
  });
})(jQuery);
