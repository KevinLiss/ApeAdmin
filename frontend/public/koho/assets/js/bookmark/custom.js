function submitBookMark() {
  if ($(".form-bookmark").valid()) {
    var index_var = $("#index_var").val();
    var weburl = $("#bm-weburl").val();
    var title = $("#bm-title").val();
    var desc = $("#bm-desc").val();
    var group = $("#bm-group").val();
    var collection = $("#bm-collection").val();
    $("#index_var").val(parseInt(index_var) + 6);

    var bmColData =
      '<div class="col-xl-3 col-md-4 xl-50">\
	      <div class="card card-with-border bookmark-card o-hidden"><div class="details-website"><img class="img-fluid" src="../assets/images/lightgallry/07.jpg" alt="" data-original-title="" title="">\
	        <div class="favourite-icon favourite_' +
      index_var +
      '"><a href="javascript:void(0)" onclick="setFavourite(' +
      index_var +
      ')" data-original-title="" title=""><i class="fa fa-star"></i></a></div>\
	        <div class="desciption-data">\
		        <div class="title-bookmark">\
		          <h6 class="title_' +
      index_var +
      '">' +
      title +
      '</h6>\
		          <p class="weburl_' +
      index_var +
      '">' +
      weburl +
      '</p>\
		          <div class="hover-block">\
		            <ul>\
		              <li><a href="" data-toggle="modal" data-target="#edit-bookmark">\
		              	<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-edit-2"><polygon points="16 3 21 8 8 21 3 21 3 16 16 3"></polygon></svg>\
		              	</a>\
		              </li>\
		              <li><a href="javascript:void(0)">\
			              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-link"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path></svg>\
			              </a>\
		              </li>\
		              <li>\
		              	<a href="javascript:void(0)">\
		              		<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-share-2"><circle cx="18" cy="5" r="3"></circle><circle cx="6" cy="12" r="3"></circle><circle cx="18" cy="19" r="3"></circle><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"></line><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"></line></svg>\
		              	</a>\
		              </li>\
		              <li>\
		              	<a href="javascript:void(0)">\
		              		<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-trash-2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path><line x1="10" y1="11" x2="10" y2="17"></line><line x1="14" y1="11" x2="14" y2="17"></line></svg>\
		              	</a>\
		              </li>\
		              <li class="pull-right text-right">\
		              	<a href="javascript:void(0)">\
		              		<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-tag"><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"></path><line x1="7" y1="7" x2="7" y2="7"></line></svg>\
		              	</a>\
		              </li>\
		            </ul>\
		          </div>\
		          <div class="content-general">\
		          	<p class="desc_' +
      index_var +
      '">' +
      desc +
      '</p>\
		          	<span class="collection_' +
      index_var +
      '">' +
      collection +
      "</span>\
		          </div>\
		        </div>\
		    </div>\
	      </div>\
	    </div>";

    $("#bookmarkData").append(bmColData);
    $("#bookmarkData1").append(bmColData);
    $("#exampleModal").modal("toggle");
    $("#bookmark-form").find('input[type="text"],textarea').val("");
  }
}

// edit contact

function editBookmark(index_var) {
  var title = $(".title_" + index_var).html();
  var weburl = $(".weburl_" + index_var).html();
  var desc = $(".desc_" + index_var).html();
  $("#edittitle").val(title);
  $("#editurl").val(weburl);
  $("#editdesc").val(desc);
}

// favourites bookmark

var fav_arr = [];
function setFavourite(index_var) {
  $(".favourite_" + index_var).toggleClass("favourite");
  var title = $(".title_" + index_var).html();
  var weburl = $(".weburl_" + index_var).html();
  var desc = $(".desc_" + index_var).html();
  var collection = $(".collection_" + index_var).html();
  var n = fav_arr.includes(index_var);

  if (n) {
    for (var i = 0; i < fav_arr.length; i++) {
      if (fav_arr[i] === index_var) {
        fav_arr.splice(i, 1);
      }
    }
    $(".favourite_card_" + index_var).hide();
  } else {
    fav_arr.push(index_var);

    var bmColData =
      '<div class="col-xl-3 col-md-4 xl-50 favourite_card_' +
      index_var +
      '">\
	      <div class="card card-with-border bookmark-card o-hidden"><div class="details-website"><img class="img-fluid" src="../assets/images/lightgallry/07.jpg" alt="" data-original-title="" title="">\
	        <div class="favourite-icon favourite" ><a href="javascript:void(0)" class="favourite_' +
      index_var +
      '" onclick="setFavourite(' +
      index_var +
      ')" data-original-title="" title=""><i class="fa fa-star"></i></a></div>\
	        <div class="desciption-data">\
		        <div class="title-bookmark">\
		          <h6 class="title_' +
      index_var +
      '">' +
      title +
      '</h6>\
		          <p class="weburl_' +
      index_var +
      '">' +
      weburl +
      '</p>\
		          <div class="hover-block">\
		            <ul>\
		              <li><a href="" data-toggle="modal" data-target="#edit-bookmark">\
		              	<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-edit-2"><polygon points="16 3 21 8 8 21 3 21 3 16 16 3"></polygon></svg>\
		              	</a>\
		              </li>\
		              <li><a href="javascript:void(0)">\
			              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-link"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path></svg>\
			              </a>\
		              </li>\
		              <li>\
		              	<a href="javascript:void(0)">\
		              		<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-share-2"><circle cx="18" cy="5" r="3"></circle><circle cx="6" cy="12" r="3"></circle><circle cx="18" cy="19" r="3"></circle><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"></line><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"></line></svg>\
		              	</a>\
		              </li>\
		              <li>\
		              	<a href="javascript:void(0)">\
		              		<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-trash-2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path><line x1="10" y1="11" x2="10" y2="17"></line><line x1="14" y1="11" x2="14" y2="17"></line></svg>\
		              	</a>\
		              </li>\
		              <li class="pull-right text-right">\
		              	<a href="javascript:void(0)">\
		              		<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-tag"><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"></path><line x1="7" y1="7" x2="7" y2="7"></line></svg>\
		              	</a>\
		              </li>\
		            </ul>\
		          </div>\
		          <div class="content-general">\
			        <p class="desc_' +
      index_var +
      '">' +
      desc +
      '</p>\
			        <span class="collection_' +
      index_var +
      '">' +
      collection +
      "</span>\
			      </div>\
		        </div>\
	      	</div>\
	      </div>\
	    </div>";
    $("#favouriteData").append(bmColData);
  }
  if (fav_arr.length == 0) {
    $(".no-favourite").show();
  } else {
    $(".no-favourite").hide();
  }
}

// list-view
$(".grid-bookmark-view").on("click", function (e) {
  $(".details-bookmark").removeClass("list-bookmark");
});
$(".list-layout-view").on("click", function (e) {
  $(".details-bookmark").css("opacity", "0.2");
  $(".details-bookmark").addClass("list-bookmark");
  setTimeout(function () {
    $(".details-bookmark").css("opacity", "1");
  }, 500);
});
