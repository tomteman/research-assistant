var labels
/* list of unique label names with number of occurences */
var uniqueLabels   

var labelToRecolor          
var menuStatus = 0;   
var index = 0;
                  

$(function(){
	
	$(".labelButton")
	.button()
	.click( function() {alert( "Running the last action" );})
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


function deleteTag(label_name){
	$("#labelName").find("#label_name").val(label_name);
	$("#labelName").ajaxSubmit({ success:       deleteResponse,    	// post-submit callback 
 								 url:      '/RemoveLabelDB',         // override for form's 'action' attribute 
 								 type:      "GET",
 								 dataType:  'json'  
    							});
}

function deleteResponse(responseText, statusText, xhr, $form)  {
	if (responseText != ""){
		var label = getLabel(responseText);								
		label.remove();
		uniqueLabels = $.grep(uniqueLabels, function (val) { return val.label_name != responseText; });
														
		$('#popupText').html("label "+ responseText +" was deleted <br/>");
		$('#popupText').dialog({ width: 400 , buttons: { "Ok": function() { $(this).dialog("close"); } }});
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
	
		
		$.each(uniqueLabels, function (intIndex, objValue) {if (objValue.label_name == old_name){
											alert("found" + objValue.label_name);
											objValue.label_name = new_name; 
										}});
	
		$('#popupText').html("label \'"+ old_name +"\' was renamed to " + new_name );
		$('#popupText').dialog({ width: 400 , buttons: { "Ok": function() { $(this).dialog("close"); } }});
		
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






function shareTag(label_name){
	
}


function printLabels(){
	$.each(uniqueLabels,function(intIndex, objValue){
		addLabel(objValue.label_name, objValue.number);
	});
}

                       

function inc(labelName){
	var label = getLabel(labelName);
	var button = label.find(".labelButton");
	var namePlusNumber = button.val();
	var currNumber = getNumber(labelName);
	button.val(button.attr('id') + "("+(currNumber+1)+")");
	
}


function dec(labelName){
	var label = getLabel(labelName);
	var button = label.find(".labelButton");
	var namePlusNumber = button.val();
	var currNumber = getNumber(labelName);
	button.val(button.attr('id') + "("+(currNumber-1)+")");
}



function getNumber(labelName){
	var label = getLabel(labelName);
	var button = label.find(".labelButton");
	var namePlusNumber = button.val();
	var firstI = label.val().length;
	number = namePlusNumber.substring(firstI+1,namePlusNumber.length );
	return  parseInt(number);
}



function showLabeledArticles(label_name){
	$("#the_iframe").attr("src", '/ShowArticlesByLabel?Id='+label_name);	
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
