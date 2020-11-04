'use strict';

document.addEventListener('DOMContentLoaded', function () {
	var inputs, i;
	inputs = document.getElementsByTagName('input');
	for (i=0; i<inputs.length; ++i) {
		if (inputs[i].type === 'range')
			inputs[i].addEventListener('change', function (event) {
				this.nextSibling.nodeValue = this.value;
			});
	}
});
