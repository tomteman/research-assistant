
   
$(document).ready(function() {    
	
	$('#ch_citing').bind('click', function () {
    	
    	if ($(this).is(':checked')) {
 	        $("#publication").fadeTo('fast', 0.5)
      		$("#publication").attr("disabled", 'disabled');
      		$("#explanation:hidden:first").fadeIn();
      		
    	} else {
    	 	$("#publication").fadeTo('fast', 1);
      		$("#publication").attr("disabled", 'enabled');
      		$("#explanation").fadeOut();
      		         	
    	}
    }) 
  
    var options1 = { 
        target:        '#result',  	      // target element(s) to be updated with server response 
        beforeSubmit:  showRequest,		  // pre-submit callback 
        success:       showResponse,      // post-submit callback 
 		url:      '/Submit',              // override for form's 'action' attribute 
 		type:      "POST",
 		dataType:  'json'
      
    }; 
    
  
    $('#newFollow').submit(function() {        
       $(this).ajaxSubmit(options1); 
       return false; 
    }); 
    
    var options2 = { 
        target:        '#result',  	 // target element(s) to be updated with server response 
        beforeSubmit:  showRequest,		  // pre-submit callback 
        success:       showResponse,    	// post-submit callback 
 		url:      '/FirstUpload',         // override for form's 'action' attribute 
 		type:      "POST",
 		dataType:  'json'
      
    }; 
    
    
    // bind to the form's submit event 
    $('#butUpload').click(function() { 
        $('#newFollow').ajaxSubmit(options2); 
        return false; 
    }); 
   
 });

 
 
 
function showRequest(formData, jqForm, options) { 
 	//TODO LOADING 
    return true; 
} 
  
  
// post-submit callback 
function showResponse(responseText, statusText, xhr, $form)  { 
   
   if (responseText == "1000"){
   		$('#popupText').html("Search with current configuration returned more than 1000 results.<br/> There is a chance that we won't be able to bring you new updates.<br/> Do you want to continue?");
   		$('#popup_content').dialog({ width: 600 });
   	
	}
	
	if (responseText == "0"){
   		$('#popupText').html("Search with current configuration returned no results.<br/> Do you want to continue?");
   		$('#popup_content').dialog({ width: 600  });
	}
	if  (!(responseText == "1000" || responseText == "0")){
		location.href = '/FollowFormDone';
   		
	}      
};

	
function Close_Popup() {
	$('#popup_content').dialog("close");
};