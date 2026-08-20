'use strict';
$(function() {
    function ratingEnable() {
        $('#u-rating-1to10').barrating('show', {
            theme: 'bars-1to10'
        });
        $('#u-rating-movie').barrating('show', {
            theme: 'bars-movie'
        });
        $('#u-rating-movie').barrating('set', 'Mediocre');
        $('#u-rating-square').barrating('show', {
            theme: 'bars-square',
            showValues: true,
            showSelectedRating: false,
        });
        $('#u-rating-pill').barrating('show', {
            theme: 'bars-pill',
            initialRating: 'A',
            showValues: true,
            showSelectedRating: false,
            allowEmpty: true,
            emptyValue: '-- no rating selected --',
            onSelect: function(value, text) {
                alert('Selected rating: ' + value);
            }
        });
        $('#u-rating-reversed').barrating('show', {
            theme: 'bars-reversed',
            showSelectedRating: true,
            reverse: true
        });
        $('#u-rating-horizontal').barrating('show', {
            theme: 'bars-horizontal',
            reverse: true,
            hoverState: false
        });
        $('#u-rating-fontawesome').barrating({
            theme: 'fontawesome-stars',
            showSelectedRating: false
        });
        $('#u-rating-css').barrating({
            theme: 'css-stars',
            showSelectedRating: false
        });
        var currentRating = $('#u-rating-fontawesome-o').data('current-rating');
        $('.stars-example-fontawesome-o .current-rating').find('span').html(currentRating);
        $('.stars-example-fontawesome-o .clear-rating').click( function(event) {
            event.preventDefault();
            $('#u-rating-fontawesome-o').barrating('clear');
        });
        $('#u-rating-fontawesome-o').barrating({
            theme: 'fontawesome-stars-o',
            showSelectedRating: false,
            initialRating: currentRating,
            onSelect: function(value, text) {
                if (!value) {
                    $('#u-rating-fontawesome-o').barrating('clear');
                } else {
                    $('.stars-example-fontawesome-o .current-rating').addClass('hidden');
                    $('.stars-example-fontawesome-o .your-rating').removeClass('hidden').find('span').html(value);
                }
            },
            onClear: function(value, text) {
                $('.stars-example-fontawesome-o').find('.current-rating').removeClass('hidden').end().find('.your-rating').addClass('hidden');
            }
        });
    }
    function ratingDisable() {
        $('select').barrating('destroy');
    }
    $('.rating-enable').click(function(event) {
        event.preventDefault();
        ratingEnable();
        $(this).addClass('deactivated');
        $('.rating-disable').removeClass('deactivated');
    });
    $('.rating-disable').click(function(event) {
        event.preventDefault();
        ratingDisable();
        $(this).addClass('deactivated');
        $('.rating-enable').removeClass('deactivated');
    });
    ratingEnable();
});
