'use strict';
$(function() {
    $('#myGrid').gridEditor({
        new_row_layouts: [[12], [4,4,4], [3,3,3,3], [2,2,2,2,2,2], [6, 6], [4,8], [8,4], [9, 3], [6, 3, 3]],
        content_types: ['ckeditor'],
        ckeditor: {
            config: {
                on: {
                    instanceReady: function(evt) {
                        var instance = this;
                    }
                }
            }
        }
    });
    var html = $('#myGrid').gridEditor('getHtml');
});