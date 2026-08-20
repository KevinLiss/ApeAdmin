'use strict';
var range_slider_custom = {
    init: function() { 
        $("#u-range-01").ionRangeSlider(),
        $("#u-range-02").ionRangeSlider({
            min: 100,
            max: 1000,
            from: 550
        }),$("#u-range-03").ionRangeSlider({
            type: "double",
            grid: true,
            min: 0,
            max: 1000,
            from: 200, 
            to: 800,
            prefix: "$"
        }),$("#u-range-04").ionRangeSlider({
            type: "double",
            grid: true,
            min: -1000,
            max: 1000,
            from: -500,
            to: 500
        }), $("#u-range-05").ionRangeSlider({
            type: "double",
            grid: true,
            min: -1000,
            max: 1000,
            from: -500,
            to: 500,
            step: 250
        }), $("#u-range-06").ionRangeSlider({
            grid: true,
            from: 3,
            values: ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        }), $("#u-range-07").ionRangeSlider({
            grid: true,
            min: 1000,
            max: 10000,
            from: 2000,
            step: 100,
            prettify_enabled: true
        }), $("#u-range-08").ionRangeSlider({
            min: 100,
            max: 1000,
            from: 550,
            disable: true
        });
    }
};
(function($) {
    "use strict";
    range_slider_custom.init();
})(jQuery);