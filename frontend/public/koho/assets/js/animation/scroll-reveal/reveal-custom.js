
/*----------------------------------------------------
 Scroll reveal animation
 ----------------------------------------------------*/
(function($) {
"use strict";
    if (Modernizr.csstransforms3d) {
        window.sr = ScrollReveal();
        sr.reveal('.reveal', {
            duration: 800,
            delay: 400,
            reset: true,
            easing: 'linear',
            scale: 1
        });
    }
})(jQuery);