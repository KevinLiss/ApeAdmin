"use strict";
var morris_chart = {
    init: function() {
        Morris.Area({
            element: 'graph123',
            behaveLikeLine: true,
            data: [{
                x: '2011 Q1',
                y: 3,
                z: 3
            },
                {
                    x: '2011 Q2',
                    y: 2,
                    z: 1
                },
                {
                    x: '2011 Q3',
                    y: 2,
                    z: 4
                },
                {
                    x: '2011 Q4',
                    y: 3,
                    z: 3
                }
            ],
            xkey: 'x',
            ykeys: ['y', 'z'],
            labels: ['Y', 'Z'],
            lineColors: [KohoAdminConfig.secondary , KohoAdminConfig.primary ],
        }), Morris.Line({
            element: "morris-line-chart",
            data: [{
                y: "2011",
                a: 100,
                b: 90
            },
                {
                    y: "2012",
                    a: 75,
                    b: 65
                },
                {
                    y: "2013",
                    a: 50,
                    b: 40
                },
                {
                    y: "2014",
                    a: 75,
                    b: 65
                },
                {
                    y: "2015",
                    a: 50,
                    b: 40
                },
                {
                    y: "2016",
                    a: 75,
                    b: 65
                },
                {
                    y: "2017",
                    a: 100,
                    b: 90
                }],
            xkey: "y",
            ykeys: ["a", "b"],
            lineColors: [KohoAdminConfig.primary , KohoAdminConfig.secondary ],
            labels: ["Series A", "Series B"]
        }), Morris.Bar({
            element: "morris-simple-bar-chart",
            data: [{
                x: "2011 Q1",
                y: 3,
                z: 2,
                a: 3
            },
                {
                    x: "2011 Q2",
                    y: 2,
                    z: 3,
                    a: 1
                },
                {
                    x: "2011 Q3",
                    y: 5,
                    z: 2,
                    a: 4
                },
                {
                    x: "2011 Q4",
                    y: 2,
                    z: 4,
                    a: 3
                }],
            xkey: "x",
            ykeys: ["y", "z", "a"],
            barColors: [KohoAdminConfig.primary , KohoAdminConfig.secondary ,"#51bb25"],
            labels: ["Y", "Z", "A"]
        }), Morris.Bar({
            element: "bar-line-chart-morris",
            data: [{
                x: "2011 Q1",
                y: 0
            },
                {
                    x: "2011 Q2",
                    y: 1
                },
                {
                    x: "2011 Q3",
                    y: 2
                },
                {
                    x: "2011 Q4",
                    y: 3
                },
                {
                    x: "2012 Q1",
                    y: 4
                },
                {
                    x: "2012 Q2",
                    y: 5
                },
                {
                    x: "2012 Q3",
                    y: 6
                },
                {
                    x: "2012 Q4",
                    y: 7
                },
                {
                    x: "2013 Q1",
                    y: 8
                }],
            xkey: "x",
            ykeys: ["y"],
            labels: ["Y"],
            barColors: [KohoAdminConfig.primary]
        }), $(function() {
            var b = [{
                period: "2012-10-01",
                licensed: 5000,
                sorned: 4750
            },
                {
                    period: "2012-09-30",
                    licensed: 4500,
                    sorned: 4250
                },
                {
                    period: "2012-09-29",
                    licensed: 4000,
                    sorned: 3750
                },
                {
                    period: "2012-09-20",
                    licensed: 3500,
                    sorned: 3250
                },
                {
                    period: "2012-09-19",
                    licensed: 3000,
                    sorned: 2750
                },
                {
                    period: "2012-09-18",
                    licensed: 2500,
                    sorned: 2250
                }
            ];
            Morris.Bar({
                element: 'x-lable-morris-chart',
                data: b,
                barColors: [KohoAdminConfig.primary , KohoAdminConfig.secondary ],
                xkey: "period",
                ykeys: ["licensed", "sorned"],
                labels: ["Licensed", "SORN"],
                xLabelAngle: 60
            })
        }), $(function() {
            for (var c = [], d = 0; d <= 360; d += 10) c.push({
                x: d,
                y: 1.5 + 1.5 * Math.sin(Math.PI * d / 180).toFixed(4)
            });
            window.m = Morris.Line({
                element: 'decimal-morris-chart',
                data: c,
                xkey: "x",
                ykeys: ["y"],
                labels: ["sin(x)"],
                parseTime: !1,
                lineColors: [KohoAdminConfig.primary],
                hoverCallback: function(a, b, c, d) {
                    return c.replace("sin(x)", "1.5 + 1.5 sin(" + d.x + ")")
                },
                xLabelMargin: 10,
                integerYLabels: !0
            })
        }), $(function() {
            var b = [{
                period: "2012-10-30",
                licensed: 2000,
                sorned: 2000
            },
                {
                    period: "2012-09-30",
                    licensed: 3000,
                    sorned: 1000
                },
                {
                    period: "2012-09-29",
                    licensed: 2000,
                    sorned: 2000
                },
                {
                    period: "2012-09-20",
                    licensed: 4000,
                    sorned: 0
                },
                {
                    period: "2012-09-19",
                    licensed: 3000,
                    sorned: 1000
                },
                {
                    period: "2012-09-18",
                    licensed: 4000,
                    sorned: 0
                },
                {
                    period: "2012-09-17",
                    licensed: 3171,
                    sorned: 660
                },
                {
                    period: "2012-09-16",
                    licensed: 3171,
                    sorned: 676
                },
                {
                    period: "2012-09-15",
                    licensed: 3201,
                    sorned: 656
                },
                {
                    period: "2012-09-10",
                    licensed: 3215,
                    sorned: 622
                }];
            Morris.Line({
                element: 'x-Labels-Diagonally-morris-chart',
                data: b,
                xkey: "period",
                lineColors: [KohoAdminConfig.primary , KohoAdminConfig.secondary],
                ykeys: ["licensed", "sorned"],
                labels: ["Licensed", "SORN"],
                xLabelAngle: 60
            })
        }), $(function() {
            Morris.Donut({
                element: 'donut-color-chart-morris',
                data: [{
                    value: 70,
                    label: "foo"
                },
                    {
                        value: 15,
                        label: "bar"
                    },
                    {
                        value: 10,
                        label: "baz"
                    },
                    {
                        value: 5,
                        label: "A really really long label"
                    }],
                backgroundColor: "rgba(68, 102, 242, 0.5)",
                labelColor: "#999999",
                colors: [KohoAdminConfig.primary , KohoAdminConfig.secondary ,"#f8d62b" ,"#51bb25" ,"rgba(248, 214, 43, 1)", "#51bb25" ,"#f8d62b"],
                formatter: function(a) {
                    return a + "%"
                }
            });
        }),
            $(function() {
                var e = 0,
                    f = function(a) {
                        for (var b = [], c = 0; c <= 360; c += 10) {
                            var d = (a + c) % 360;
                            b.push({
                                x: c,
                                y: Math.sin(Math.PI * d / 180).toFixed(4),
                                z: Math.cos(Math.PI * d / 180).toFixed(4)
                            })
                        }
                        return b
                    },
                    g = Morris.Line({
                        element:'updating-data-morris-chart',
                        data: f(0),
                        xkey: "x",
                        ykeys: ["y", "z"],
                        labels: ["sin()", "cos()"],
                        parseTime: !1,
                        ymin: -1,
                        ymax: 1,
                        hideHover: !0,
                        lineColors: [KohoAdminConfig.primary , KohoAdminConfig.secondary ],
                    }),
                    h = function() {
                        e++, g.setData(f(5 * e)), $(".reloadStatus").text(e + " reloads")
                    };
                setInterval(h, 100)
            }), $(function() {
            Morris.Bar({
                element: 'stacked-bar-chart',
                data: [{
                    x: "2011 Q1",
                    a: 3,
                    y: 3,
                    z: 2
                },
                    {
                        x: "2011 Q2",
                        a: 1,
                        y: 2,
                        z: null
                    },
                    {
                        x: "2011 Q3",
                        a: 4,
                        y: 0,
                        z: 2
                    },
                    {
                        x: "2011 Q4",
                        a: 1,
                        y: 2,
                        z: null
                    },
                    {
                        x: "2011 Q5",
                        a: 4,
                        y: 0,
                        z: 2
                    },
                    {
                        x: "2011 Q6",
                        a: 3,
                        y: 3,
                        z: 2

                    },
                    {
                        x: "2011 Q4",
                        a: 4,
                        y: 0,
                        z: 2
                    },
                    {
                        x: "2011 Q7",
                        a: 3,
                        y: 3,
                        z: 2
                    }],
                xkey: "x",
                ykeys: ["y", "z", "a"],
                labels: ["A", "Y", "Z"],
                barColors: [KohoAdminConfig.primary , KohoAdminConfig.secondary ,"#51bb25" ,"#f8d62b" ,"#a927f9", KohoAdminConfig.secondary , KohoAdminConfig.primary ],
                stacked: !0
            });
        });
    }
};
(function($) {
    "use strict";
    morris_chart.init()
})(jQuery);
