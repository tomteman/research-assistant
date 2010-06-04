var labels
/* list of unique label names with number of occurences */
var uniqueLabels   
/* list of unique label names - only names*/
var uniqueLabelsNames = []
                
var menuStatus = 0;                         
                         
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
function printLabels(){
	$.each(uniqueLabelsNames,function(intIndex, objValue){
		alert(objValue);
		addLabel(objValue);
	});
	
}

                        
function addLabel(labelName, number){
	var newLabel = $("#firstLabel").clone();
	var labelButton = newLabel.find(".labelButton");
	var menuItem = newLabel.find(".menuItem")
	
	newLabel.show();
	labelButton.val(labelName + "("+number+")");
	labelButton.attr("id", labelName);
	labelButton.click( function() { showLabeledArticles(labelButton.attr("id")) } );
	newLabel.find("#menuButton").click( function() {menu($(this).parent().parent().find("#dropDown"));})
	
	menuItem.mouseover( function () {$(this).css("background", "#0078ae")  })
    menuItem.mouseout( function () {$(this).css("background", "#d0e5f5") })  
    
    newLabel.find("#Delete").click( function() { menu( menuItem.parent()); deleteTag(labelButton.attr("id")); });
	newLabel.find("#Remove").click( function() { menu(menuItem.parent()); renameTag(labelButton.attr("id"));  });
	newLabel.find("#Share").click( function() { menu(menuItem.parent()); shareTag(labelButton.attr("id")); });
	$("#labelList").append(newLabel);
	
}


function showLabeledArticles(label_name){
	$("#the_iframe").attr("src", '/ShowArticlesByLabel?Id='+label_name);	
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
	alert(responseText);
	$("#"+responseText).parent().remove();
	$('#popupText').html("label "+ responseText +" was deleted <br/>");
    $('#popupText').dialog({ width: 600 , buttons: { "Ok": function() { $(this).dialog("close"); } }});
}

function renameTag(label_name){
	
}

function shareTag(label_name){
	
}



function menu(div_menu){
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
		getUniqueLabelsNamesList();
	});
}


function getUniqueLabelsNamesList(){
	$.each(uniqueLabels,function(intIndex, objValue){
		uniqueLabelsNames.push(objValue.label_name)
		addLabel(objValue.label_name, objValue.number);
	});
}

function extractUniqueLabelList(){
	$.each(labels, function(intIndex , objValue){
		if (($.inArray(objValue.label_name, uniqueLabels)) == -1)
			uniqueLabels.push(objValue.label_name)
			
		});
}



