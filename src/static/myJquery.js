
   
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
    
    
    var options_rm_follow = { 
        target:        '#result',  	      // target element(s) to be updated with server response 
        beforeSubmit:  showRequest,		  // pre-submit callback 
        success:       showResponse2,      // post-submit callback 
 		url:      '/MyFollows',              // override for form's 'action' attribute 
 		type:      "POST",
 		dataType:  'json'
      
    }; 
    
  
     // Remove follow when button is clicked 
    $('.removeButton').click(function() {
     
    	var id_name = $(this).attr("id");	
    	$(this).parent("li").remove();
    	$("#name_to_remove").val(id_name);
        $("#follow_to_remove").ajaxSubmit(options_rm_follow); 
        return false; 
    }); 
 });

 
 
 
function showRequest(formData, jqForm, options) { 
 	//TODO LOADING 
    return true; 
} 
  
  
// post-submit callback 
function showResponse(responseText, statusText, xhr, $form)  { 
   
    if (responseText == "-2"){
           $('#popupText').html("Sorry. DB currently unavailable. Please try again later. <br/>");
           $('#popupText').dialog({ width: 600 , buttons: { "Ok": function() { $(this).dialog("close"); } }});
    }
    
   if (responseText == "-1"){
           $('#popupText').html("This follow already exists <br/>");
           $('#popupText').dialog({ width: 600 , buttons: { "Ok": function() { $(this).dialog("close"); } }});
    }

   if (responseText == "1000"){
   		$('#popupText').html("Search with current configuration returned more than 1000 results.<br/> There is a chance that we won't be able to bring you new updates.<br/> Do you want to continue?");
   		$('#popup_content').dialog({ width: 600 });
	}
	
	if (responseText == "0"){
   		$('#popupText').html("Search with current configuration returned no results.<br/> Do you want to continue?");
   		$('#popup_content').dialog({ width: 600  });
	}
	if  (!(responseText == "1000" || responseText == "0" || responseText == "-1")){
		location.href = '/FollowFormDone';
   		
	}      
};

 

function showResponse2(responseText, statusText, xhr, $form)  { 
   
    
};

	
function Close_Popup() {
	$('#popup_content').dialog("close");
};