var followRow;
var iFrameHeight;
   
var options2 = { 
        success:       showResponse,    	// post-submit callback 
 		url:      '/FirstUpload',         // override for form's 'action' attribute 
 		type:      "POST",
 		dataType:  'json'  
    };

$(document).ready(function() {   
	iFrameHeightInit();
	iFrameHeightIncrement(700-iFrameHeight);
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
    
    //////////////////////remove follow
    var options_follow = { 
    	success:       gotoSearch,    	// post-submit callback   
 		url:      '/MyFollows',              // override for form's 'action' attribute 
 		type:      "POST",
 		dataType:  'json'
    }; 
    
    
     // Remove follow when button is clicked 
    $('.removeButton').click(function() {
    	var id_name = $(this).parent().attr("value");
    	followRow = $(this).parent().parent().parent();
    	
    	$('#popupText').html("Are you sure you want to delete follow: <br/>" + id_name);
		$('#popupText').dialog({ width: 600 , buttons: {
									"Cancel": function() { $(this).dialog("close");},
									"Yes": function() {
											$(this).dialog("close");
											$("#action_type").val("remove");
											$("#name_to_remove").val(id_name);
											parent.updateNumber("myFollows", 0)
											$("#follow_to_remove").ajaxSubmit(options_follow); 
											 }
								} });
    	});
    
    $('.runSearch').click(function() {
    	var id_name = $(this).parent().attr("value");
    	$("#action_type").val("search");
    	$("#name_to_remove").val(id_name);
        $("#follow_to_remove").ajaxSubmit(options_follow); 
        return false; 
    }); 
 //////////////////////////////////////////////////   
    
	$("#accordion").accordion({ collapsible:true, active: false, autoHeight: false });
    
 });
///////////////////////////////////////////////////////////////

function sendMail(){
	$("#empty_form").ajaxSubmit({success:       sendMailResponse,      // post-submit callback 
		 url:      '/FollowFormDone',              // override for form's 'action' attribute 
		 type:      "POST",
		 dataType:  'html'  
	}); 
	
}

function sendMailResponse(responseText, statusText, xhr, $form)  {
	$("#follow_created").hide();
	if (responseText != "0"){ 
		$("#sendingError").show();
	}
	else{
		$("#emailWasSend").show();
	}
}
	 


function gotoSearch(responseText, statusText, xhr, $form)  {
	if (responseText == "true"){
		location.href = '/Search?Type=FollowResults';
	}else{
		if (responseText == "1"){
			followRow.remove();
		}else{
			$('#popupText').html("Sorry. DB currently unavailable. Please try again later. <br/>");
			$('#popupText').dialog({ width: 400 , buttons: { "Ok": function() { $(this).dialog("close"); } }});
		}
	}
}

function updateAuthors(){
	var ch_author = $('input[name=ch_author]').fieldValue();
	var ch_author_input = $('input[name=ch_author_input]').fieldValue();
	var author_input = $('input[name=author_input]').fieldValue();
	if (ch_author != ""){
		var authors= "";
		var count = 0;
		var all_authors = $('input[name=author_name]');
		all_authors.each( function () {
			count++;
			var author_name=$(this).fieldValue();
			if (author_name != "") 
			authors = authors + " "+ author_name;	
		});	 
		if (ch_author_input && author_input != "")
			authors = authors + " "+ author_input;
		if (count != 0){
			$('#ch_author').val(authors);
		}
	}
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
   		$('#popupText').dialog({ width: 600 , buttons: {
   										"Cancel": function() { 
   													stopShowingLoadingImage();
   													$(this).dialog("close");
   													},
   										"Yes": function() {
   												$(this).dialog("close");
   												showLoadingImage();
   												$('#newFollow').ajaxSubmit(options2); 
   												}
   		} });

	}
	
	if (responseText == "0"){
   		$('#popupText').html("No articles published this year answer your search parameters criteria.<br/>Would you like to add this follow anyway?");
   		$('#popupText').dialog({ width: 600 , buttons: {
				"Cancel": function() { 
   							stopShowingLoadingImage();
   							$(this).dialog("close");
							},
				"Yes": function() {
						$(this).dialog("close");
						showLoadingImage();
						$('#newFollow').ajaxSubmit(options2); 
						}
   		} });

	}
	if  (!(responseText == "1000" || responseText == "0" || responseText == "-1")){
		parent.updateNumber("myFollows", 1);
		location.href = '/FollowFormDone';
   		
	}      
};


function showLoadingImage(){
    $("#newFollow").html('<CENTER><img  src="/static/images/ajax-loader.gif" /></CENTER>');
};

function stopShowingLoadingImage(){
	$("#newFollow").html(form);
};

function iFrameHeightInit(){
	iFrameHeight = jQuery("iframe",top.document).contents().find('body').attr('scrollHeight')
}

function iFrameHeightIncrement(value){
	newHeight = iFrameHeight + value;
	jQuery("iframe",top.document).height(newHeight);	
	iFrameHeight = newHeight
}