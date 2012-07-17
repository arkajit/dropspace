var quota_chart, space_chart;
var root_dir = '/';

var updateFileInfo = function(data) {
  var root = (root_dir == '/') ? 'Root' : root_dir;
  $('#droptitle').html(root + ': ' + data.total);
  $('#filestable').html(data.filestable);
};

var joinPaths = function(a, b) {
  if (a.slice(-1) == '/') {
    return a + b;
  } else {
    return a + '/' + b;
  }
}

$(document).ready(function() {
  $('#filestable').tablesorter({ sortList: [1,1] });

  var sc_options = {
    chart: {
      renderTo: 'spacechart',
      type: 'pie',
    },
    title: {
      text: 'Dropbox Space Inventory'
    },
    subtitle: {
      text: 'Details for ' + root_dir
    },
    plotOptions: {
      pie: {
        events: {
          click: function() {
            console.log('Clicked series');
          }
        },
        point: {
          events: {
            click: function() {
              // Ignore clicks on aggregated Files point.
              if (this.name == 'Files') {
                return;
              }
              var new_rootdir = joinPaths(root_dir, this.name);
              $.getJSON($SCRIPT_ROOT + '/_spacedata', {
                'root': new_rootdir
              }, function (data) {
                  space_chart.series[0].setData(data.result || []);
                  root_dir = new_rootdir;
                  space_chart.setTitle(null,
                     { text: 'Details for ' + root_dir });
                  updateFileInfo(data);
              });
            },
            mouseOver: function() {
              this.sliced = true;
              this.selected = true;
            },
            mouseOut: function() {
              this.sliced = false;
              this.selected = false;
            },
          }
        }
      }
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

  $.getJSON($SCRIPT_ROOT + '/_spacedata', {
    }, function (data) {
      sc_options.series[0].data = data.result || [];
      space_chart = new Highcharts.Chart(sc_options);
      updateFileInfo(data);
    });
});
