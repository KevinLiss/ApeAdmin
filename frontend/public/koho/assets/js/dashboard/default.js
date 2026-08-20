//  yearly overview  start
var options = {
  series: [
    {
      type: "area",
      data: [20, 20, 50, 90, 70, 80, 30, 45, 35, 95, 70, 45, 90],
    },
  ],
  chart: {
    height: 203,
    type: "area",
    toolbar: {
      show: false,
    },
  },
  stroke: {
    curve: "smooth",
    width: [5, 1],
    dashArray: [0, 5],
  },
  fill: {
    type: "gradient",
    gradient: {
      shadeIntensity: 1,
      opacityFrom: 0.5,
      opacityTo: 0.9,
      stops: [0, 100],
    },
  },

  markers: {
    size: 0,
    colors: undefined,
    strokeColors: [KohoAdminConfig.primary],
    strokeWidth: [8, 0],
    strokeOpacity: 0.3,
    strokeDashArray: 0,
    fillOpacity: 1,
    discrete: [],
    shape: "circle",
    radius: 2,
    offsetX: 0,
    offsetY: 0,
    onClick: undefined,
    onDblClick: undefined,
    showNullDataPoints: true,
    hover: {
      size: 7,
      sizeOffset: 3,
    },
  },
  responsive: [
    {
      breakpoint: 1401,
      options: {
        chart: {
          height: 210,
        },
      },
    },
    {
      breakpoint: 992,
      options: {
        chart: {
          height: 200,
        },
      },
    },
  ],
  yaxis: {
    show: false,
  },
  grid: {
    show: false,
  },
  xaxis: {
    show: false,
    labels: {
      show: false,
    },
    axisTicks: {
      show: false,
    },
    crosshairs: {
      show: true,
      width: 1,
      position: "back",
      stroke: {
        color: KohoAdminConfig.primary,
        width: 1,
        dashArray: 5,
      },
    },
  },
  tooltip: {
    marker: {
      show: false,
    },
    fixed: {
      enabled: false,
      position: "bottomRight",
      offsetX: 0,
      offsetY: 0,
    },
  },
  dataLabels: {
    enabled: false,
  },
  legend: {
    show: false,
  },
  colors: [KohoAdminConfig.primary],
};
var chart = new ApexCharts(document.querySelector("#yearly-view"), options);
chart.render();

// knob chart start
(function ($) {
  "use strict";
  $(".knob1").knob({
    width: 120,
    height: 120,
    max: 120,
    format: function (value) {
      return value + "%";
    },
    draw: function () {
      // "tron" case
      if (this.$.data("skin") == "tron") {
        this.cursorExt = 1;

        var a = this.arc(this.cv), // Arc
          pa, // Previous arc
          r = 1;

        this.g.lineWidth = this.lineWidth;

        if (this.o.displayPrevious) {
          pa = this.arc(this.v);
          this.g.beginPath();
          this.g.strokeStyle = this.pColor;
          this.g.arc(
            this.xy,
            this.xy,
            this.radius - this.lineWidth,
            pa.s,
            pa.e,
            pa.d
          );
          this.g.stroke();
        }

        this.g.beginPath();
        this.g.strokeStyle = r ? this.o.fgColor : this.fgColor;
        this.g.arc(
          this.xy,
          this.xy,
          this.radius - this.lineWidth,
          a.s,
          a.e,
          a.d
        );
        this.g.stroke();

        this.g.lineWidth = 2;
        this.g.beginPath();
        this.g.strokeStyle = this.o.fgColor;
        this.g.arc(
          this.xy,
          this.xy,
          this.radius - this.lineWidth + 1 + (this.lineWidth * 2) / 3,
          0,
          2 * Math.PI,
          false
        );
        this.g.stroke();

        return false;
      }
    },
  });
  // Example of infinite knob, iPod click wheel
  var v,
    up = 0,
    down = 0,
    i = 0,
    $idir = $("div.idir"),
    $ival = $("div.ival"),
    incr = function () {
      i++;
      $idir.show().html("+").fadeOut();
      $ival.html(i);
    },
    decr = function () {
      i--;
      $idir.show().html("-").fadeOut();
      $ival.html(i);
    };
  $("input.infinite").knob({
    min: 0,
    max: 20,
    stopper: false,
    change: function () {
      if (v > this.cv) {
        if (up) {
          decr();
          up = 0;
        } else {
          up = 1;
          down = 0;
        }
      } else {
        if (v < this.cv) {
          if (down) {
            incr();
            down = 0;
          } else {
            down = 1;
            up = 0;
          }
        }
      }
      v = this.cv;
    },
  });
})(jQuery);

// small chart start
var options = {
  series: [
    {
      name: "Statistics",
      data: [20, 30, 40, 80, 50],
    },
    {
      name: "Statistics",
      data: [80, 70, 60, 20, 50],
    },
  ],
  chart: {
    type: "bar",
    height: 155,
    stacked: true,
    stackType: "100%",
    toolbar: {
      show: false,
    },
  },

  plotOptions: {
    bar: {
      horizontal: false,
      s̶t̶a̶r̶t̶i̶n̶g̶S̶h̶a̶p̶e̶: "rounded",
      e̶n̶d̶i̶n̶g̶S̶h̶a̶p̶e̶: "rounded",
      borderRadius: 6,
      columnWidth: "50px",
      barHeight: "70%",
    },
  },
  grid: {
    show: false,
    xaxis: {
      lines: {
        show: false,
      },
    },
  },
  dataLabels: {
    enabled: false,
  },
  fill: {
    opacity: 1,
  },
  legend: {
    show: false,
  },
  tooltip: {
    marker: {
      show: false,
    },
    fixed: {
      enabled: false,
      position: "bottomRight",
      offsetX: 0,
      offsetY: 0,
    },
  },
  states: {
    hover: {
      filter: {
        type: "darken",
        value: 1,
      },
    },
  },
  colors: [KohoAdminConfig.secondary, "#EADAD3"],
  xaxis: {
    show: false,
    axisBorder: {
      show: false,
    },
    axisTicks: {
      show: false,
    },
  },
  yaxis: {
    show: false,
    axisBorder: {
      show: false,
    },
    axisTicks: {
      show: false,
    },
  },
  responsive: [
    {
      breakpoint: 991,
      options: {
        chart: {
          height: 140,
        },
      },
    },
    {
      breakpoint: 768,
      options: {
        chart: {
          height: 120,
        },
      },
    },
    {
      breakpoint: 576,
      options: {
        chart: {
          height: 150,
        },
      },
    },
    {
      breakpoint: 480,
      options: {
        chart: {
          height: 120,
        },
      },
    },
  ],
};
var chart = new ApexCharts(document.querySelector("#stock-value"), options);
chart.render();

// beyo line start
var options = {
  series: [
    {
      name: "Net Profit",
      data: [30, 70, 40, 50, 70, 50, 90],
    },
    {
      name: "Revenue",
      data: [60, 40, 30, 60, 80, 70, 75],
    },
    {
      name: "Free Cash Flow",
      data: [40, 60, 35, 90, 60, 60, 60],
    },
  ],
  chart: {
    type: "bar",
    height: 270,
    toolbar: {
      show: false,
    },
  },
  plotOptions: {
    bar: {
      horizontal: false,
      borderRadius: 6,
      columnWidth: "55px",
    },
  },
  dataLabels: {
    enabled: false,
  },
  stroke: {
    show: true,
    width: 2,
    colors: ["transparent"],
  },

  grid: {
    show: false,
    xaxis: {
      lines: {
        show: true,
      },
    },
    yaxis: {
      lines: {
        show: false,
      },
    },
  },
  yaxis: {
    show: false,
    labels: {
      show: false,
    },
    axisTicks: {
      show: false,
    },
  },
  xaxis: {
    show: false,
    labels: {
      show: false,
    },
    axisTicks: {
      show: false,
    },
  },
  states: {
    hover: {
      filter: {
        type: "darken",
        value: 1,
      },
    },
  },
  tooltip: {
    marker: {
      show: false,
    },
    fixed: {
      enabled: false,
      position: "bottomRight",
      offsetX: 0,
      offsetY: 0,
    },
  },
  fill: {
    opacity: 1,
  },
  legend: {
    show: false,
  },
  colors: ["#B7B1D7", "#B7B1D7", "#FFFFFF"],
};
var chart = new ApexCharts(document.querySelector("#beyo-line"), options);
chart.render();

// investment chart start
var options = {
  series: [
    {
      name: "Desktops",
      data: [5, 20, 5, 50, 25, 50, 20, 60],
    },
  ],
  chart: {
    height: 108,
    type: "line",
    zoom: {
      enabled: false,
    },
    toolbar: {
      show: false,
    },
  },
  dataLabels: {
    enabled: false,
  },
  stroke: {
    curve: "smooth",
  },
  legend: {
    show: false,
  },
  grid: {
    show: false,
  },
  colors: [KohoAdminConfig.primary],
  xaxis: {
    axisBorder: {
      show: false,
    },
    labels: {
      show: false,
    },
    axisTicks: {
      show: false,
    },
    crosshairs: {
      show: true,
      width: 1,
      position: "back",
      stroke: {
        color: KohoAdminConfig.primary,
        width: 1,
        dashArray: 5,
      },
    },
    tooltip:{
      enabled: false,
    },
  },
  tooltip: {
    marker: {
      show: false,
    },
    fixed: {
      enabled: false,
      position: "bottomRight",
      offsetX: 0,
      offsetY: 0,
    },
  },
  yaxis: {
    labels: {
      show: false,
    },
  },
};

var chart = new ApexCharts(document.querySelector("#invest-chart"), options);
chart.render();

// gain chart start
var options = {
  series: [
    {
      name: "Desktops",
      data: [20, 10, 20, 10, 20, 15, 25],
    },
  ],
  chart: {
    height: 108,
    type: "line",
    zoom: {
      enabled: false,
    },
    toolbar: {
      show: false,
    },
  },
  dataLabels: {
    enabled: false,
  },
  stroke: {
    curve: "smooth",
  },
  legend: {
    show: false,
  },
  grid: {
    show: false,
  },
  colors: [KohoAdminConfig.secondary],
  xaxis: {
    axisBorder: {
      show: false,
    },
    labels: {
      show: false,
    },
    axisTicks: {
      show: false,
    },
    crosshairs: {
      show: true,
      width: 1,
      position: "back",
      stroke: {
        color: KohoAdminConfig.secondary,
        width: 1,
        dashArray: 5,
      },
    },
    tooltip:{
      enabled: false,
    },
  },
  yaxis: {
    labels: {
      show: false,
    },
  },
  tooltip: {
    marker: {
      show: false,
    },
    fixed: {
      enabled: false,
      position: "bottomRight",
      offsetX: 0,
      offsetY: 0,
    },
  },
};

var chart = new ApexCharts(document.querySelector("#gain-chart"), options);
chart.render();

// profit chart start
var options = {
  series: [
    {
      name: "Desktops",
      data: [20, 15, 20, 15, 18, 14, 20, 15],
    },
  ],
  chart: {
    height: 108,
    type: "line",
    zoom: {
      enabled: false,
    },
    toolbar: {
      show: false,
    },
  },
  dataLabels: {
    enabled: false,
  },
  stroke: {
    curve: "smooth",
  },
  legend: {
    show: false,
  },
  grid: {
    show: false,
  },
  colors: [KohoAdminConfig.success],
  xaxis: {
    axisBorder: {
      show: false,
    },
    labels: {
      show: false,
    },
    axisTicks: {
      show: false,
    },
    crosshairs: {
      show: true,
      width: 1,
      position: "back",
      stroke: {
        color: KohoAdminConfig.success,
        width: 1,
        dashArray: 5,
      },
    },
    tooltip:{
      enabled: false,
    },
  },
  yaxis: {
    labels: {
      show: false,
    },
  },
  tooltip: {
    marker: {
      show: false,
    },
    fixed: {
      enabled: false,
      position: "bottomRight",
      offsetX: 0,
      offsetY: 0,
    },
  },
};

var chart = new ApexCharts(document.querySelector("#profit-chart"), options);
chart.render();
