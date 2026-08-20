//Sales Chart
var options = {
  series: [
    {
      name: "Statistics",
      data: [20, 60, 50, 70, 40, 80, 20],
    },
    {
      name: "Statistics",
      data: [80, 40, 50, 30, 60, 20, 20],
    },
  ],
  chart: {
    type: "bar",
    height: 100,
    stacked: true,
    stackType: "100%",
    toolbar: {
      show: false,
    },
  },
  plotOptions: {
    bar: {
      horizontal: false,
      columnWidth: "40px",
      borderRadius: 2,
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
  states: {
    hover: {
      filter: {
        type: "darken",
        value: 1,
      },
    },
  },
  dataLabels: {
    enabled: false,
  },
  legend: {
    show: false,
  },
  colors: [KohoAdminConfig.primary, "#dad8e0"],
  xaxis: {
    show: false,
    labels: {
      show: false,
    },
    axisBorder: {
      show: false,
    },
    axisTicks: {
      show: false,
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
  responsive: [
    {
      breakpoint: 1661,
      options: {
        chart: {
          width: 80,
        },
      },
    },
    {
      breakpoint: 1365,
      options: {
        chart: {
          width: 80,
        },
      },
    },
  ],
};
var chart = new ApexCharts(document.querySelector("#sales-chart"), options);
chart.render();

//Income Chart
var options = {
  series: [
    {
      name: "Statistics",
      data: [20, 60, 50, 70, 40, 80, 20],
    },
    {
      name: "Statistics",
      data: [80, 40, 50, 30, 60, 20, 20],
    },
  ],
  chart: {
    type: "bar",
    height: 100,
    stacked: true,
    stackType: "100%",
    toolbar: {
      show: false,
    },
  },
  plotOptions: {
    bar: {
      horizontal: false,
      columnWidth: "40px",
      borderRadius: 2,
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
  states: {
    hover: {
      filter: {
        type: "darken",
        value: 1,
      },
    },
  },
  dataLabels: {
    enabled: false,
  },
  legend: {
    show: false,
  },
  colors: [KohoAdminConfig.secondary, "#faded1"],
  xaxis: {
    show: false,
    labels: {
      show: false,
    },
    axisBorder: {
      show: false,
    },
    axisTicks: {
      show: false,
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
  responsive: [
    {
      breakpoint: 1661,
      options: {
        chart: {
          width: 80,
        },
      },
    },
    {
      breakpoint: 1365,
      options: {
        chart: {
          width: 80,
        },
      },
    },
  ],
};
var chart = new ApexCharts(document.querySelector("#income-chart"), options);
chart.render();

//Order Chart
var options = {
  series: [
    {
      name: "Statistics",
      data: [20, 60, 50, 70, 40, 80, 20],
    },
    {
      name: "Statistics",
      data: [80, 40, 50, 30, 60, 20, 20],
    },
  ],
  chart: {
    type: "bar",
    height: 100,
    stacked: true,
    stackType: "100%",
    toolbar: {
      show: false,
    },
  },
  plotOptions: {
    bar: {
      horizontal: false,
      columnWidth: "40px",
      borderRadius: 2,
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
  states: {
    hover: {
      filter: {
        type: "darken",
        value: 1,
      },
    },
  },
  dataLabels: {
    enabled: false,
  },
  legend: {
    show: false,
  },
  colors: [KohoAdminConfig.primary, "#dad8e0"],
  xaxis: {
    show: false,
    labels: {
      show: false,
    },
    axisBorder: {
      show: false,
    },
    axisTicks: {
      show: false,
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
  responsive: [
    {
      breakpoint: 1661,
      options: {
        chart: {
          width: 80,
        },
      },
    },
    {
      breakpoint: 1365,
      options: {
        chart: {
          width: 80,
        },
      },
    },
  ],
};
var chart = new ApexCharts(document.querySelector("#order-chart"), options);
chart.render();

// Visitor Chart
var options = {
  series: [
    {
      name: "Statistics",
      data: [20, 60, 50, 70, 40, 80, 20],
    },
    {
      name: "Statistics",
      data: [80, 40, 50, 30, 60, 20, 20],
    },
  ],
  chart: {
    type: "bar",
    height: 100,
    stacked: true,
    stackType: "100%",
    toolbar: {
      show: false,
    },
  },
  plotOptions: {
    bar: {
      horizontal: false,
      columnWidth: "40px",
      borderRadius: 2,
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
  states: {
    hover: {
      filter: {
        type: "darken",
        value: 1,
      },
    },
  },
  dataLabels: {
    enabled: false,
  },
  legend: {
    show: false,
  },
  colors: [KohoAdminConfig.secondary, "#faded1"],
  xaxis: {
    show: false,
    labels: {
      show: false,
    },
    axisBorder: {
      show: false,
    },
    axisTicks: {
      show: false,
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
  responsive: [
    {
      breakpoint: 1661,
      options: {
        chart: {
          width: 80,
        },
      },
    },
    {
      breakpoint: 1365,
      options: {
        chart: {
          width: 80,
        },
      },
    },
  ],
};
var chart = new ApexCharts(document.querySelector("#visitor-chart"), options);
chart.render();

//Recent Chart
var options = {
  series: [
    {
      type: "line",
      data: [150, 470, 250, 380, 100, 480, 420],
    },
    {
      type: "area",
      data: [220, 160, 230, 150, 220, 130, 200],
    },
  ],
  chart: {
    height: 355,
    type: "area",
    toolbar: {
      show: false,
    },
    dropShadow: {
      enabled: true,
      left: 8,
      blur: 0,
      color: KohoAdminConfig.secondary,
      opacity: 0.1,
    },
  },
  dataLabels: {
    enabled: false,
  },
  stroke: {
    curve: "smooth",
    width: [5, 0],
    colors: [KohoAdminConfig.secondary, KohoAdminConfig.primary],
  },

  grid: {
    borderColor: "#3f3a591a",
  },

  fill: {
    type: "solid",
    opacity: [1, 0.2],
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
    shared: true,
    intersect: false,
    y: {
      formatter: function (y) {
        if (typeof y !== "undefined") {
          return y.toFixed(0) + " k";
        }
        return y;
      },
    },
  },
  xaxis: {
    type: "month",
    categories: ["Jan", "Feb", "Mar", "April", "May", "June", "July"],
    axisBorder: {
      show: false,
    },
    axisTicks: {
      show: false,
    },
    crosshairs: {
      show: true,
      width: 50,
      position: "back",
      opacity: 0.2,
      stroke: {
        color: KohoAdminConfig.secondary,
        width: 0,
        dashArray: 0,
      },

      fill: {
        type: "solid",
        color: KohoAdminConfig.secondary,
      },
    },
    tooltip: {
      marker: {
        show: false,
      },
      show: false,
      enabled: false,
    },
  },
  legend: {
    show: false,
  },
  responsive: [
    {
      breakpoint: 1661,
      options: {
        chart: {
          height: 357,
        },
      },
    },
    {
      breakpoint: 575,
      options: {
        chart: {
          height: 280,
        },
      },
    },

    {
      breakpoint: 400,
      options: {
        chart: {
          height: 230,
        },
      },
    },
  ],
  colors: [KohoAdminConfig.secondary, KohoAdminConfig.primary],
};
var chart = new ApexCharts(document.querySelector("#recent-chart"), options);
chart.render();

// Country Sales Chart
var options1 = {
  chart: {
    height: 335,
    type: "radar",
    toolbar: {
      show: false,
    },
  },
  series: [
    {
      data: [20, 100, 40, 30, 50, 80, 33],
    },
  ],
  stroke: {
    width: 2,
    curve: "smooth",
  },
  legend: {
    show: false,
  },
  labels: [
    "Sunday",
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
  ],
  grid: {
    borderColor: "#d3dbf4",
  },
  colors: [KohoAdminConfig.secondary],
  markers: {
    size: [5, 0],
    colors: ["#00000000"],
    strokeColor: KohoAdminConfig.secondary,
    strokeWidth: [3, 0],
    hover: {
      size: 5,
      sizeOffset: 3,
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
    tickAmount: 6,
    show: false,
  },
  responsive: [
    {
      breakpoint: 1661,
      options: {
        chart: {
          height: 320,
        },
      },
    },
    {
      breakpoint: 420,
      options: {
        chart: {
          height: 260,
        },
      },
    },
  ],
};

var chart1 = new ApexCharts(
  document.querySelector("#country-sales-chart"),
  options1
);

chart1.render();

// Items-Slider Slick Slider

$(".items-slider").slick({
  slidesToShow: 2,
  slidesToScroll: 1,
  autoplay: false,
  infinite: true,
  autoplaySpeed: 1500,
  responsive: [
    {
      breakpoint: 421,
      settings: {
        slidesToShow: 1,
        slidesToScroll: 1,
        infinite: true,
        dots: true,
      },
    },
  ],
});