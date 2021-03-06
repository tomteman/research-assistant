var labels
/* list of unique label names with number of occurences */
var uniqueLabels    
var index = 0;
var userAgent
maxLabelLength = 22;
function getCurrentUser(){ 
	var user = $.ajax({
		  url: "/getCurrentUser",
		  type: "GET",
		  async: false
		}).responseText
		return user
};

$(function(){
    checkIntroCookie();


	userAgent = navigator.userAgent.toString().toLowerCase();
	if(userAgent.indexOf('chrome') != -1)
		userAgent="chrome"
			
	$("#search-submit").click(function(event){
		if ($("#search-text").val() == ""){
			event.preventDefault()
			event.bind('click')
			}
		});
							
	
				
    $(".labelButton").live("mouseover",function(){ 
    	$(this).tooltip();
    });
    
    $(".labelButton_shared").live("mouseover",function(){ 
    	$(this).tooltip();
    });
    
		
				
	$(".labelButton")
	.button()
	.next()
		.button( {
			text: false,
			icons: {
			primary: "ui-icon-triangle-1-s"
		}}).click( function() {menu($(this).parent());})
	.parent()
	.buttonset();
	
	$(".labelButton_shared")
	.button()
	.next()
		.button( {
			text: false,
			icons: {
			primary: "ui-icon-triangle-1-s"
		}}).click( function() {menu($(this).parent());})
	.parent()
	.buttonset();
	
     getLabelsFromDB();
     getUniqueLabelsFromDB();
    	
     
 });


/////////////////////////////////////////////////////////////////////////

function setHideIntroCookie() {
	document.cookie="intro=" + "off";
}

function setOnIntroCookie() {
	document.cookie="intro=" + "on";
}

function getCookie(c_name){
	if (document.cookie.length>0)
  	{
	c_start=document.cookie.indexOf(c_name + "=");
  	if (c_start!=-1)
    	{
	  c_start=c_start + c_name.length+1;
    	c_end=document.cookie.indexOf(";",c_start);
    	if (c_end==-1) c_end=document.cookie.length;
    	return unescape(document.cookie.substring(c_start,c_end));
    	}
  	}
	return "";
}

function checkIntroCookie() {
	intro = getCookie("intro");
	if (intro !=null && intro != "off") {
		$('.slideshow1Wrapper').show()
		$('.closeBannerButton').show()
		$('.showBannerButton').hide()
	}else{
		$('.slideshow1Wrapper').hide("fast")
		$('.closeBannerButton').hide()
		$('.showBannerButton').show()
	
	}
	
}


function shortenLabelName(labelName){
	if(labelName.length>14)
		return (labelName.slice(0,10)+"...")
	else return labelName
}

function recolorLabelsIniFrame(label_name){
	var iframe = document.getElementById("the_iframe");
	iframe.contentWindow.recolorLabelInstances(label_name)
}

function deleteLabelsIniFrame(label_name){
	var iframe = document.getElementById("the_iframe");
	iframe.contentWindow.deleteLabelInstances(label_name)
}

function renameLabelsIniFrame(old_label_name, new_label_name){
	var iframe = document.getElementById("the_iframe");
	iframe.contentWindow.renameLabelInstances(old_label_name, new_label_name)
}

function addLabel(labelName, number){
	var newLabel = $("#firstLabel").clone();
	var labelButton = newLabel.find(".labelButton");
	var menuItem = newLabel.find(".menuItem");
	var div_menu = menuItem.parent();
	
	newLabel.show();
	newLabel.val(labelName);
	labelButton.attr("title",labelName)
	labelName = shortenLabelName(labelName);
	labelButton.val(labelName + " ("+number+")");
	
	labelButton.click( function() { showLabeledArticles(newLabel.attr("value")) } );
	
	div_menu.val("0");
    newLabel.find("#menuButton").click( function(event) {
    	change_menu_status(div_menu);
		$('body').click(function(){
			if (div_menu.val() != "0")
				change_menu_status(div_menu);
		})

		event.stopPropagation();
    })
    
    
	menuItem.mouseover( function () {$(this).css("background", "#0078ae")  })
    menuItem.mouseout( function () {$(this).css("background", "#d0e5f5") })  
    
    newLabel.find("#Delete").click( function() { change_menu_status( menuItem.parent()); deleteTag(newLabel.attr("value"), true); });
	newLabel.find("#Rename").click( function() { change_menu_status(menuItem.parent()); renameTag(newLabel.attr("value"));  });
	newLabel.find("#Share").click( function() { change_menu_status(menuItem.parent()); shareTag(newLabel.attr("value")); });
	newLabel.find("#SendMail").click( function() { change_menu_status(menuItem.parent()); sendMail(newLabel.attr("value")); });
	$("#labelList").append(newLabel);	
}

function addLabelShared(labelName, number){
	var newLabel = $("#firstLabel_shared").clone();
	var labelButton = newLabel.find(".labelButton_shared");
	var menuItem = newLabel.find(".menuItem_shared");
	var div_menu = menuItem.parent();
	
	newLabel.show();
	newLabel.val(labelName);
	labelButton.attr("title",labelName)
	labelName = shortenLabelName(labelName);
	labelButton.val(labelName + " ("+number+")");
	
	
	labelButton.click( function() { showLabeledArticles(newLabel.attr("value"));
									
									});
	div_menu.val("0");
    newLabel.find("#menuButton_shared").click( function(event) {
    	change_menu_status(div_menu);
		$('body').click(function(){
			if (div_menu.val() != "0")
				change_menu_status(div_menu);
		})

		event.stopPropagation();
    })
    
	menuItem.mouseover( function () {$(this).css("background", "#FFc1c1")  })
    menuItem.mouseout( function () {$(this).css("background", "#FFe4e1") })  
    
    newLabel.find("#Share").click( function() { change_menu_status( menuItem.parent()); shareTag(newLabel.attr("value")); });
	newLabel.find("#UserList").click( function() { change_menu_status(menuItem.parent()); getLabelUserList(newLabel.attr("value"));  });
	newLabel.find("#RemoveMe").click( function() { change_menu_status(menuItem.parent()); removeMeFromLabel(newLabel.attr("value")); });
	newLabel.find("#Duplicate").click( function() { change_menu_status(menuItem.parent()); duplicateLabel(newLabel.attr("value")); });
	newLabel.find("#SendMail").click( function() { change_menu_status(menuItem.parent()); sendMail(newLabel.attr("value")); });
	$("#labelList_shared").append(newLabel);	
}

function handleErrorCode(errorNumber){
	if (errorNumber == -2)
		generatePopUp ("The email address entered is not valid. Please try again.");
	else if (errorNumber == -3)
		generatePopUp ("The user you are trying to share this label with already has a shared label with the same name.<br>If your label is currently private - try to rename and then share.");
	else if (errorNumber == -4 || errorNumber == -5)
		generatePopUp("There were some problems retrieving the information.<br>Please try to refresh this page.");
	else if (errorNumber == -6)
		generatePopUp("Sorry, you cannot share a label with yourself... :)");
	else if (errroNumber == -7)
		generatePopUp("There are some problems connecting to the Data Base.<br>Please make sure you are connected to the internet.");
	else if (errorNumber == -8)
		generatePopUp("There were some problems sending the mail notification to the invited user.<b>However, the label was shared successfully, <br>and the user will see it in his Invitations during his next visit to the site.")
	else generatePopUp("Unknown Error. Sorry.")
}

function generatePopUp(text){
	$('#popupText').html(text+"<br/>");
	$('#popupText').dialog({ 
        open: function() {
        $(this).parents('.ui-dialog-buttonpane button:eq(0)').focus();
      	},
		width: 500 , buttons: { "OK": function() { $(this).dialog("close"); } }});
}


function getLabelUserList(label_name){
	user_list_for_label = {
				   label_name: label_name
					};
	$.ajax({

		type: 'POST',
		url: "/GetSharedLabelUsers",
		data: user_list_for_label,
		success: function(data, textStatus){
			if (data <= 0){
				handleErrorCode(data)
			}
			else{
				generatePopUp("Users sharing this label: <br>" +data)
			}
		}
	});
}

function removeMeFromLabel(label_name){
	$('#popupText').html("Are you sure you want to remove yourself from the label "+ label_name +" ? <br/>");
	$('#popupText').dialog({
		open: function() {
	      $(this).parents('.ui-dialog-buttonpane button:eq(1)').focus(); 
	    },
		
		width: 400 , buttons: { 		
		"No": function() { 
			$(this).dialog("close"); },
		"Yes": function() {
				label_name_to_remove = {
						   label_name: label_name
							};
				$.ajax({
					type: 'POST',
					url: "/RemoveFromSharedLabelDB",
					data: label_name_to_remove,
					success: function(data, textStatus){
						if (data <= 0){
							handleErrorCode(data)
						}
						else{
							removeLabelFromLocalDBandHTML(label_name)
						}
					}
				});
			$(this).dialog("close"); 
			}
		}
	});	
}


function removeLabelFromLocalDBandHTML(label_name) {
	var label = getLabel(label_name);	
	label.remove();
	/* update local data (labels) */
	uniqueLabels = $.grep(uniqueLabels, function (val) { return val.label_name != label_name; });
	labels = $.grep(labels, function(val){return val.label_name != label_name})
	/* delete labels from HTML */
	deleteLabelsIniFrame(label_name)	
}
	
		

function duplicateLabel(label_name){
	label_name_to_duplicate = {
			   label_name: label_name
				};
	$.ajax({
		type: 'POST',
		url: "/DuplicateSharedLabelToPrivate",
		data: label_name_to_duplicate,
		success: function(data, textStatus){
			if (data <= 0){
				handleErrorCode(data)
			}
			else{
				window.location = "/";
			}
		}
	});	
}

function deleteTag(label_name, ask_user_flag){
	if (ask_user_flag == true)
	{
		$('#popupText').html("Are you sure you want to delete the label "+ label_name +" ? <br/>");
	
		$('#popupText').dialog({
			open: function() {
			$(this).parents('.ui-dialog-buttonpane button:eq(1)').focus(); 
	    	},
			width: 400 , buttons: { 		
	    		"No": function() { 
	    		$(this).dialog("close"); 
	    		},
	    		"Yes": function() {
	    			$("#labelName").find("#label_name").val(label_name);
	    			$("#labelName").ajaxSubmit({ success:       deleteResponse,    	// post-submit callback 
		 								 url:      '/RemoveLabelDB',         // override for form's 'action' attribute 
		 								 type:      "GET",
		 								 dataType:  'json'  
		    							});	
	    			$(this).dialog("close"); }
		}
		});
	}
	else
	{
		$("#labelName").find("#label_name").val(label_name);
		$("#labelName").ajaxSubmit({ success:       deleteResponse,    	// post-submit callback 
								 url:      '/RemoveLabelDB',         // override for form's 'action' attribute 
								 type:      "GET",
								 dataType:  'json'  
							});	
	}
	
	
	
}

function deleteResponse(responseText, statusText, xhr, $form)  {
	if (responseText <= 0){
		handleErrorCode(responseText)			
	}
	else{
		removeLabelFromLocalDBandHTML(responseText)
	}
	
		
}

function renameTag(label_name){
	
	$('#renameText').html("Rename label \'"+ label_name +"\' to");
    $("#popup_rename").dialog({
    		open: function() {
	      		$('#newName').focus(); 
	    	},
			width: 500,
			modal: true,
			buttons: {
				'Rename': function() { var newName= $('#newName').val();
										nameIsUsed = labelExists(newName);	
										if (!nameIsUsed){
											$("#labelName").find("#label_name").val(label_name);
											$("#labelName").find("#new_name").val(newName);
											$("#labelName").ajaxSubmit({ success:    renameResponse,    	// post-submit callback 
										 								 url:      '/RenameLabelDB',         // override for form's 'action' attribute 
										 								 type:      "POST",
										 								 dataType:  'json'  
										    							});
											$(this).dialog("close");
										}else{
											generatePopUp("Label with this name already exists. <br>Please choose a different name.")
										}					
    								},
				"Cancel": function() { $(this).dialog("close"); }
				},
			close: function() {
					
			}
    });	
}


function renameResponse(responseText, statusText, xhr, $form)  {
	if (responseText != ""){
	
		index = responseText.indexOf("_|_");
		old_name = responseText.substring(0, index); 
		new_name = responseText.substring( index+3, responseText.length);
		
		
		var label=getLabel(old_name);
		var number = getNumber(old_name);
		label.val(new_name);
		var button = label.find(".labelButton");
		name_to_display = new_name
		button.attr("title",name_to_display)
		name_to_display = shortenLabelName(name_to_display);
		button.val(name_to_display + "("+ number+")");
		
		$.each(uniqueLabels, function (intIndex, objValue) {
			if (objValue.label_name == old_name){
				objValue.label_name = new_name; 
			}
		});
		$.each(labels, function (intIndex, objValue) {
			if (objValue.label_name == old_name){
				objValue.label_name = new_name; 
			}
		});
		
		/* update iframe HTML */
		renameLabelsIniFrame(old_name, new_name);
	

		
	}else{
		generatePopUp("Sorry. DB currently unavailable. Please try again later.")	
	}	
}


function getLabel(name){
	var label = ""
	$(".label").each(function () {if ($(this).val() == name ){										
										label = $(this);}});
	return label	
}


//return true if user has label with given name
function labelExists(name){
	flag = false;
	$.each(uniqueLabels,function(intIndex, objValue){
		if (name == objValue.label_name){
			flag=true;
		}
	});
	return flag;
}

function alertUniqueLabels(){
	$.each(uniqueLabels, function(intIndex, objValue){
		alert("uniqueLabels: "+objValue.label_name+";"+objValue.number+";"+objValue.is_shared);	
	});
}

function alertLabels(){
	$.each(labels, function(intIndex, objValue){
		alert("allLabels: "+objValue.label_name+";"+objValue.key+";"+objValue.is_shared);	
	});
}

/* 2nd param - true=set to shared; false=set to private*/
function toggleLabelShareStatusLocally(label_name, toShare){
	
	$.each(uniqueLabels, function(intIndex, objValue){
		if (objValue.label_name == label_name)
			objValue.is_shared = toShare;
	});
	
	$.each(labels, function(intIndex, objValue){
		if (objValue.label_name == label_name)
			objValue.is_shared = toShare;
	});
	
}

function getShareTarget(label_name){
	
	$('#shareText').html("Share the label \'"+ label_name +"\' with <i>(e-mail address)</i>: ");
    $("#popup_share").dialog({
    		open: function() {
  				$('#userName').focus(); 
			},
			width: 500,
			modal: true,
			buttons: {
				'Share': function() { 
    						var user_name= $('#userName').val();
    						sharedLabel = {
    								   label_name:label_name,
    								   user_name:user_name
    									}
							$.ajax({
								type: 'POST',
								url: "/ShareLabel",
								data: sharedLabel,
								success: function(data, textStatus){
									if (data != 1){
										generatePopUp("We're sorry, an error has occured. Please try again later.")
									}
									else{
										generatePopUp("An email was sent to <b>" + user_name+"</b>")
									}
								}
							});
						$(this).dialog("close");},
				"Cancel": function() { $(this).dialog("close"); }
				},
			close: function() {
					}
    });	
}

function sendMail(label_name){
	$('#shareText').html("Email the contents of the label \'"+ label_name +"\' to <i>(e-mail address)</i>: ");
    $("#popup_share").dialog({
    		open: function() {
  				$('#userName').focus(); 
			},
			width: 500,
			modal: true,
			buttons: {
				'Send': function() { 
    						var user_name= $('#userName').val();
    						sharedLabel = {
    								   label_name:label_name,
    								   user_name:user_name
    									}

							$.ajax({
								type: 'POST',
								url: "/SendLabel",
								data: sharedLabel,
								success: function(data, textStatus){
									if (data !="true"){
										generatePopUp("We're sorry, an error has occured. Please try again later.")
									}
									else{
										generatePopUp("An email was sent to <b>" + user_name+"</b>.")
									}
								}
							});
						$(this).dialog("close");},
				"Cancel": function() { $(this).dialog("close"); }
				},
			close: function() {
					}
    });	
}



function replacePrivateLabelUIWithShared(label_name){
	toggleLabelShareStatusLocally(label_name, true);
	
	
	/* update HTML in iFrame*/
	recolorLabelsIniFrame(label_name)
	
	/* remove old private label button in sidebar */
	var label = getLabel(label_name);
	label.remove();
	
	/* create new shared label button in sidebar */
	uniqueLabel = $.grep(uniqueLabels, function(objValue){
		return objValue.label_name == label_name});	
	addLabelShared(label_name, uniqueLabel[0].number);
}

function shareTag(label_name){
	/* get username to share label with */
	
	getShareTarget(label_name);
	
	
	/* update DB and local parameters */
	$.get("/ShareLabel?Id="+label_name, function(data){	
	});
	
	
}


function printLabels(){
	$.each(uniqueLabels,function(intIndex, objValue){
		if (objValue.is_shared)
			addLabelShared(objValue.label_name, objValue.number);
		else
			addLabel(objValue.label_name, objValue.number);
	});
}

                       
function inc(labelName){
	var label = getLabel(labelName);
	var button = label.find(".labelButton");
	var namePlusNumber = button.val();
	var currNumber = getNumber(labelName, false);
	labelName = shortenLabelName(labelName)
	button.val(labelName + " ("+(currNumber+1)+")");
}

function inc_shared(labelName){
	var label = getLabel(labelName);
	var button = label.find(".labelButton_shared");
	var namePlusNumber = button.val();
	var currNumber = getNumber(labelName, true);
	labelName = shortenLabelName(labelName)
	button.val(labelName + " ("+(currNumber+1)+")");
}

function dec(labelName){
	var label = getLabel(labelName);
	var button = label.find(".labelButton");
	var namePlusNumber = button.val();
	var currNumber = getNumber(labelName, false);
	labelName = shortenLabelName(labelName)
	button.val(labelName + " ("+(currNumber-1)+")");
}

function dec_shared(labelName){
	var label = getLabel(labelName);
	var button = label.find(".labelButton_shared");
	var namePlusNumber = button.val();
	var currNumber = getNumber(labelName, true);
	labelName = shortenLabelName(labelName)
	button.val(labelName + " ("+(currNumber-1)+")");
}



function getNumber(labelName, isShared){
	var label = getLabel(labelName);
	if (isShared)
		var button = label.find(".labelButton_shared");
	else
		var button = label.find(".labelButton");
	var namePlusNumber = button.val();
	
	var firstI= namePlusNumber.indexOf("(");
	number = namePlusNumber.substring(firstI+1,namePlusNumber.length-1 );
	return  parseInt(number);
}



function showLabeledArticles(label_name){
	$("#the_iframe").attr("src", '/ShowArticlesByLabel?&action_type=ShowLabel&Id='+label_name);
}






function change_menu_status(div_menu){
    if (div_menu.val() == "0"){
        div_menu.show();
        div_menu.val("1")

    }else{
        div_menu.hide();
        div_menu.val("0")
       
    }   
}



                         

function getLabelsFromDB(){
	$.getJSON('/GetAllLabels?Type=All',function(data){
		labels = data;			
	});
}

function getUniqueLabelsFromDB(){
	$.getJSON('/GetAllLabels?Type=Unique',function(data){
		uniqueLabels = data;
		index=0;
		printLabels();
	});
}

/*
 * updates number of My follows/ Pending/Suggestions Invitations (the number in parentheses)
 * hrefName = "myFollows"/"myPendings"
 * increase = 1 to increase the number, 0 to decrease
 * 
 */
function updateNumber(hrefName, increase){
	
	var hrefFullName = $("#"+hrefName).text();
	var bracket_index = hrefFullName.indexOf("(")
	sNumber = hrefFullName.substring(bracket_index+1, hrefFullName.length-1 )
	number = parseInt(sNumber);
	if (increase) {
		number += 1;
	}else{
		number -= 1;
	}
	
	hrefFullName = hrefFullName.substring(0, bracket_index+1).concat(number.toString()+")")
	$("#"+hrefName).text(hrefFullName);		
}



