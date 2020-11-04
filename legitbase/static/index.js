'use strict';

document.addEventListener('DOMContentLoaded', function () {
	var controls, i;
	controls = document.getElementsByClassName('group-select');
	for (i=0; i<controls.length; ++i) {
		controls[i].addEventListener('change', function () {
			var group, checkboxes, j;
			group = this.nextSibling;
			while (group.nodeType !== group.ELEMENT_NODE)
				group = group.nextSibling;
			checkboxes = group.childNodes;
			for (j=0; j<checkboxes.length; ++j)
				checkboxes[j].checked = this.checked;
		});
	}
});

$(document).ready(function(){
  $("a").on('click', function(event) {


    if (this.hash !== "") {
      event.preventDefault();

      var hash = this.hash;

      $('html, body').animate({
        scrollTop: $(hash).offset().top
      }, 500, function(){
   
        window.location.hash = hash;
      });
    } 
  });
});