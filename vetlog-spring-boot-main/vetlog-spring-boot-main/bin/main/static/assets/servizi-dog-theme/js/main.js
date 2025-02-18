$ (function () {

	"use strict";

    $('a.page-scroll').bind('click', function(event) {
        var $anchor = $(this);
        $('html, body').stop().animate({
            scrollTop: $($anchor.attr('href')).offset().top
        }, 1000, 'easeInOutExpo');
        event.preventDefault();
    });

	// Highlight the top nav as scrolling occurs
	$('body').scrollspy({
	    target: '.navbar-fixed-top'
	});

	// Closes the Responsive Menu on Menu Item Click
	$('.navbar-collapse ul li a').click(function() {
	    $('.navbar-toggle:visible').click();
	});

	// One page navigation menu scroll
	function spy_scroll(){

		$('.navbar-nav').onePageNav({
	        currentClass: 'active',
	        scrollSpeed: 3000,
	        scrollThreshold: 0.5,
	        easing: 'swing'
	    }); 

	}

	function setParallax() {
		if( $(window).width() > 768 ) {
			$('.full-width-parallax').parallax(0, 0.3);
		}
	}

	setParallax();

	$(window).resize( function() {
		setParallax();
	});

	$(document).ready(function(){
		$('.nav.navbar-nav li a').bind('click', function(event) {
        var $anchor = $(this);
		$('html, body').stop().animate({
            scrollTop: $($anchor.attr('href')).offset().top
        }, 1500, 'easeInOutExpo');
        event.preventDefault();
    });
	
	// Highlight the top nav as scrolling occurs
	$('#content').scrollspy({
		target: '.navbar-fixed-top'
	});

	$(document).ready(function() {

		//$('.content-tabs').tabCollapse();

	    $('.nav-tabs a').click(function(e) {
	        e.preventDefault();
	        $(this).tab('show');
	    });

	});

	function isScrolledIntoView(elem) {	
		try{
		    var docViewTop = $(window).scrollTop();
		    var docViewBottom = docViewTop + $(window).height();

		    var elemTop = $(elem).offset().top;
		    var elemBottom = elemTop + $(elem).height();

		    return ((elemBottom <= docViewBottom) && (elemTop >= docViewTop));
		}catch(e){ }
	}

	var dialed = false;

	function responsiveSlider() {
		var width = $(window).width();
		var height = $(window).height() - ($(window).height() / 3) + 100;
		$('header').height(height);
		$('header .item').height(height);
		$('header .item').css('background-position', 'center center');
	}
	responsiveSlider();

	//Window Resize Event
	$(window).resize(function(){
		responsiveTable();
		responsiveSlider();
		$('.price-table hr.price').each(function(){
			$(this).width($(this).parent().parent().parent().width() - 5);
		});
		$("section div[class^='col-lg-'].item").each(function(){
			var cls = $(this).attr('class');
			var index = cls.indexOf(' ');
			var number = cls.substring(7, index);
			var height = $(this).height();
			if($(window).width() < 768)
			{
				$("section div[class^='col-lg-" + number + "'].info").each(function(){
				$(this).css('height','auto');
				});
			}
			else
			{
				$("section div[class^='col-lg-" + number + "'].info").each(function(){
					$(this).height($(this).width());
				});
			}
		});
	});

	function responsiveTable() {
		var width = $(window).width();
		if(width < 768 && width > 450) {
			$('table thead').children().first().children('th').eq(1).hide();
			$('table thead').children().first().children('th').eq(3).hide();
			$('table tr').each(function(){
				$(this).children('td').eq(1).hide();
				$(this).children('td').eq(3).hide();
			});
		}
		else if(width < 450) {
			$('table thead').children().first().children('th').eq(2).hide();
			$('table thead').children().first().children('th').eq(4).hide();
			$('table tr').each(function(){
				$(this).children('td').eq(2).hide();
				$(this).children('td').eq(4).hide();
			});
			$('table thead').children().first().children('th').eq(1).hide();
			$('table thead').children().first().children('th').eq(3).hide();
			$('table tr').each(function(){
				$(this).children('td').eq(1).hide();
				$(this).children('td').eq(3).hide();
			});
		}
		else {
			$('table th').each(function(){ $(this).show(); })
			$('table td').each(function(){ $(this).show(); })
		}
	}

	// Window Scroll Event
	$(window).scroll(function(){
		var element = $('.fact .number');
		var knob = $('.dial');
		if(isScrolledIntoView(element) && element.html() == "0")
			element.countTo();
		if(isScrolledIntoView(knob) && !dialed)
		{

			dialed = true;
			$('.dial').each(function () { 

	          var elm = $(this);
	          var color = elm.attr("data-fgColor");  
	          var perc = elm.attr("value");  
	 
	          elm.knob({ 
	               'value': 1, 
	                'min': 0,
	                'max': 100,
	                "readOnly": true,
	                "lineCap": 'round',
					"thickness": .2,
					"inputColor": "#FF7B27",
					"font": "Raleway",
					"fontWeight": 700,
	                'dynamicDraw': true
	          });

	          $({value: 0}).animate({ value: perc }, {
	              duration: 1000,
	              easing: 'swing',
	              progress: function () {                  
	              	elm.val(Math.ceil(this.value)).trigger('change')
	              }
	          });

	          });
		}
	});

 	$("a[data-rel^='prettyPhoto']").prettyPhoto();

 	/* Carousel */

	$('#owl-demo').owlCarousel({
		autoPlay: true,
		singleItem: true
	});

	$('#owl-testimonials').each(function(){
		$(this).owlCarousel({
			singleItem : true
		});
	});

});
});