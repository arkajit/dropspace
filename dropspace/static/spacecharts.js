var quota_chart, space_chart;

$(document).ready(function() {
  var qc_options = {
    chart: {
      renderTo: 'quotachart',
      type: 'pie',
    }, 
    title: {
      text: 'Dropbox Quota Consumption'
    },
    tooltip: {
      formatter: function() {
        return '<b>'+this.point.name+'</b>: ' +
          this.point.percentage.toFixed(2) + '%'
      }
    },
    series: [{
      type: 'pie',
      name: 'Space Used',
      data: [],
    }],
  };
  $.getJSON($SCRIPT_ROOT + '/_quotainfo', {
      // Can provide userid, otherwise server will read from cookie.
      // 'uid': '12013862'
    }, function (data) {
      // Don't need to parseJSON, since data is not a string, but a JSON object.
      qc_options.series[0].data = data.result || [];
      quota_chart = new Highcharts.Chart(qc_options);
    });

  /* TODO(arkajit): Re-enable when complete.
  var sc_options = {
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
  $.getJSON($SCRIPT_ROOT + '/_spacedata', {
    }, function (data) {
      sc_options.series[0].data = data.result || [];
      space_chart = new Highcharts.Chart(sc_options);
    });
  */
});
