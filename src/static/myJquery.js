
   
$(document).ready(function() {   
	
	var form= $("#newFollow").html();
	
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
  
    ////////////////////Submit
    var options1 = { 
        target:        '#result',  	      // target element(s) to be updated with server response 
        beforeSubmit: validate, 
        success:       showResponse,      // post-submit callback 
 		url:      '/Submit',              // override for form's 'action' attribute 
 		type:      "POST",
 		dataType:  'json'   
    }; 
	
    $('#newFollow').submit(function() { 
    	updateAuthors();
    	$(this).ajaxSubmit(options1  ); 
        return false; 
    }); 
    
    ///////////////////First Upload
    var options2 = { 
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
    
    //////////////////////remove follow
    var options_rm_follow = { 
    	success:       gotoSearch,    	// post-submit callback   
 		url:      '/MyFollows',              // override for form's 'action' attribute 
 		type:      "POST",
 		dataType:  'json'
    }; 
    
     // Remove follow when button is clicked 
    $('.removeButton').click(function() {
    	var id_name = $(this).attr("id");
    	$(this).parent().parent().remove();
    	$("#action_type").val("remove");
    	$("#name_to_remove").val(id_name);
        $("#follow_to_remove").ajaxSubmit(options_rm_follow); 
        return false; 
    });
    
    $('.runSearch').click(function() {
    	var id_name = $(this).attr("id");
    	$("#action_type").val("search");
    	$("#name_to_remove").val(id_name);
        $("#follow_to_remove").ajaxSubmit(options_rm_follow); 
        return false; 
    });
    
 });

function gotoSearch(responseText, statusText, xhr, $form)  {
	
	if (responseText == "true"){
		location.href = '/Search?Type=FollowResults';
	}
	else{
		$('#popupText').html("Sorry. DB currently unavailable. Please try again later. <br/>");
		$('#popupText').dialog({ width: 400 , buttons: { "Ok": function() { $(this).dialog("close"); } }});

	}
	
}


function updateAuthors(){
	var authors= "";
	var all_authors = $('input[name=author_name]');
		all_authors.each( function () {
			var author_name=$(this).fieldValue();
			if (author_name != "") 
			authors = authors + " "+ author_name;	
	});	 
	
 	$('#ch_author').val(authors);
}



function validate(formData, jqForm, options) { 
	
 	var ch_citing = $('input[name=ch_citing]').fieldValue();
 	var ch_keywords = $('input[name=ch_keywords]').fieldValue();
 	var ch_author = $('input[name=ch_author]').fieldValue();
 	var ch_journal = $('input[name=ch_journal]').fieldValue();
 	var keywords = $('input[name=keywords]').fieldValue();
 	var journal = $('input[name=journal]').fieldValue();
 		
    if (ch_citing=="" && 
    	(ch_keywords=="" || (ch_keywords!="" && !keywords[0])) &&
    	ch_author=="" &&
    	(ch_journal=="" || (ch_journal!="" && !journal[0])) )
        {
        		$('#popupText').html("Please, choose one of the fields");
		   		$('#popupText').dialog({ width: 600, buttons: { "Ok": function() { $(this).dialog("close"); } }});
        		return false;
        }
	
    form = $("#newFollow").html(); 
    showLoadingImage();
    return true;
    	
};
 
  
  
// post-submit callback 
function showResponse(responseText, statusText, xhr, $form)  { 
   
    if (responseText == "-2"){
    	stopShowingLoadingImage();
        $('#popupText').html("Sorry. DB currently unavailable. Please try again later. <br/>");
        $('#popupText').dialog({ width: 600 , buttons: { "Ok": function() { $(this).dialog("close"); } }});
    }
    
   if (responseText == "-1"){
	    stopShowingLoadingImage();
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



function showLoadingImage(){
    $("#newFollow").html('<CENTER><img  src="/static/images/ajax-loader.gif" /></CENTER>');
};



function Close_Popup() {
	stopShowingLoadingImage();
	$('#popup_content').dialog("close");

};

function stopShowingLoadingImage(){
	$("#newFollow").html(form);
};