(function($) {
  "use strict";
    Sortable.create(draggableMultiple, {
      group: 'draggableMultiple',
      animation: 150
    });
})(jQuery);
  $( function() {
    $( "#draggableMultiple" ).sortable({
      revert: true,
      animation:150
    });
  }); 