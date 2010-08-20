var iFrameHeight;

$(document).ready(function() {   
	iFrameHeightInit();
	iFrameHeightIncrement(700-iFrameHeight);
}


function iFrameHeightInit(){
	iFrameHeight = jQuery("iframe",top.document).contents().find('body').attr('scrollHeight')
}

function iFrameHeightIncrement(value){
	newHeight = iFrameHeight + value;
	jQuery("iframe",top.document).height(newHeight);	
	iFrameHeight = newHeight
}