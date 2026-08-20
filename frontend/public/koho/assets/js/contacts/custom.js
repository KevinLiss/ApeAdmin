function submitContact() {
	if ($("#bookmark-form").valid()) {
		var index_var = $('#index_var').val();
		var firstname = $('#con-name').val();
		var lastname = $('#con-last').val();
		var mail = $('#con-mail').val();
		$('#index_var').val(parseInt(index_var)+5);

			var tablist = '	<a class="contact-tab-'+index_var+' nav-link active" id="v-pills-user-tab" data-toggle="pill" onclick="activeDiv('+index_var+')" href="#v-pills-user" role="tab" aria-controls="v-pills-user" aria-selected="true" data-original-title="" title="">\
			                <div class="media">\
				                <img class="img-50 img-fluid m-r-20 rounded-circle update_img_0" src="../assets/images/user/user.png" alt="" data-original-title="" title="">\
				                <div class="media-body">\
				                    <h6>\
					                    <span class="first_name_'+index_var+'">'+firstname+'</span>\
					                    <span class="last_name_'+index_var+'">'+lastname+'</span></h6>\
				                    <p class="email_add_'+index_var+'">'+mail+'</p>\
				                </div>\
			                </div>\
			            </a>';
		      var tabcontent =  '<div class="tab-pane contact-tab-'+index_var+' tab-content-child fade show active" id="v-pills-user" role="tabpanel" aria-labelledby="v-pills-user-tab">\
		                <div class="profile-mail">\
		                  <div class="media">\
		                  <img class="img-100 img-fluid m-r-20 rounded-circle update_img_0" src="../assets/images/user/user.png" alt="" data-original-title="" title="">\
		                    <input class="updateimg" type="file" name="img" onchange="readURL(this,0)" data-original-title="" title="">\
		                    <div class="media-body mt-0">\
		                      <h5>\
		                      <span class="first_name_'+index_var+'">'+firstname+'</span>\
		                      <span class="last_name_'+index_var+'">'+lastname+'</span></h5>\
		                      <p class="email_add_'+index_var+'">'+mail+'</p>\
		                      <ul>\
		                        <li><a href="javascript:void(0)" onclick="editContact('+index_var+')" data-original-title="" title="">Edit</a></li>\
		                        <li><a href="javascript:void(0)" onclick="deleteContact('+index_var+')" data-original-title="" title="">Delete</a></li>\
		                        <li><a href="javascript:void(0)" onclick="history('+index_var+')" data-original-title="" title="">History</a></li>\
		                        <li><a href="javascript:void(0)" onclick="printContact('+index_var+')" data-toggle="modal" data-target="#printModal" data-original-title="" title="">Print</a></li>\
		                      </ul>\
		                    </div>\
		                  </div>\
		                  <div class="email-general">\
		                    <h6>General</h6>\
		                    <p>Email Address: <span class="font-primary email_add_'+index_var+'">'+mail+'</span></p>\
		                  </div>\
		    			</div>';

	    $('#v-pills-tab').append(tablist);
	    $('#v-pills-tabContent').append(tabcontent);
	    $('.contacts-tabs .nav-link ').removeClass('active show');
	    $('.contacts-tabs .tab-content .tab-content-child ').removeClass('active show');
		$( '.contact-tab-'+index_var ).addClass('active show');
	    $('#exampleModal').modal('toggle');
	    $('#bookmark-form').find('input[type="text"]').val('');
	    var notify = $.notify('Contact added successfully.', {
		    type: 'contactadd',
		    allow_dismiss: false,
		    delay: 2000,
		    placement: {
				from: 'top',
				align: 'center'
			},
		    timer: 300
		});
	}
} 

(function($) {
	$(".contact-editform").hide();
	$(".more-data").hide();
})(jQuery);

// edit contact

function editContact(index){

	$("#v-pills-tabContent").hide();
	$(".contact-editform").show();

	var first_name = $(".first_name_"+index).html();
	var last_name = $(".last_name_"+index).html();
	var email_add = $(".email_add_"+index).html();
	$("#first_name").val(first_name);
	$("#last_name").val(last_name);
	$("#email_add").val(email_add);
}

// print contact

function printContact(index){

	var print_name = $(".first_name_"+index).html();
	var plast_name = $(".last_name_"+index).html();
	var pemail_add = $(".email_add_"+index).html();
	var update_img = $(".update_img_"+index).attr("src");
	$("#printname").html(print_name);
	$("#printlast").html(plast_name);
	$("#printmail").html(pemail_add);
	$("#mailadd").html(pemail_add);
	$("#updateimg").attr("src",update_img);
}

// delete
function deleteContact(index){
	swal({
            title: "Are you sure?",
            text: "This contact will be deleted from your Personal Contacts and from the chat list too.",
            icon: "warning",
            buttons: true,
            dangerMode: true,
        })
        .then((willDelete) => {
            if (willDelete) {
                $('.contact-tab-'+index).hide();
				$( '.contact-tab-'+index ).next().addClass('active show');
            } else {
                swal("Your contact is safe!");
            }
        })
}
function activeDiv(index){
	$('.contacts-tabs .nav-link ').removeClass('active show');
	$('.contacts-tabs .tab-content .tab-content-child ').removeClass('active show');
	$( '.contact-tab-'+index ).addClass('active show');
}

// upload images

 function readURL(input,index){
		var elems = document.getElementsByClassName('update_img_'+index);
		for(i=0;i<elems.length;i++) {
		   elems[i].src =  window.URL.createObjectURL(input.files[0]);
		}
  };

$('.update-contact').on('click', function(e) {
	$("#v-pills-tabContent").show();
	$(".contact-editform").hide();
});

$('.edit-information').on('click', function(e) {
	$(".more-data").show();
	$(".edit-information").hide();
});

// history 

function history(index) {
    $("#right-history").toggleClass("show");
};

$(".closehistory").on('click', function(){
	$("#right-history").removeClass("show");
});

// print modal

function printDiv() {

  var divToPrint=document.getElementById('DivIdToPrint');

  var newWin=window.open('','Print-Window');

  newWin.document.open();

  newWin.document.write('<html><body onload="window.print()">'+divToPrint.innerHTML+'</body></html>');

  newWin.document.close();

  setTimeout(function(){newWin.close();},10);

}