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
	newLabel.show();
	labelButton.val(labelName + "("+number+")");
	labelButton.attr("id", labelName);
	labelButton.click( function() { showLabeledArticles(labelButton.attr("id")) } );
	newLabel.find("#menuButton").click( function() {menu($(this).parent());})
	
	$("#labelList").append(newLabel);
	
}


function showLabeledArticles(label_name){
	$("#the_iframe").attr("src", '/ShowArticlesByLabel?Id='+label_name);
	
}

function menu(parent){
	if (menuStatus == 0){
		parent.parent().find("#dropDown").show();
		menuStatus=1;
	}else{
		parent.parent().find("#dropDown").hide();
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



