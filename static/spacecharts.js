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
      name: 'Space Used',
      data: [],
    }],
  };
  $.getJSON($SCRIPT_ROOT + '/_quotainfo', {
      'uid': '12013862'
    }, function (data) {
      // Don't need to parseJSON, since data is not a string, but a JSON object.
      options.series[0].data = data.result || [];
      chart = new Highcharts.Chart(options);
    });
});
