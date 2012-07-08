var chart;
$(document).ready(function() {
  var options = {
    chart: {
      renderTo: 'spacechart',
      type: 'pie',
    }, 
    title: {
      text: 'Dropbox Space Inventory'
    },
    series: [{
      type: 'pie',
      name: 'Root directory',
      data: [
        ['foo', 23],
        ['bar', 15],
        ['baz', 37],
      ]
    }],
  };
  chart = new Highcharts.Chart(options);
});
