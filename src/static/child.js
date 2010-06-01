var resultsWithParams
var addLabelButtonPressed = new Array(10)
var commentButtonPressed = new Array(10)                   
var labelUniqueId = 0

function displayTagsOnResults(resultsJSON)
{
	 resultsWithParams = eval("("+ resultsJSON+ ")");
	 displayTags()
	 return
}

function indexOfArticleInResultsFromKey(article_key){
	result = -1;
	$.each(resultsWithParams.results, function(intIndex, objValue){
		if (objValue.key == article_key)
			result = intIndex
	});
	return result
}
	

function displayTags(){
	$.each(resultsWithParams.results,function(articleNumber , objValue){
		/* return list of user labels matching article key (indexes in label list) */
		labelListIndexes = articleKeyInLabelList(resultsWithParams.results[articleNumber].key, articleNumber);
		if (labelListIndexes.length){
			for (var i = 0, j = labelListIndexes.length; i<j; i++){
				displayLabelOnArticle(articleNumber,labelListIndexes[i]);
			}
		}
	});
}


/* checks if the given article key appears in the user's label list */
function articleKeyInLabelList(key, articleNumber){	
	var labelList = parent.labels
	var labelListIndexes = []
	$.each(labelList,function(intIndex , objValue){
		if(objValue.article_key == key){
			labelListIndexes.push(intIndex);
		}
	});
	return labelListIndexes;
}

function displayLabelOnArticle(articleNumber,labelListIndex){
	x= $("#"+resultsWithParams.results[articleNumber].key)		
	str = "<button class=\"fg-button ui-state-default ui-corner-all L" + labelUniqueId + "\" type=\"submit\">"
		+parent.labels[labelListIndex].label_name+"</button>" +
		"<button class=\"fg-button-x\" type=\"submit\">x</button>"
	$(x).prepend(str)
	str = "<div class=\"commentbox L" + labelUniqueId + "\">" +
				"<textarea class=\"commentcontent\" id=\"L" + labelUniqueId + "\"></textarea>" +
				"<div class=\"button_block\" id=\"L" + labelUniqueId +"\">" +
					"<input type=\"submit\" id=\"button\" value=\" Save \"/>" +
					"<input type=\"submit\" id=\"cancel\" value=\" Close\" />" +
				"</div>" +
			"</div>" 
	
			
	$(x).append(str)
	$(".commentbox.L" + labelUniqueId).hide()	
	labelUniqueId+=1
}

function displayLabelOnArticleByKey(labelArticleKey,label_name){
	x= $("#"+labelArticleKey)		
	str = "<button class=\"fg-button ui-state-default ui-corner-all L" + labelUniqueId + "\" type=\"submit\">"
		+label_name+"</button>" +
		"<button class=\"fg-button-x\" type=\"submit\">x</button>"
	$(x).prepend(str)
	commentId= labelArticleKey
	str = "<div class=\"commentbox L" + labelUniqueId + "\">" +
				"<textarea class=\"commentcontent\" id=\"L" + labelUniqueId + "\"></textarea>" +
				"<div class=\"button_block\" id=\"L" + labelUniqueId +"\">" +
					"<input type=\"submit\" id=\"button\" value=\" Save \"/>" +
					"<input type=\"submit\" id=\"cancel\" value=\" Close\" />" +
				"</div>" +
			"</div>" 
	
	
	$(x).append(str)
	$(".commentbox.L" + labelUniqueId).hide()	
	labelUniqueId+=1
}
/* This function is called when a user inputs a new (unknown) label name */
function addNewLabel(label_name, labelArticleKey){
	if(label_name.length < 1) return false
	/* add label to labels */
	addLabelToGlobalLabels(label_name, labelArticleKey)
	/* convert labeled article to JSON */
	index = indexOfArticleInResultsFromKey(labelArticleKey)
	var ArticleDataWithLabelName = []
	ArticleDataWithLabelName.push(resultsWithParams.results[index])
	ArticleDataWithLabelName.push(label_name)
	
	articleJSON = $.toJSON(ArticleDataWithLabelName)
	/* update DB */
	
	$.ajax({
		  type: 'POST',
		  url: "/UpdateLabelDB",
		  data: articleJSON
		});	
	/* update number of labels in uniqueLabels */
	var newLabel = {
			label_name: label_name,
			number: 0
				};
			
	parent.uniqueLabels.push(newLabel);
	parent.uniqueLabelsNames.push(label_name);
	incrementUniqueLabelCount(label_name);
	
	/* show label in HTML */
	
	displayLabelOnArticleByKey(labelArticleKey,label_name)
//	alert(parent.uniqueLabelsNames[0].label_name)
}
function labelExistsInArticle(label_name, labelArticleKey){
	var flag = false
	$.each(parent.labels, function(intIndex,objValue){
		if (objValue.label_name == label_name && objValue.article_key == labelArticleKey){
			flag = true
		};
});
	return flag
}
	
/* This function is called when auto complete matches a result */
function existingLabelSelected(label_name, labelArticleKey){
	/* add label to labels */
	if (!labelExistsInArticle(label_name, labelArticleKey)){
		addLabelToGlobalLabels(label_name, labelArticleKey)
		/* convert labeled article to JSON */
		index = indexOfArticleInResultsFromKey(labelArticleKey)
		var ArticleDataWithLabelName = []
		ArticleDataWithLabelName.push(resultsWithParams.results[index])
		ArticleDataWithLabelName.push(label_name)
		articleJSON = $.toJSON(ArticleDataWithLabelName)
		/* update DB */
		$.ajax({
			  type: 'POST',
			  url: "/UpdateLabelDB",
			  data: articleJSON
			});	
		/* update number of labels in uniqueLabels */
		
		incrementUniqueLabelCount(label_name);
		
		/* show label in HTML */
		
		displayLabelOnArticleByKey(labelArticleKey,label_name)
	}
}

function incrementUniqueLabelCount(label_name){
	$.each(parent.uniqueLabels, function(intIndex,objValue){
		if (objValue.label_name == label_name){
			objValue.number += 1;
			return false
		}
	});
}

function decrementUniqueLabelCount(label_name){
	$.each(parent.uniqueLabels, function(intIndex,objValue){
		if (objValue.label_name == label_name){
			objValue.number -= 1;
			return false
		}
	});
}	


/*
  function removeLabelFromUniqueLabelsNamesList(label_name){
	parent.uniqueLabelsNames = $.grep(parent.uniqueLabelsNames, function(val) { return val != label_name; });
}
*/
function removeLabelFromGlobalLabels(label_name, article_key){
	parent.labels = $.grep(parent.labels, function(label , i) { 
		return (label.label_name != label_name || label.article_key != article_key);
	});
}

function addLabelToGlobalLabels(label_name, labelArticleKey){
	var labelObject = {
	   		comment: "",
	   		is_shared: false,
	   		users_list: [],
	   		serialized_article: "",
	   		label_name: label_name,
	   		article_key: labelArticleKey			                
		   };
	parent.labels.push(labelObject)
}

function removeLabelFromArticle(label_name, article_key){
	/* decrement label occurence in uniqueLabels (and remove from uniqueLabelsNames if reached 0) */
	decrementUniqueLabelCount(label_name);
	/* remove from global labels list */
	removeLabelFromGlobalLabels(label_name, article_key);
}


$(function(){
	$(".labelBox").hide()
	
	$(".commentcontent").live("focus", function(){
		classList = $(this).parent().attr('class').split(' ');
		labelKey = classList[1]            
		$(".commentcontent.#"+labelKey).animate({"height": "85px", "width": "500px"}, "fast" );
		$(".button_block.#"+labelKey).slideDown("fast");
		return false;
	});
	
	$(".commentcontent").live("blur", function(){
		classList = $(this).parent().attr('class').split(' ');
		labelKey = classList[1]            
		$(".commentcontent.#"+labelKey).animate({"height": "30px", "width": "200px"}, "fast" );
		$(".button_block.#"+labelKey).slideUp("fast");
		return false;
	});

	$("#cancel").live("click",function(){
		classList = $(this).parent().parent().attr('class').split(' ');
		labelKey = classList[1]
		$(".commentbox."+labelKey).hide()
		return false;
		});

	$("#cancel").live("click",function(){
		classList = $(this).parent().parent().attr('class').split(' ');
		labelKey = classList[1]
		$(".commentbox."+labelKey).hide()
		return false;
		});

		
	$(".fg-button-x").live("click", function(){
		/* remove tag from DB and global variables */
		article_key = ($(this).closest("div").attr("id"));
		label_name = ($(this).prev().html());
		removeLabelFromArticle(label_name, article_key)
		/* remove tag from HTML */
		$(this).prev().remove();
		$(this).remove();
	});
	
	$(".fg-button").live("click", function(){
		/* open comment box */
		classList = $(this).attr('class').split(' ');
		labelKey = classList[3]
		$(".commentbox."+labelKey).show()	
		/* update DB and globals*/
		
	});
	$(".addLabel").click(function(){
		var classList =$(this).parent().parent().closest("div").attr('class').split(' ');
		var articleClassID = classList[1]
		var labelArticleKey = ($(this).parent().parent().closest("div").attr("id"));
		//$(this).attr("disabled", "disabled");
		$(".labelBox").val("")
	    $(this).parent().next(".labelBox").slideToggle(200)
    	var ac = $(this).parent().next(".labelBox").autocomplete({
            minChars: 1, // Minimum request length for triggering autocomplete
            delimiter: /(,|;)\s*/, // Delimiter for separating requests (a character or regex)
            maxHeight: 400, // Maximum height of the suggestion list, in pixels
            width: 300, // List width
            zIndex: 9999, // List's z-index
            deferRequestBy: 0, // Request delay (milliseconds), if you prefer not to send lots of requests while the user is typing. I usually set the delay at 300 ms.
            onSelect: function(data, value){ // Callback function, triggered if one of the suggested options is selected,
    			alert("XXX")
    			existingLabelSelected(data, labelArticleKey)
    			$(".article."+articleClassID).closest(".labelBox").val("")
    			$(".article."+articleClassID).closest(".labelBox").hide()
    			
    			},
            lookup: parent.uniqueLabelsNames, // List of suggestions for local autocomplete
            multiple: true,
            multipleSeparator: ",",
            selectFirst: false
            
        });
	    ac.enable();
	    /* handle "user pressed Enter key" event */
	    $('.labelBox').keyup(function(e) {
	    	if(e.keyCode == 13) {
	    		
	    		/* get all the labels the user inputed for this article, and place them in an array */
	    		var label_names = []
	    		label_names = $(this).val().split(',');
	    		/* recognize which article is being labeled */
	    		labelArticleKey = ($(this).parent().closest("div").attr("id"));
	    		$(this).val("")
    			$(this).hide()
	    		for (var i = 0, j = label_names.length; i<j; i++){
	    			/* if this label already exists */
	    			if ($.inArray(label_names[i], parent.uniqueLabelsNames) != -1)
	    				existingLabelSelected(label_names[i], labelArticleKey)
	    			else
	    			/* if this is a new label */
	    				addNewLabel(label_names[i], labelArticleKey)		
	    		}
	    	}
		});
	   })
});


