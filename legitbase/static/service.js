'use strict';

document.addEventListener('DOMContentLoaded', function () {
	var form, sort;
	var rate_boxes, experience_boxes, district_boxes, language_boxes;
	var parameters;

	function parse_URL_parameters() {
		var items, params, i, p;
		items = window.location.search.substr(1).split('&');
		params = {__proto__: null};
		for (i=0; i<items.length; ++i) {
			p = items[i].split('=');
			params[p[0]] = p[1];
		}
		return params;
	}

	function submit() {
		document.getElementById('browse').click();
	}

	function handle_all_checked(button_id, elements, checked) {
		document.getElementById(button_id)
			.addEventListener('click', function () {
				var i;
				for (i=0; i<elements.length; ++i)
					elements[i].checked = checked;
				submit();
			});
	}

	function handle_submit_on_changes(elements) {
		var i;
		for (i=0; i<elements.length; ++i)
			elements[i].addEventListener('change', function () {
				submit();
			});
	}

	form = document.getElementById('heading_categories');
	sort = document.getElementById('sort');
	rate_boxes =
		document.getElementById('rate')
			.querySelectorAll('input[type="checkbox"]');
	experience_boxes =
		document.getElementById('experience')
			.querySelectorAll('input[type="checkbox"]');
	district_boxes =
		document.getElementById('district')
			.querySelectorAll('input[type="checkbox"]');
	language_boxes =
		document.getElementById('language')
			.querySelectorAll('input[type="checkbox"]');
	parameters = parse_URL_parameters();

	if (parameters['s']) sort.value = parameters['s'];

	handle_all_checked('allrate', rate_boxes, true);
	handle_all_checked('norate', rate_boxes, false);
	handle_all_checked('allexperience', experience_boxes, true);
	handle_all_checked('noexperience', experience_boxes, false);
	handle_all_checked('alldistrict', district_boxes, true);
	handle_all_checked('nodistrict', district_boxes, false);
	handle_all_checked('alllanguage', language_boxes, true);
	handle_all_checked('nolanguage', language_boxes, false);

	handle_submit_on_changes(rate_boxes);
	handle_submit_on_changes(experience_boxes);
	handle_submit_on_changes(language_boxes);

	document.getElementById('districtsubmit')
		.addEventListener('click', submit);

	sort.addEventListener('change', submit);
});
