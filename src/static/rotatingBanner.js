
	$('.slideshow1').cycle({
			fx:				'fade',  // name of transition effect (or comma separated names, ex: fade,scrollUp,shuffle)
			timeout:       	5000,   // milliseconds between slide transitions (0 to disable auto advance) 
			//continuous:	0,     // true to start next transition immediately after current one completes 
			//speed:       	500,    // speed of the transition (any valid fx speed value)
			//delay:		-4000,
			pause:         	1,     // true to enable "pause on hover" 
	});

	
	
	/* when user clicks to hide the banner */
	function hideBanner(){
		$('.slideshow1').hide()
		$('.closeBannerButton').hide()
		$('.showBannerButton').show()
	}
	
	/* when user clicks to show the banner */
	function showBanner(){
		$('.slideshow1').show()
		$('.closeBannerButton').show()
		$('.showBannerButton').hide()
	}