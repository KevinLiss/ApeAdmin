$(function(){
    $(".notification").on('click', function() {
        $.notify({
            icon: 'glyphicon glyphicon-star',
            message: "Code Copied to clipboard!  "
        },{
            type: 'copy',
            newest_on_top:false ,
            mouse_over:false,
            showProgressbar:false,
            spacing:10,
            timer:1400,
            z_index: 1000,
            allow_dismiss: true,
            delay:1000,
            placement:{
                from:'bottom',
                align:'right'
            },
            animate:{
                enter:'animated bounce',
                exit:'animated bounce'
            }
        });
    });
});
