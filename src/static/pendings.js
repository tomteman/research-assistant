
var new_label="";
var last_action = "";
var cur_row = ""

$(document).ready(function() {   
   
	var pendingOptions = {  
	        success:       pendingResponse,      // post-submit callback 
	 		url:      '/ShowPendings',              // override for form's 'action' attribute 
	 		type:      "POST",
	 		dataType:  'json'   
	    }; 
	 
    $('.accept').click(function() {
    	var pending_id = $(this).parent().attr("value");
    	new_label = $(this).parent().parent().find("#label_name").attr("value");
    	cur_row = $(this).parents("tr");
    	$("#action_type").val("accept");
    	$("#pending_id").val(pending_id);
    	last_action = "accept"
        $("#pendingActions").ajaxSubmit(pendingOptions); 
        return false; 
    });
    
    $('.reject').click(function() {
    	var pending_id = $(this).parent().attr("value");
    	cur_row = $(this).parents("tr");
    	$("#action_type").val("reject");
    	$("#pending_id").val(pending_id);
    	last_action = "reject"
        $("#pendingActions").ajaxSubmit(pendingOptions); 
        return false; 
    });
    
    $('.preview').click(function() {
    	var pending_id = $(this).parent().attr("value");
    	new_label = $(this).parent().parent().find("#label_name").attr("value");
    	$("#action_type").val("ShowPending");
    	$("#pending_id").val(pending_id);
        $("#pendingActions").ajaxSubmit({success:       previewResponse,      // post-submit callback 
	 									 url:      '/ShowArticlesByLabel',              // override for form's 'action' attribute 
	 									 type:      "GET",
	 									 dataType:  'html'  
        								}); 
        return false; 
    });
    
 });

function previewResponse(responseText, statusText, xhr, $form)  {
	if (responseText == "-7"){
        $('#popupText').html("Sorry. DB currently unavailable. Please try again later. <br/>");
        $('#popupText').dialog({ width: 600 , zIndex: 3999, buttons: { "Ok": function() { $(this).dialog("close"); } }});
    }
	if (responseText == "-4" || responseText == "-5"){
        $('#popupText').html("Sorry, an error ocured. Please try again later. <br/>");
        $('#popupText').dialog({ width: 600 , zIndex: 3999, buttons: { "Ok": function() { $(this).dialog("close"); } }});
    }
	else document.body.innerHTML=responseText;
    	
}


function pendingResponse(responseText, statusText, xhr, $form)  {
	if (responseText == "-7"){
        $('#popupText').html("Sorry. DB currently unavailable. Please try again later. <br/>");
        $('#popupText').dialog({ width: 600 , zIndex: 3999, buttons: { "Ok": function() { $(this).dialog("close"); } }});
    }
    
   if (responseText == "-4"){
	   
        $('#popupText').html("An error has occured. Please, try again later <br/>");
        $('#popupText').dialog({ width: 600 , zIndex: 3999, buttons: { "Ok": function() { $(this).dialog("close"); } }});
    }

   if (responseText == "0" || parseInt(responseText) > "0"){
	   if (last_action == "accept"){
		   parent.addLabel(new_label, responseText);
		   $('#popupText').html("label was added <br/>");
	   }
	   if (last_action == "reject"){
		   $('#popupText').html("inventation was rejected <br/>");
	   }
	   cur_row.remove()
	   $('#popupText').dialog({ width: 400 , zIndex: 3999, buttons: { "Ok": function() { $(this).dialog("close"); } }});
	}
   
	
}