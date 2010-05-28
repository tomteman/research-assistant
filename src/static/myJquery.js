
   
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
    
    
   
 // select + reference "triggering element" -- will pass to $.jqm()
  var triggers = $('a.ex3bTrigger')[0];
  
  // NOTE; we could have used document.getElementById(), or selected
  //  multiple elemets with $(..selector..) and passed the trigger
  //  as a jQuery object. OR, just include the string '#ex3btrigger' 
  //  as the trigger parameter (as typically demonstrated).
  
  //  NOTE; we supply a target for the ajax return. This allows us
  //   to keep the structure of the alert window. An element can 
  //   also be passed (see the documentation) as target.
  
  $('#ex3b').jqm({
    trigger: triggers,
    ajax: 'examples/3b.html',
    target: 'div.jqmAlertContent',
    overlay: 0
    });
  
  // Close Button Highlighting. IE doesn't support :hover. Surprise?
  if($.browser.msie) {
  $('div.jqmAlert .jqmClose')
  .hover(
    function(){ $(this).addClass('jqmCloseHover'); }, 
    function(){ $(this).removeClass('jqmCloseHover'); });
  }

  
  
  // Close Button Highlighting. IE doesn't support :hover. Surprise?
  $('input.jqmdX')
  .hover(
    function(){ $(this).addClass('jqmdXFocus'); }, 
    function(){ $(this).removeClass('jqmdXFocus'); })
  .focus( 
    function(){ this.hideFocus=true; $(this).addClass('jqmdXFocus'); })
  .blur( 
    function(){ $(this).removeClass('jqmdXFocus'); });

    
    var options1 = { 
        target:        '#result',  	 // target element(s) to be updated with server response 
        beforeSubmit:  showRequest,		  // pre-submit callback 
        success:       showResponse,    	// post-submit callback 
 		url:      '/Submit',         // override for form's 'action' attribute 
 		type:      "POST",
 		dataType:  'json'
      
    }; 
    
   
    // bind to the form's submit event 
    $('#newFollow').submit(function() { 
        // inside event callbacks 'this' is the DOM element so we first 
        // wrap it in a jQuery object and then invoke ajaxSubmit 
        $(this).ajaxSubmit(options1); 
 
        // !!! Important !!! 
        // always return false to prevent standard browser submit and page navigation 
        return false; 
    }); 
    
    var options2 = { 
        target:        '#result',  	 // target element(s) to be updated with server response 
        beforeSubmit:  showRequest,		  // pre-submit callback 
        success:       showResponse,    	// post-submit callback 
 		url:      '/Submit',         // override for form's 'action' attribute 
 		type:      "POST",
 		dataType:  'json'
      
    }; 
    
    
    // bind to the form's submit event 
    $('#firstUpload').submit(function() { 
        // inside event callbacks 'this' is the DOM element so we first 
        // wrap it in a jQuery object and then invoke ajaxSubmit 
        $(this).ajaxSubmit(options2); 
 
        // !!! Important !!! 
        // always return false to prevent standard browser submit and page navigation 
        return false; 
    }); 
    
    
       

    
 });


function showRequest(formData, jqForm, options) { 
 	//TODO LOADING
    
    return true; 
} 
 
 
 
// post-submit callback 
function showResponse(responseText, statusText, xhr, $form)  { 
	$('#popup').fadeIn('fast');
	$('#window').fadeIn('fast');
   
    alert('status: ' + statusText + '\n\nresponseText: \n' + responseText + 
        '\n\nThe output div should have already been updated with the responseText.');  
	
	}
	
	

function Show_Popup() {
	$('#popup').fadeIn('fast');
	$('#window').fadeIn('fast');
}
	
function Close_Popup() {
	$('#popup').fadeOut('fast');
	$('#window').fadeOut('fast');
}