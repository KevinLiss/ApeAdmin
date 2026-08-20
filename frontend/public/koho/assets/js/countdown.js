(function ($) {
  "use strict";
  // Countdown js
  const second = 1000,
    minute = second * 60,
    hour = minute * 60,
    day = hour * 24;

  var countDown = new Date("Dec 30, 2022 00:00:00").getTime(),
    x = setInterval(function () {
      var now = new Date().getTime(),
        distance = countDown - now;

      (document.getElementById("days").innerText = Math.floor(distance / day)),
        (document.getElementById("hours").innerText = Math.floor(
          (distance % day) / hour
        )),
        (document.getElementById("minutes").innerText = Math.floor(
          (distance % hour) / minute
        )),
        (document.getElementById("seconds").innerText = Math.floor(
          (distance % minute) / second
        ));
    }, second);
})(jQuery);
