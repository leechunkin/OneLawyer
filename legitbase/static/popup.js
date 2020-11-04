'use strict';

function popup(toggle_elements, show_elements, open_elements=[], close_elements=[], start=false) {
	var opening = Boolean(start);
	function open(new_status) {
		var i;
		for (i=0; i<show_elements.length; ++i)
			show_elements[i].hidden = !new_status;
		opening = new_status;
	}
	function click_toggle() {
		open(!opening);
	}
	function click_open() {
		if (!opening) return open(true);
	}
	function click_close() {
		if (opening) return open(false);
	}
	opening = false;
	return (function () {
		var i;
		for (i=0; i<toggle_elements.length; ++i)
			toggle_elements[i].addEventListener('click', click_toggle);
		for (i=0; i<open_elements.length; ++i)
			open_elements[i].addEventListener('click', click_open);
		for (i=0; i<close_elements.length; ++i)
			close_elements[i].addEventListener('click', click_close);
	}());
}

function popup_install(popup_class, toggle_class, show_class, open_class=null, close_class=null, start=false) {
	var popups, i, toggle, show, open, close, j;
	popups = document.getElementsByClassName(popup_class);
	for (i=0; i<popups.length; ++i) {
		toggle = popups[i].getElementsByClassName(toggle_class);
		show = popups[i].getElementsByClassName(show_class);
		for (j=0; j<show.length; ++j)
			show[j].hidden = !start;
		if (open_class == null)
			open = [];
		else
			open = popups[i].getElementsByClassName(open_class);
		if (close_class == null)
			close = [];
		else
			close = popups[i].getElementsByClassName(close_class);
		popup(toggle, show, open, close, start);
	}
}

document.addEventListener('DOMContentLoaded', function () {
	popup_install('popup', 'popup-toggle', 'popup-show', 'popup-open', 'popup-close');
	popup_install('popup1', 'popup1-toggle', 'popup1-show', 'popup1-open', 'popup1-close');
});
