jQuery(function() {
	"use strict";

  function set_safari_fix(){
    var ua = navigator.userAgent, vendor = navigator.vendor; 
    if (ua.search(/Safari/)  != -1 && vendor.search(/Apple/) != -1 ) {
      if (jQuery('.gt3_gallery_wrapper.circle').length || jQuery('.gt3_gallery_wrapper.square').length) {
      jQuery('.gallery-icon img').addClass('safari');
      }    
    };
  }

  jQuery(window).on('load', function() { 
    jQuery('.gt3pg_gallery-item').each(function() { 
      if (jQuery(this).height())
        jQuery(this).height(Math.ceil(jQuery(this).height())); 
    }); 
  });

  jQuery(window).on('resize', function() { 
    jQuery('.gt3pg_gallery-item').each(function() { 
      if (jQuery(this).height())
        jQuery(this).height('').height(Math.ceil(jQuery(this).height())); 
    }); 
  });

  set_safari_fix();
  jQuery('.gt3pg_gallery-item.gt3pg_element').each(function(n) {
    jQuery(this).delay(n*150).fadeTo(400, 1);
  });

  jQuery('html').addClass('gt3_swipe_box');
  jQuery('.gt3pg_swipebox').swipebox_pg(); 

  jQuery(document).on("click", "#pg_swipebox-container .pg_slide.current img", function (e) { 
    jQuery('#pg_swipebox-next').trigger('click');
    e.stopPropagation();
  });
  jQuery(document).on("click", "#pg_swipebox-container", function (e) {
    jQuery('#pg_swipebox-close').trigger('click');
  });

});
