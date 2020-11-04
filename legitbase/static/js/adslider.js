jQuery(document).ready(function ($) {

    setInterval(function () {
        moveRight();
    }, 5000);
  
	var slideCount = $('#adslider ol li').length;
	var slideWidth = $('#adslider ol li').width();
	var slideHeight = $('#adslider ol li').height();
	var sliderUlWidth = slideCount * slideWidth;
	
	$('#adslider').css({ width: slideWidth, height: slideHeight });
	
	$('#adslider ol').css({ width: sliderUlWidth, marginLeft: - slideWidth });
	
    $('#adslider ol li:last-child').prependTo('#adslider ol');

    function moveLeft() {
        $('#adslider ol').animate({
            left: + slideWidth
        }, 900, function () {
            $('#adslider ol li:last-child').prependTo('#adslider ol');
            $('#adslider ol').css('left', '');
        });
    };

    function moveRight() {
        $('#adslider ol').animate({
            left: - slideWidth
        }, 900, function () {
            $('#adslider ol li:first-child').appendTo('#adslider ol');
            $('#adslider ol').css('left', '');
        });
    };

    $('a.control_prev').click(function () {
        moveLeft();
    });

    $('a.control_next').click(function () {
        moveRight();
    });

});