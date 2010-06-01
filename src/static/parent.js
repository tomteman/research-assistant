var labels
/* list of unique label names with number of occurences */
var uniqueLabels   
/* list of unique label names - only names*/
var uniqueLabelsNames = []

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
	});
}

function extractUniqueLabelList(){
	$.each(labels, function(intIndex , objValue){
		if (($.inArray(objValue.label_name, uniqueLabels)) == -1)
			uniqueLabels.push(objValue.label_name)	
		});
}

$(function(){
	getLabelsFromDB();
	getUniqueLabelsFromDB();
});


