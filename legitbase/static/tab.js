'use strict';

function panel(pairs) {
	var i;
	for (i=0; i<pairs.length; ++i) {
		(function (j) {
			pairs[j].tab.addEventListener('click', function () {
				var k;
				for (k=0; k<pairs.length; ++k) {
					console.debug('pair =', pairs[k]);
					pairs[k].panel.hidden = j !== k;
				}
			});
		})(i);
		pairs[i].panel.hidden = Boolean(i);
	}
}

function tab_install(group_class, tab_class, panel_class) {
	var groups, i, tabs, panels, pairs, n, j;
	groups = document.getElementsByClassName(group_class);
	for (i=0; i<groups.length; ++i) {
		tabs = groups[i].getElementsByClassName(tab_class);
		panels = groups[i].getElementsByClassName(panel_class);
		n = Math.min(tabs.length, panels.length);
		pairs = new Array(n);
		for (j=0; j<n; ++j)
			pairs[j] = {tab: tabs[j], panel: panels[j]};
		panel(pairs);
	}
}

document.addEventListener('DOMContentLoaded', function () {
	tab_install('tab-panel', 'tab', 'panel');
});

var addclass = 'tab_color';
var $cols = $('.tab').click(function(e) {
    $cols.removeClass(addclass);
    $(this).addClass(addclass);
});

$(function() {
  $('.tab:nth-of-type(1)').addClass('tab_color');
});

