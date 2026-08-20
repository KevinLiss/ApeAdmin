(function($) {
    "use strict";
    setTimeout(function(){
        $("#line-chart-sparkline").sparkline([5, 10, 20, 14, 17, 21, 20, 10, 4, 13,0, 10, 30, 40, 10, 15, 20], {
            type: 'line',
            width: '100%',
            height: '100%',
            tooltipClassname: 'chart-sparkline',
            lineColor: KohoAdminConfig.primary,
            fillColor: 'rgba(62, 95, 206, 0.40)',
            highlightLineColor: KohoAdminConfig.primary,
            highlightSpotColor: KohoAdminConfig.primary,
            targetColor: KohoAdminConfig.primary,
            performanceColor: KohoAdminConfig.primary,
            boxFillColor: KohoAdminConfig.primary,
            medianColor: KohoAdminConfig.primary,
            minSpotColor: KohoAdminConfig.primary
        });
    });
    var mrefreshinterval = 500;
    var lastmousex = -1;
    var lastmousey = -1;
    var lastmousetime;
    var mousetravel = 0;
    var mpoints = [];
    var mpoints_max = 30;
    $('body').mousemove(function(e) {
        var mousex = e.pageX;
        var mousey = e.pageY;
        if (lastmousex > -1)
            mousetravel += Math.max(Math.abs(mousex - lastmousex), Math.abs(mousey - lastmousey));
        lastmousex = mousex;
        lastmousey = mousey;
    });
    var mdraw = function() {
        var md = new Date();
        var timenow = md.getTime();
        if (lastmousetime && lastmousetime != timenow) {
            var pps = Math.round(mousetravel / (timenow - lastmousetime) * 1000);
            mpoints.push(pps);
            if (mpoints.length > mpoints_max)
                mpoints.splice(0, 1);
            mousetravel = 0;

            var mouse_wid = $('#mouse-speed-chart-sparkline').parent('.card-block').parent().width();
            var a = mpoints - mouse_wid;
            $('#mouse-speed-chart-sparkline').sparkline(mpoints, {
                width: '100%',
                height: '100%',
                tooltipClassname: 'chart-sparkline',
                lineColor: KohoAdminConfig.primary ,
                fillColor: 'rgba(62, 95, 206, 0.40)',
                highlightLineColor: KohoAdminConfig.primary ,
                highlightSpotColor: KohoAdminConfig.primary ,
                targetColor: KohoAdminConfig.primary ,
                performanceColor: KohoAdminConfig.primary ,
                boxFillColor: KohoAdminConfig.primary ,
                medianColor: KohoAdminConfig.primary ,
                minSpotColor: KohoAdminConfig.primary
            });
        }
        lastmousetime = timenow;
        mtimer = setTimeout(mdraw, mrefreshinterval);
    }
    var mtimer = setTimeout(mdraw, mrefreshinterval);
    $.sparkline_display_visible();
    $("#custom-line-chart").sparkline([5, 30, 27, 35, 30, 50, 70], {
        type: 'line',
        width: '100%',
        height: '100%',
        tooltipClassname: 'chart-sparkline',
        chartRangeMax: '50',
        lineColor: KohoAdminConfig.secondary,
        fillColor: 'rgba(255, 206, 0, 0.30)',
        highlightLineColor: 'rgba(247, 49, 100, 0.30)',
        highlightSpotColor: 'rgba(247, 49, 100, 0.8)'
        
    });
    $("#custom-line-chart").sparkline([0, 5, 10, 7, 25, 20, 30], {
        type:'line',
        width:'100%',
        height:'100%',
        composite:'!0',
        tooltipClassname:'chart-sparkline',
        chartRangeMax:'40',
        lineColor:KohoAdminConfig.primary,
        fillColor:'rgba(62, 95, 206, 0.40)',
        highlightLineColor: 'rgba(145, 46, 252, 0.40)',
        highlightSpotColor: 'rgba(145, 46, 252, 0.8)'
    });
})(jQuery);

var sparkline_chart = {
  init: function() {
    setTimeout(function(){
        $("#simple-line-chart-sparkline").sparkline([5, 10, 20, 14, 17, 21, 20, 10, 4, 13,0, 10, 30, 40, 10, 15, 20], {
            type: 'line',
            width: '100%',
            height: '100%',
            tooltipClassname: 'chart-sparkline',
            lineColor: KohoAdminConfig.primary,
            fillColor: 'transparent',
            highlightLineColor: KohoAdminConfig.primary,
            highlightSpotColor: KohoAdminConfig.primary,
            targetColor: KohoAdminConfig.primary,
            performanceColor: KohoAdminConfig.primary,
            boxFillColor: KohoAdminConfig.primary,
            medianColor: KohoAdminConfig.primary,
            minSpotColor: KohoAdminConfig.primary
        });
    }), $("#bar-chart-sparkline").sparkline([5, 2, 2, 4, 9, 5, 7, 5, 2, 2, 6], {
        type: 'bar',
        barWidth: '60',
        height: '100%',
        tooltipClassname: 'chart-sparkline',
        barColor: KohoAdminConfig.primary
    }), $("#pie-sparkline-chart").sparkline([1.5, 1, 1, 0.5], {
        type: 'pie',
        width: '100%',
        height: '100%',
        sliceColors: ['#51bb25','#f8d62b', KohoAdminConfig.secondary , KohoAdminConfig.primary ],
        tooltipClassname: 'chart-sparkline'
    });
    }
};
(function($) {
    "use strict";
  sparkline_chart.init()
})(jQuery);
