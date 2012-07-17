var quota_chart, space_chart;
var root_dir = '/';

var updateFileInfo = function(data) {
  var root;
  if (root_dir == '/') {
    root = 'Root';
    $('#updir').css('visibility', 'hidden')
  } else {
    root = root_dir;
    $('#updir').css('visibility', 'visible')
  }
  $('#updir a').removeClass('active');
  $('#droptitle').html(root + ': ' + data.total);
  $('#filestable').html(data.filestable);
};

var joinPaths = function(a, b) {
  if (a.slice(-1) == '/') {
    return a + b;
  } else {
    return a + '/' + b;
  }
};

var getSpaceData = function(root) {
  var newroot = root || '/';
  $.getJSON($SCRIPT_ROOT + '/_spacedata', {
      'root': newroot
    }, function (data) {
      space_chart.series[0].setData(data.result || []);
      root_dir = newroot;
      space_chart.setTitle(null,
         { text: 'Details for ' + root_dir });
      updateFileInfo(data);
    });
};

$(document).ready(function() {
  var sc_options = {
    chart: {
      backgroundColor: '#eee',
      renderTo: 'spacechart',
      type: 'pie',
      animation: {
        duration: 1500  // ms
      },
      width: 500  // px
    },
    title: {
      text: 'Subdirectory Inventory'
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
              getSpaceData(new_rootdir);
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
        var s = '<b>'+this.point.name+'</b>: ' +
          this.point.percentage.toFixed(2) + '%.';
        if (this.point.name != 'Files') {
          s += ' Click to drilldown into subdirectory.';
        }
        return s;
      }
    },
    series: [{
      type: 'pie',
      name: 'Space Used',
      data: [],
    }],
  };
  space_chart = new Highcharts.Chart(sc_options);
  getSpaceData(root_dir);

  $('#updir').click(function() {
      if (root_dir == '/') {
        return;
      }
      $('#updir a').addClass('active');
      var lastslash = root_dir.lastIndexOf('/');
      var prevdir = root_dir.slice(0, lastslash);
      console.log('Going to prevdir: ' + prevdir);
      getSpaceData(prevdir);
  });
});
