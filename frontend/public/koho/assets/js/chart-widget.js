(function ($) {
  "use strict";
  /*Line chart*/
  var optionslinechart = {
    chart: {
      toolbar: {
        show: false,
      },
      height: 170,
      type: "area",
    },
    dataLabels: {
      enabled: false,
    },
    stroke: {
      curve: "smooth",
    },
    xaxis: {
      show: false,
      type: "datetime",
      categories: [
        "2018-09-19T00:00:00",
        "2018-09-19T01:30:00",
        "2018-09-19T02:30:00",
        "2018-09-19T03:30:00",
        "2018-09-19T04:30:00",
        "2018-09-19T05:30:00",
        "2018-09-19T06:30:00",
      ],
      labels: {
        show: false,
      },
      axisBorder: {
        show: false,
      },
    },
    yaxis: {
      show: false,
      labels: {
        show: false,
      },
      axisBorder: {
        show: false,
      },
    },
    grid: {
      show: false,
      padding: {
        left: 0,
        right: 0,
        bottom: -40,
      },
    },
    fill: {
      type: "gradient",
      gradient: {
        shade: "light",
        type: "vertical",
        shadeIntensity: 0.4,
        inverseColors: false,
        opacityFrom: 0.8,
        opacityTo: 0.2,
        stops: [0, 100],
      },
    },
    colors: [KohoAdminConfig.primary],

    series: [
      {
        data: [4, 6, 8, 6, 10, 12, 14],
      },
    ],
    tooltip: {
      x: {
        format: "dd/MM/yy HH:mm",
      },
    },
  };

  var chartlinechart = new ApexCharts(
    document.querySelector("#chart-widget1"),
    optionslinechart
  );

  chartlinechart.render();

  /*Line chart2*/
  var optionslinechart2 = {
    chart: {
      toolbar: {
        show: false,
      },
      height: 170,
      type: "area",
    },
    dataLabels: {
      enabled: false,
    },
    stroke: {
      curve: "smooth",
    },
    xaxis: {
      show: false,
      type: "datetime",
      categories: [
        "2018-09-19T00:00:00",
        "2018-09-19T01:30:00",
        "2018-09-19T02:30:00",
        "2018-09-19T03:30:00",
        "2018-09-19T04:30:00",
        "2018-09-19T05:30:00",
        "2018-09-19T06:30:00",
      ],
      labels: {
        show: false,
      },
      axisBorder: {
        show: false,
      },
    },
    yaxis: {
      show: false,
      labels: {
        show: false,
      },
      axisBorder: {
        show: false,
      },
    },
    grid: {
      show: false,
      padding: {
        left: 0,
        right: 0,
        bottom: -40,
      },
    },
    fill: {
      type: "gradient",
      gradient: {
        shade: "light",
        type: "vertical",
        shadeIntensity: 0.4,
        inverseColors: false,
        opacityFrom: 0.8,
        opacityTo: 0.2,
        stops: [0, 100],
      },
    },
    colors: [KohoAdminConfig.secondary],
    series: [
      {
        name: "series1",
        data: [6, 2, 10, 8, 4, 12, 14],
      },
    ],
    tooltip: {
      x: {
        format: "dd/MM/yy HH:mm",
      },
    },
  };

  var chartlinechart2 = new ApexCharts(
    document.querySelector("#chart-widget2"),
    optionslinechart2
  );
  chartlinechart2.render();

  /*Line chart3*/
  var optionslinechart3 = {
    chart: {
      toolbar: {
        show: false,
      },
      height: 170,
      type: "area",
    },
    dataLabels: {
      enabled: false,
    },
    stroke: {
      curve: "smooth",
    },
    xaxis: {
      show: false,
      type: "datetime",
      categories: [
        "2018-09-19T00:00:00",
        "2018-09-19T01:30:00",
        "2018-09-19T02:30:00",
        "2018-09-19T03:30:00",
        "2018-09-19T04:30:00",
        "2018-09-19T05:30:00",
        "2018-09-19T06:30:00",
      ],
      labels: {
        show: false,
      },
      axisBorder: {
        show: false,
      },
    },
    yaxis: {
      show: false,
      labels: {
        show: false,
      },
      axisBorder: {
        show: false,
      },
    },
    grid: {
      show: false,
      padding: {
        left: 0,
        right: 0,
        bottom: -40,
      },
    },
    fill: {
      colors: ["#67C100"],
      type: "gradient",
      gradient: {
        shade: "light",
        type: "vertical",
        shadeIntensity: 0.4,
        inverseColors: false,
        opacityFrom: 0.8,
        opacityTo: 0.2,
        stops: [0, 100],
      },
    },
    colors: ["#67C100"],

    series: [
      {
        data: [16, 14, 10, 12, 10, 12, 8],
      },
    ],
    tooltip: {
      x: {
        format: "dd/MM/yy HH:mm",
      },
    },
  };

  var chartlinechart3 = new ApexCharts(
    document.querySelector("#chart-widget3"),
    optionslinechart3
  );
  chartlinechart3.render();

  // column chart
  var optionscolumnchart = {
    series: [
      {
        name: "Net Profit",
        data: [44, 55, 57, 56, 61, 58, 63, 60, 66],
      },
      {
        name: "Revenue",
        data: [76, 85, 101, 98, 87, 105, 91, 114, 94],
      },
      {
        name: "Free Cash Flow",
        data: [35, 41, 36, 26, 45, 48, 52, 53, 41],
      },
    ],

    legend: {
      show: false,
    },
    chart: {
      type: "bar",
      height: 380,
    },
    plotOptions: {
      bar: {
        radius: 10,
        horizontal: false,
        columnWidth: "55%",
        endingShape: "rounded",
      },
    },
    dataLabels: {
      enabled: false,
    },
    stroke: {
      show: true,
      colors: ["transparent"],
      curve: "smooth",
      lineCap: "butt",
    },
    grid: {
      show: false,
      padding: {
        left: 0,
        right: 0,
      },
    },
    xaxis: {
      categories: [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
      ],
    },
    yaxis: {
      title: {
        text: "$ (thousands)",
      },
    },
    fill: {
      colors: [KohoAdminConfig.primary, KohoAdminConfig.secondary, "#51bb25"],
      type: "gradient",
      gradient: {
        shade: "light",
        type: "vertical",
        shadeIntensity: 0.1,
        inverseColors: false,
        opacityFrom: 1,
        opacityTo: 0.9,
        stops: [0, 100],
      },
    },

    tooltip: {
      y: {
        formatter: function (val) {
          return "$ " + val + " thousands";
        },
      },
    },
    responsive: [
      {
        breakpoint: 575,
        options: {
          chart: {
            height: 280,
          },
        },
      },
    ],
  };

  var chartcolumnchart = new ApexCharts(
    document.querySelector("#chart-widget4"),
    optionscolumnchart
  );
  chartcolumnchart.render();

  // earning chart
  var options = {
    series: [70],
    chart: {
      height: 350,
      type: "radialBar",
    },
    plotOptions: {
      radialBar: {
        hollow: {
          margin: 15,
          size: "70%",
          image: "../assets/images/email-template/success.png",
          imageWidth: 64,
          imageHeight: 64,
          imageClipped: false,
        },
        dataLabels: {
          name: {
            show: false,
            color: "#fff",
          },
          value: {
            show: true,
            color: "#333",
            offsetY: 70,
            fontSize: "22px",
          },
        },
      },
    },
    fill: {
      type: "image",
      image: {
        src: ["../assets/images/user-card/5.jpg"],
      },
    },
    stroke: {
      lineCap: "round",
    },
    labels: ["Volatility"],
    responsive: [
      {
        breakpoint: 420,
        options: {
          chart: {
            height: 280,
          },
        },
      },
    ],
  };

  var chart = new ApexCharts(document.querySelector("#chart-widget5"), options);
  chart.render();

  // product chart
  var optionsproductchart = {
    chart: {
      height: 320,
      type: "line",
    },
    stroke: {
      curve: "smooth",
    },

    series: [
      {
        name: "TEAM A",
        type: "area",
        data: [44, 55, 31, 47, 31, 43, 26, 41, 31, 47, 33],
      },
      {
        name: "TEAM B",
        type: "line",
        data: [55, 69, 45, 61, 43, 54, 37, 52, 44, 61, 43],
      },
    ],
    fill: {
      colors: [KohoAdminConfig.primary, KohoAdminConfig.secondary],
      type: "gradient",
      gradient: {
        shade: "light",
        type: "vertical",
        shadeIntensity: 0.4,
        inverseColors: false,
        opacityFrom: 0.9,
        opacityTo: 0.8,
        stops: [0, 100],
      },
    },

    colors: [KohoAdminConfig.primary, KohoAdminConfig.secondary],
    labels: [
      "01",
      "02",
      "03",
      "04",
      "05",
      "06",
      "07",
      "08",
      "09 ",
      "10",
      "11",
      "12",
    ],
    markers: {
      size: 0,
    },
    yaxis: [
      {
        title: {
          text: "Series A",
        },
      },
      {
        opposite: true,
        title: {
          text: "Series B",
        },
      },
    ],
    tooltip: {
      shared: true,
      intersect: false,
      y: {
        formatter: function (y) {
          if (typeof y !== "undefined") {
            return y.toFixed(0) + " points";
          }
          return y;
        },
      },
    },
  };

  var chartproductchart = new ApexCharts(
    document.querySelector("#chart-widget6"),
    optionsproductchart
  );
  chartproductchart.render();

  // Turnover chart
  var optionsturnoverchart = {
    chart: {
      height: 320,
      type: "area",
      zoom: {
        enabled: false,
      },
    },
    dataLabels: {
      enabled: false,
    },
    stroke: {
      curve: "straight",
    },
    fill: {
      colors: [KohoAdminConfig.primary],
      type: "gradient",
      gradient: {
        shade: "light",
        type: "vertical",
        shadeIntensity: 0.4,
        inverseColors: false,
        opacityFrom: 0.9,
        opacityTo: 0.8,
        stops: [0, 100],
      },
    },

    series: [
      {
        name: "STOCK ABC",
        data: series.monthDataSeries1.prices,
      },
    ],
    title: {
      text: "Fundamental Analysis of Stocks",
      align: "left",
    },
    colors: [KohoAdminConfig.primary],
    labels: series.monthDataSeries1.dates,
    xaxis: {
      type: "datetime",
    },
    yaxis: {
      opposite: false,
    },
    legend: {
      horizontalAlign: "left",
    },
  };

  var chartturnoverchart = new ApexCharts(
    document.querySelector("#chart-widget7"),
    optionsturnoverchart
  );
  chartturnoverchart.render();

  // sales chart
  var optionssaleschart = {
    fill: {
      type: "gradient",
      gradient: {
        shade: "dark",
        type: "Reflected",
        shadeIntensity: 0.1,
        inverseColors: false,
        opacityFrom: 1,
        opacityTo: 0.8,
        stops: [0, 100],
      },
    },
    colors: [KohoAdminConfig.primary, KohoAdminConfig.secondary, "#51bb25"],
    chart: {
      height: 300,
      type: "radar",
      dropShadow: {
        enabled: true,
        blur: 1,
        left: 1,
        top: 1,
      },
    },
    series: [
      {
        name: "Series 1",
        data: [80, 50, 30, 40, 100, 20],
      },
      {
        name: "Series 2",
        data: [20, 30, 40, 80, 20, 80],
      },
      {
        name: "Series 3",
        data: [44, 76, 78, 13, 43, 10],
      },
    ],
    title: {
      text: "Radar Chart - Multi Series",
    },
    stroke: {
      width: 0,
    },
    markers: {
      size: 0,
    },
    labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
  };

  var chartsaleschart = new ApexCharts(
    document.querySelector("#chart-widget8"),
    optionssaleschart
  );
  chartsaleschart.render();

  // user chart
  function generateData(baseval, count, yrange) {
    var i = 0;
    var series = [];
    while (i < count) {
      var x = Math.floor(Math.random() * (750 - 1 + 1)) + 1;
      var y =
        Math.floor(Math.random() * (yrange.max - yrange.min + 1)) + yrange.min;
      var z = Math.floor(Math.random() * (75 - 15 + 1)) + 15;

      series.push([x, y, z]);
      baseval += 86400000;
      i++;
    }
    return series;
  }
  var optionsuserchart = {
    chart: {
      toolbar: {
        show: false,
      },
      height: 320,
      type: "bubble",
    },
    dataLabels: {
      enabled: false,
    },
    series: [
      {
        name: "Bubble1",
        data: generateData(new Date("11 Feb 2017 GMT").getTime(), 20, {
          min: 10,
          max: 60,
        }),
      },
      {
        name: "Bubble2",
        data: generateData(new Date("11 Feb 2017 GMT").getTime(), 20, {
          min: 10,
          max: 60,
        }),
      },
      {
        name: "Bubble3",
        data: generateData(new Date("11 Feb 2017 GMT").getTime(), 20, {
          min: 10,
          max: 60,
        }),
      },
      {
        name: "Bubble4",
        data: generateData(new Date("11 Feb 2017 GMT").getTime(), 20, {
          min: 10,
          max: 60,
        }),
      },
    ],
    fill: {
      type: "gradient",
      gradient: {
        shade: "dark",
        type: "horizontal",
        shadeIntensity: 0.4,
        inverseColors: false,
        opacityFrom: 1,
        opacityTo: 0.7,
        stops: [0, 100],
      },
    },
    colors: [
      KohoAdminConfig.primary,
      KohoAdminConfig.secondary,
      "#51bb25",
      "#544fff",
    ],
    title: {
      text: "Simple Bubble Chart",
    },
    xaxis: {
      tickAmount: 12,
      type: "category",
    },
    yaxis: {
      max: 70,
    },
  };
  var chartuserchart = new ApexCharts(
    document.querySelector("#chart-widget9"),
    optionsuserchart
  );
  chartuserchart.render();

  // browser-candlestick chart
  var optionscandlestickchart = {
    chart: {
      toolbar: {
        show: false,
      },
      height: 500,
      type: "candlestick",
    },
    plotOptions: {
      candlestick: {
        colors: {
          upward: KohoAdminConfig.primary,
          downward: KohoAdminConfig.secondary,
        },
      },
    },
    fill: {
      opacity: 0.9,
      colors: ["#3e5fce"],
    },

    series: [
      {
        data: [
          {
            x: new Date(1538778600000),
            y: [6629.81, 6650.5, 6623.04, 6633.33],
          },
          {
            x: new Date(1538780400000),
            y: [6632.01, 6643.59, 6620, 6630.11],
          },
          {
            x: new Date(1538782200000),
            y: [6630.71, 6648.95, 6623.34, 6635.65],
          },
          {
            x: new Date(1538784000000),
            y: [6635.65, 6651, 6629.67, 6638.24],
          },
          {
            x: new Date(1538785800000),
            y: [6638.24, 6640, 6620, 6624.47],
          },
          {
            x: new Date(1538787600000),
            y: [6624.53, 6636.03, 6621.68, 6624.31],
          },
          {
            x: new Date(1538789400000),
            y: [6624.61, 6632.2, 6617, 6626.02],
          },
          {
            x: new Date(1538791200000),
            y: [6627, 6627.62, 6584.22, 6603.02],
          },
          {
            x: new Date(1538793000000),
            y: [6605, 6608.03, 6598.95, 6604.01],
          },
          {
            x: new Date(1538794800000),
            y: [6604.5, 6614.4, 6602.26, 6608.02],
          },
          {
            x: new Date(1538796600000),
            y: [6608.02, 6610.68, 6601.99, 6608.91],
          },
          {
            x: new Date(1538798400000),
            y: [6608.91, 6618.99, 6608.01, 6612],
          },
          {
            x: new Date(1538800200000),
            y: [6612, 6615.13, 6605.09, 6612],
          },
          {
            x: new Date(1538802000000),
            y: [6612, 6624.12, 6608.43, 6622.95],
          },
          {
            x: new Date(1538803800000),
            y: [6623.91, 6623.91, 6615, 6615.67],
          },
          {
            x: new Date(1538805600000),
            y: [6618.69, 6618.74, 6610, 6610.4],
          },
          {
            x: new Date(1538807400000),
            y: [6611, 6622.78, 6610.4, 6614.9],
          },
          {
            x: new Date(1538809200000),
            y: [6614.9, 6626.2, 6613.33, 6623.45],
          },
          {
            x: new Date(1538811000000),
            y: [6623.48, 6627, 6618.38, 6620.35],
          },
          {
            x: new Date(1538812800000),
            y: [6619.43, 6620.35, 6610.05, 6615.53],
          },
          {
            x: new Date(1538814600000),
            y: [6615.53, 6617.93, 6610, 6615.19],
          },
          {
            x: new Date(1538816400000),
            y: [6615.19, 6621.6, 6608.2, 6620],
          },
          {
            x: new Date(1538818200000),
            y: [6619.54, 6625.17, 6614.15, 6620],
          },
          {
            x: new Date(1538820000000),
            y: [6620.33, 6634.15, 6617.24, 6624.61],
          },
          {
            x: new Date(1538821800000),
            y: [6625.95, 6626, 6611.66, 6617.58],
          },
          {
            x: new Date(1538823600000),
            y: [6619, 6625.97, 6595.27, 6598.86],
          },
          {
            x: new Date(1538825400000),
            y: [6598.86, 6598.88, 6570, 6587.16],
          },
          {
            x: new Date(1538827200000),
            y: [6588.86, 6600, 6580, 6593.4],
          },
          {
            x: new Date(1538829000000),
            y: [6593.99, 6598.89, 6585, 6587.81],
          },
          {
            x: new Date(1538830800000),
            y: [6587.81, 6592.73, 6567.14, 6578],
          },
          {
            x: new Date(1538832600000),
            y: [6578.35, 6581.72, 6567.39, 6579],
          },
          {
            x: new Date(1538834400000),
            y: [6579.38, 6580.92, 6566.77, 6575.96],
          },
          {
            x: new Date(1538836200000),
            y: [6575.96, 6589, 6571.77, 6588.92],
          },
          {
            x: new Date(1538838000000),
            y: [6588.92, 6594, 6577.55, 6589.22],
          },
          {
            x: new Date(1538839800000),
            y: [6589.3, 6598.89, 6589.1, 6596.08],
          },
          {
            x: new Date(1538841600000),
            y: [6597.5, 6600, 6588.39, 6596.25],
          },
          {
            x: new Date(1538843400000),
            y: [6598.03, 6600, 6588.73, 6595.97],
          },
          {
            x: new Date(1538845200000),
            y: [6595.97, 6602.01, 6588.17, 6602],
          },
          {
            x: new Date(1538847000000),
            y: [6602, 6607, 6596.51, 6599.95],
          },
          {
            x: new Date(1538848800000),
            y: [6600.63, 6601.21, 6590.39, 6591.02],
          },
          {
            x: new Date(1538850600000),
            y: [6591.02, 6603.08, 6591, 6591],
          },
          {
            x: new Date(1538852400000),
            y: [6591, 6601.32, 6585, 6592],
          },
          {
            x: new Date(1538854200000),
            y: [6593.13, 6596.01, 6590, 6593.34],
          },
          {
            x: new Date(1538856000000),
            y: [6593.34, 6604.76, 6582.63, 6593.86],
          },
          {
            x: new Date(1538857800000),
            y: [6593.86, 6604.28, 6586.57, 6600.01],
          },
          {
            x: new Date(1538859600000),
            y: [6601.81, 6603.21, 6592.78, 6596.25],
          },
          {
            x: new Date(1538861400000),
            y: [6596.25, 6604.2, 6590, 6602.99],
          },
          {
            x: new Date(1538863200000),
            y: [6602.99, 6606, 6584.99, 6587.81],
          },
          {
            x: new Date(1538865000000),
            y: [6587.81, 6595, 6583.27, 6591.96],
          },
          {
            x: new Date(1538866800000),
            y: [6591.97, 6596.07, 6585, 6588.39],
          },
          {
            x: new Date(1538868600000),
            y: [6587.6, 6598.21, 6587.6, 6594.27],
          },
          {
            x: new Date(1538870400000),
            y: [6596.44, 6601, 6590, 6596.55],
          },
          {
            x: new Date(1538872200000),
            y: [6598.91, 6605, 6596.61, 6600.02],
          },
          {
            x: new Date(1538874000000),
            y: [6600.55, 6605, 6589.14, 6593.01],
          },
          {
            x: new Date(1538875800000),
            y: [6593.15, 6605, 6592, 6603.06],
          },
          {
            x: new Date(1538877600000),
            y: [6603.07, 6604.5, 6599.09, 6603.89],
          },
          {
            x: new Date(1538879400000),
            y: [6604.44, 6604.44, 6600, 6603.5],
          },
          {
            x: new Date(1538881200000),
            y: [6603.5, 6603.99, 6597.5, 6603.86],
          },
          {
            x: new Date(1538883000000),
            y: [6603.85, 6605, 6600, 6604.07],
          },
          {
            x: new Date(1538884800000),
            y: [6604.98, 6606, 6604.07, 6606],
          },
        ],
      },
    ],
    title: {
      text: "CandleStick Chart",
      align: "left",
    },
    xaxis: {
      type: "datetime",
    },
    yaxis: {
      tooltip: {
        enabled: true,
      },
    },
  };

  var chartcandlestickchart = new ApexCharts(
    document.querySelector("#chart-widget13"),
    optionscandlestickchart
  );
  chartcandlestickchart.render();

  var trigoStrength = 3;
  var iteration = 11;

  function getRandom() {
    var i = iteration;
    return (
      (Math.sin(i / trigoStrength) * (i / trigoStrength) +
        i / trigoStrength +
        1) *
      (trigoStrength * 2)
    );
  }

  function getRangeRandom(yrange) {
    return (
      Math.floor(Math.random() * (yrange.max - yrange.min + 1)) + yrange.min
    );
  }

  function generateMinuteWiseTimeSeries(baseval, count, yrange) {
    var i = 0;
    var series = [];
    while (i < count) {
      var x = baseval;
      var y =
        (Math.sin(i / trigoStrength) * (i / trigoStrength) +
          i / trigoStrength +
          1) *
        (trigoStrength * 2);

      series.push([x, y]);
      baseval += 300000;
      i++;
    }
    return series;
  }

  function getNewData(baseval, yrange) {
    var newTime = baseval + 300000;
    return {
      x: newTime,
      y: Math.floor(Math.random() * (yrange.max - yrange.min + 1)) + yrange.min,
    };
  }

  // Finance Chart

  var optionsColumn = {
    chart: {
      height: 350,
      type: "bar",
      animations: {
        enabled: true,
        easing: "linear",
        dynamicAnimation: {
          speed: 1000,
        },
      },

      events: {
        animationEnd: function (chartCtx) {
          const newData = chartCtx.w.config.series[0].data.slice();
          newData.shift();
          window.setTimeout(function () {
            chartCtx.updateOptions(
              {
                series: [
                  {
                    data: newData,
                  },
                ],
                xaxis: {
                  min: chartCtx.minX,
                  max: chartCtx.maxX,
                },
                subtitle: {
                  text:
                    parseInt(getRangeRandom({ min: 1, max: 20 })).toString() +
                    "%",
                },
              },
              false,
              false
            );
          }, 300);
        },
      },
      toolbar: {
        show: false,
      },
      zoom: {
        enabled: false,
      },
    },
    dataLabels: {
      enabled: false,
    },
    stroke: {
      width: 0,
    },
    series: [
      {
        name: "Load Average",
        data: generateMinuteWiseTimeSeries(
          new Date("12/12/2016 00:20:00").getTime(),
          12,
          {
            min: 10,
            max: 110,
          }
        ),
      },
    ],
    title: {
      text: "Load Average",
      align: "left",
      style: {
        fontSize: "12px",
      },
    },
    subtitle: {
      text: "20%",
      floating: true,
      align: "right",
      offsetY: 0,
      style: {
        fontSize: "22px",
      },
    },

    fill: {
      colors: [KohoAdminConfig.primary],
      type: "gradient",
      gradient: {
        shade: "light",
        type: "vertical",
        shadeIntensity: 0.4,
        inverseColors: false,
        opacityFrom: 1,
        opacityTo: 0.8,
        stops: [0, 100],
      },
    },
    xaxis: {
      type: "datetime",
      range: 2700000,
    },
    yaxis: {
      decimalsInFloat: 1,
    },
    legend: {
      show: true,
    },
  };

  var chartColumn = new ApexCharts(
    document.querySelector("#columnchart"),
    optionsColumn
  );
  chartColumn.render();

  // Order Status Chart

  var optionsLine = {
    chart: {
      height: 350,
      type: "line",
      stacked: true,
      animations: {
        enabled: true,
        easing: "linear",
        dynamicAnimation: {
          speed: 1000,
        },
      },
      events: {
        animationEnd: function (chartCtx) {
          const newData1 = chartCtx.w.config.series[0].data.slice();
          newData1.shift();
          const newData2 = chartCtx.w.config.series[1].data.slice();
          newData2.shift();
          window.setTimeout(function () {
            chartCtx.updateOptions(
              {
                series: [
                  {
                    data: newData1,
                  },
                  {
                    data: newData2,
                  },
                ],
                subtitle: {
                  text: parseInt(getRandom() * Math.random()).toString(),
                },
              },
              false,
              false
            );
          }, 300);
        },
      },
      toolbar: {
        show: false,
      },
      zoom: {
        enabled: false,
      },
    },
    dataLabels: {
      enabled: false,
    },
    stroke: {
      curve: "straight",
      width: 5,
    },
    grid: {
      padding: {
        left: 0,
        right: 0,
      },
    },
    fill: {
      opacity: 0.9,
    },
    colors: [KohoAdminConfig.primary, KohoAdminConfig.secondary],
    markers: {
      size: 0,
      hover: {
        size: 0,
      },
    },
    series: [
      {
        name: "Running",
        data: generateMinuteWiseTimeSeries(
          new Date("12/12/2016 00:20:00").getTime(),
          12,
          {
            min: 30,
            max: 110,
          }
        ),
      },
      {
        name: "Waiting",
        data: generateMinuteWiseTimeSeries(
          new Date("12/12/2016 00:20:00").getTime(),
          12,
          {
            min: 30,
            max: 110,
          }
        ),
      },
    ],
    xaxis: {
      type: "datetime",
      range: 2700000,
    },
    yaxis: {
      decimalsInFloat: 1,
    },
    title: {
      text: "Processes",
      align: "left",
      style: {
        fontSize: "12px",
      },
    },
    subtitle: {
      text: "20",
      floating: true,
      align: "right",
      offsetY: 0,
      style: {
        fontSize: "22px",
      },
    },
    legend: {
      show: true,
      floating: true,
      horizontalAlign: "left",
      onItemClick: {
        toggleDataSeries: false,
      },
      position: "top",
      offsetY: -28,
      offsetX: 60,
    },
  };

  var chartLine = new ApexCharts(
    document.querySelector("#linechart"),
    optionsLine
  );
  chartLine.render();

  // Skill Status CHart

  var optionsCircle = {
    chart: {
      type: "radialBar",
      height: 385,
      offsetY: -20,
      offsetX: 0,
    },
    plotOptions: {
      radialBar: {
        size: undefined,
        inverseOrder: false,
        hollow: {
          margin: 5,
          size: "48%",
          background: "transparent",
        },
        track: {
          show: true,
          background: "#ffffff",
          strokeWidth: "10%",
          opacity: 1,
          margin: 3,
        },
      },
    },
    series: [71, 63],
    labels: ["Device 1", "Device 2"],
    legend: {
      show: false,
    },
    fill: {
      type: "gradient",
      gradient: {
        shade: "light",
        type: "horizontal",
        shadeIntensity: 0.5,
        inverseColors: true,
        opacityFrom: 1,
        opacityTo: 1,
        stops: [0, 100],
      },
    },
    responsive: [
      {
        breakpoint: 420,
        options: {
          chart: {
            height: 320,
            offsetY: 20,
            offsetX: 0,
          },
        },
      },
    ],
    colors: [KohoAdminConfig.primary, KohoAdminConfig.secondary],
  };

  var chartCircle = new ApexCharts(
    document.querySelector("#circlechart"),
    optionsCircle
  );
  chartCircle.render();

  // Order Status Progress Bar Chart

  var optionsProgress1 = {
    chart: {
      height: 70,
      type: "bar",
      stacked: true,
      sparkline: {
        enabled: true,
      },
    },
    plotOptions: {
      bar: {
        horizontal: true,
        barHeight: "20%",
        colors: {
          backgroundBarColors: ["#ffffff"],
        },
      },
    },
    colors: [KohoAdminConfig.primary],
    stroke: {
      width: 0,
    },
    fill: {
      colors: [KohoAdminConfig.primary],
      type: "gradient",
      gradient: {
        gradientToColors: [KohoAdminConfig.primary],
      },
    },
    series: [
      {
        name: "Process 1",
        data: [44],
      },
    ],
    title: {
      floating: true,
      offsetX: -10,
      offsetY: 5,
      text: "Process 1",
    },
    subtitle: {
      floating: true,
      align: "right",
      offsetY: 0,
      text: "50%",
      style: {
        fontSize: "20px",
      },
    },
    tooltip: {
      enabled: false,
    },
    xaxis: {
      categories: ["Process 1"],
    },
    yaxis: {
      max: 100,
    },
    fill: {
      opacity: 1,
    },
  };

  var chartProgress1 = new ApexCharts(
    document.querySelector("#progress1"),
    optionsProgress1
  );
  chartProgress1.render();

  var optionsProgress2 = {
    chart: {
      height: 70,
      type: "bar",
      stacked: true,
      sparkline: {
        enabled: true,
      },
    },
    plotOptions: {
      bar: {
        horizontal: true,
        barHeight: "20%",
        colors: {
          backgroundBarColors: ["#ffffff"],
        },
      },
    },
    colors: ["#3e5fce"],
    stroke: {
      width: 0,
    },
    series: [
      {
        name: "Process 2",
        data: [80],
      },
    ],
    title: {
      floating: true,
      offsetX: -10,
      offsetY: 5,
      text: "Process 2",
    },
    subtitle: {
      floating: true,
      align: "right",
      offsetY: 0,
      text: "80%",
      style: {
        fontSize: "20px",
      },
    },
    tooltip: {
      enabled: false,
    },
    xaxis: {
      categories: ["Process 2"],
    },
    yaxis: {
      max: 100,
    },
    fill: {
      colors: ["#3e5fce"],
      type: "gradient",
      gradient: {
        inverseColors: false,
        gradientToColors: ["#3e5fce"],
      },
    },
  };

  var chartProgress2 = new ApexCharts(
    document.querySelector("#progress2"),
    optionsProgress2
  );
  chartProgress2.render();

  var optionsProgress3 = {
    chart: {
      height: 70,
      type: "bar",
      stacked: true,
      sparkline: {
        enabled: true,
      },
    },
    plotOptions: {
      bar: {
        horizontal: true,
        barHeight: "20%",
        colors: {
          backgroundBarColors: ["#ffffff"],
        },
      },
    },
    colors: ["#51bb25"],
    stroke: {
      width: 0,
    },
    series: [
      {
        name: "Process 3",
        data: [74],
      },
    ],
    fill: {
      colors: ["#51bb25"],
      type: "gradient",
      gradient: {
        gradientToColors: ["#51bb25"],
      },
    },
    title: {
      floating: true,
      offsetX: -10,
      offsetY: 5,
      text: "Process 3",
    },
    subtitle: {
      floating: true,
      align: "right",
      offsetY: 0,
      text: "74%",
      style: {
        fontSize: "20px",
      },
    },
    tooltip: {
      enabled: false,
    },
    xaxis: {
      categories: ["Process 3"],
    },
    yaxis: {
      max: 100,
    },
  };

  var chartProgress3 = new ApexCharts(
    document.querySelector("#progress3"),
    optionsProgress3
  );
  chartProgress3.render();

  var optionsProgress4 = {
    chart: {
      height: 70,
      type: "bar",
      stacked: true,
      sparkline: {
        enabled: true,
      },
    },
    plotOptions: {
      bar: {
        horizontal: true,
        barHeight: "20%",
        colors: {
          backgroundBarColors: ["#ffffff"],
        },
      },
    },
    colors: ["#544fff"],
    stroke: {
      width: 0,
    },
    series: [
      {
        name: "Process 4",
        data: [74],
      },
    ],
    fill: {
      colors: ["#544fff"],
      type: "gradient",
      gradient: {
        gradientToColors: ["#544fff"],
      },
    },
    title: {
      floating: true,
      offsetX: -10,
      offsetY: 5,
      text: "Process 4",
    },
    subtitle: {
      floating: true,
      align: "right",
      offsetY: 0,
      text: "74%",
      style: {
        fontSize: "20px",
      },
    },
    tooltip: {
      enabled: false,
    },
    xaxis: {
      categories: ["Process 4"],
    },
    yaxis: {
      max: 100,
    },
  };

  var chartProgress4 = new ApexCharts(
    document.querySelector("#progress4"),
    optionsProgress4
  );
  chartProgress4.render();

  var optionsProgress5 = {
    chart: {
      height: 70,
      type: "bar",
      stacked: true,
      sparkline: {
        enabled: true,
      },
    },
    plotOptions: {
      bar: {
        horizontal: true,
        barHeight: "20%",
        colors: {
          backgroundBarColors: ["#ffffff"],
        },
      },
    },
    colors: ["#fb740d"],
    stroke: {
      width: 0,
    },
    series: [
      {
        name: "Process 5",
        data: [74],
      },
    ],
    fill: {
      colors: ["#fb740d"],
      type: "gradient",
      gradient: {
        gradientToColors: ["#fb740d"],
      },
    },
    title: {
      floating: true,
      offsetX: -10,
      offsetY: 5,
      text: "Process 5",
    },
    subtitle: {
      floating: true,
      align: "right",
      offsetY: 0,
      text: "74%",
      style: {
        fontSize: "20px",
      },
    },
    tooltip: {
      enabled: false,
    },
    xaxis: {
      categories: ["Process 5"],
    },
    yaxis: {
      max: 100,
    },
  };

  var chartProgress5 = new ApexCharts(
    document.querySelector("#progress5"),
    optionsProgress5
  );
  chartProgress5.render();

  window.setInterval(function () {
    iteration++;

    chartColumn.updateSeries([
      {
        data: [
          ...chartColumn.w.config.series[0].data,
          [chartColumn.w.globals.maxX + 210000, getRandom()],
        ],
      },
    ]),
      chartLine.updateSeries([
        {
          data: [
            ...chartLine.w.config.series[0].data,
            [chartLine.w.globals.maxX + 300000, getRandom()],
          ],
        },
        {
          data: [
            ...chartLine.w.config.series[1].data,
            [chartLine.w.globals.maxX + 300000, getRandom()],
          ],
        },
      ]);

    chartCircle.updateSeries([
      getRangeRandom({ min: 10, max: 100 }),
      getRangeRandom({ min: 10, max: 100 }),
    ]);

    var p1Data = getRangeRandom({ min: 10, max: 100 });
    chartProgress1.updateOptions({
      series: [
        {
          data: [p1Data],
        },
      ],
      subtitle: {
        text: p1Data + "%",
      },
    });

    var p2Data = getRangeRandom({ min: 10, max: 100 });
    chartProgress2.updateOptions({
      series: [
        {
          data: [p2Data],
        },
      ],
      subtitle: {
        text: p2Data + "%",
      },
    });

    var p3Data = getRangeRandom({ min: 10, max: 100 });
    chartProgress3.updateOptions({
      series: [
        {
          data: [p3Data],
        },
      ],
      subtitle: {
        text: p3Data + "%",
      },
    });
  }, 3000);
})(jQuery);
