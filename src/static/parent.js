var labels
/* list of unique label names with number of occurences */
var uniqueLabels   
var menuStatus = 0;   
var index = 0;
var userAgent         

function checkIfUserLoggedIn()
$.get("/getCurrentUser",function(data){ 
	alert(data)
});

$(function(){
	checkIfUserLoggedIn()
	userAgent = navigator.userAgent.toString().toLowerCase();
		if(userAgent.indexOf('chrome') != -1)
			userAgent="chrome"
				
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
	labelButton.val(labelName + "("+number+")");
	
	
	labelButton.click( function() { showLabeledArticles(newLabel.attr("value")) } );
	
	newLabel.find("#menuButton").click( function() {change_menu_status($(this).parent().parent().find("#dropDown"));})
	
	menuItem.mouseover( function () {$(this).css("background", "#0078ae")  })
    menuItem.mouseout( function () {$(this).css("background", "#d0e5f5") })  
    
    newLabel.find("#Delete").click( function() { change_menu_status( menuItem.parent()); deleteTag(newLabel.attr("value")); });
	newLabel.find("#Rename").click( function() { change_menu_status(menuItem.parent()); renameTag(newLabel.attr("value"));  });
	newLabel.find("#Share").click( function() { change_menu_status(menuItem.parent()); shareTag(newLabel.attr("value")); });
	$("#labelList").append(newLabel);	
}

function addLabelShared(labelName, number){
	var newLabel = $("#firstLabel_shared").clone();
	var labelButton = newLabel.find(".labelButton_shared");
	var menuItem = newLabel.find(".menuItem_shared");
	var div_menu = menuItem.parent();
	
	newLabel.show();
	newLabel.val(labelName);
	labelButton.val(labelName + "("+number+")");
	
	
	labelButton.click( function() { showLabeledArticles(newLabel.attr("value")) } );
	
	newLabel.find("#menuButton_shared").click( function() {change_menu_status($(this).parent().parent().find("#dropDown_shared"));})
	
	menuItem.mouseover( function () {$(this).css("background", "#0078ae")  })
    menuItem.mouseout( function () {$(this).css("background", "#d0e5f5") })  
    
    newLabel.find("#Delete").click( function() { change_menu_status( menuItem.parent()); deleteTag(newLabel.attr("value")); });
	newLabel.find("#Rename").click( function() { change_menu_status(menuItem.parent()); renameTag(newLabel.attr("value"));  });
	newLabel.find("#Share").click( function() { change_menu_status(menuItem.parent()); shareTag(newLabel.attr("value")); });
	$("#labelList_shared").append(newLabel);	
}

function deleteTag(label_name){
	$('#popupText').html("Are you sure you want to delete the label "+ label_name +" ? <br/>");
	$('#popupText').dialog({ width: 400 , buttons: { 		
		"No": function() { 
			$(this).dialog("close"); },
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

function deleteResponse(responseText, statusText, xhr, $form)  {
	if (responseText != ""){
		var label = getLabel(responseText);								
		label.remove();
		
		/* update local data (labels) */
		uniqueLabels = $.grep(uniqueLabels, function (val) { return val.label_name != responseText; });
		labels = $.grep(labels, function(val){return val.label_name != responseText})
		
		/* delete labels from HTML */
		deleteLabelsIniFrame(responseText)				
	}
	else{
		$('#popupText').html("Sorry. DB currently unavailable. Please try again later. <br/>");
		$('#popupText').dialog({ width: 400 , buttons: { "Ok": function() { $(this).dialog("close"); } }});
	
	}
	
		
}

function renameTag(label_name){
	
	$('#renameText').html("Rename label \'"+ label_name +"\' to");
    $("#popup_rename").dialog({
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
											$('#popupText').html("Label with this name already exists <br/>");
											$('#popupText').dialog({ width: 400 , zIndex: 3999, buttons: { "Ok": function() { $(this).dialog("close"); } }});
											
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
		button.val(new_name + "("+ number+")");
	
		
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
		$('#popupText').html("Sorry. DB currently unavailable. Please try again later. <br/>");
		$('#popupText').dialog({ width: 400 , buttons: { "Ok": function() { $(this).dialog("close"); } }});
	
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
	
	$('#shareText').html("Share the label \'"+ label_name +"\' with: ");
    $("#popup_share").dialog({
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
									if (data <= 0){
										alert(data)
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


function shareTag(label_name){
	/* get username to share label with */
	
	getShareTarget(label_name);
	
	
	/* update DB and local parameters */
	$.get("/ShareLabel?Id="+label_name, function(data){	
	});
	
	//toggleLabelShareStatusLocally(label_name, true);
	
	
	/* update HTML in iFrame*/
	//recolorLabelsIniFrame(label_name)
	
	/* remove old private label button in sidebar */
//	var label = getLabel(label_name);
//	label.remove();
//	
//	/* create new shared label button in sidebar */
//	uniqueLabel = $.grep(uniqueLabels, function(objValue){
//		return objValue.label_name == label_name});	
//	addLabelShared(label_name, uniqueLabel[0].number);
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
	button.val(labelName + "("+(currNumber+1)+")");
}

function inc_shared(labelName){
	var label = getLabel(labelName);
	var button = label.find(".labelButton_shared");
	var namePlusNumber = button.val();
	var currNumber = getNumber(labelName, true);
	button.val(labelName + "("+(currNumber+1)+")");
}

function dec(labelName){
	var label = getLabel(labelName);
	var button = label.find(".labelButton");
	var namePlusNumber = button.val();
	var currNumber = getNumber(labelName, false);
	button.val(labelName + "("+(currNumber-1)+")");
}

function dec_shared(labelName){
	var label = getLabel(labelName);
	var button = label.find(".labelButton_shared");
	var namePlusNumber = button.val();
	var currNumber = getNumber(labelName, true);
	button.val(labelName + "("+(currNumber-1)+")");
}



function getNumber(labelName, isShared){
	var label = getLabel(labelName);
	if (isShared)
		var button = label.find(".labelButton_shared");
	else
		var button = label.find(".labelButton");
	var namePlusNumber = button.val();
	var firstI = label.val().length;
	number = namePlusNumber.substring(firstI+1,namePlusNumber.length );
	return  parseInt(number);
}



function showLabeledArticles(label_name){
	$("#the_iframe").attr("src", '/ShowArticlesByLabel?&action_type=ShowLabel&Id='+label_name);
}






function change_menu_status(div_menu){
	if (menuStatus == 0){
		div_menu.show();
		menuStatus=1;

	}else{
		div_menu.hide();
		menuStatus=0;
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
