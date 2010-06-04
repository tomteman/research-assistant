var resultsWithParams
var iFrameHeight           
var labelUniqueId = 0

function displayTagsOnResults(resultsJSON)
{
	 resultsWithParams = eval("("+ resultsJSON+ ")");
	 displayTags();
	 iFrameHeightInit()
	 /* add hiehgt to iframe for label adders (autocomplete) */
	 iFrameHeightIncrement(10*15)

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
	articleKey = resultsWithParams.results[articleNumber].key;
	x= $("#"+articleKey)
	
	str = "<div style=\"display: inline\" class=\"labelButton L" + labelUniqueId + " " + articleKey + "\">" +
			"<div style=\"display: inline\">" +
				"<button id=\"labelname\" class=\"fg-button L" + labelUniqueId +" ui-button ui-button-label ui-widget ui-state-default ui-corner-all\" input type=\"submit\">" + parent.labels[labelListIndex].label_name + "</button>" +
				"<button id=\"closelabel\" class=\"fg-button-x L" + labelUniqueId +" ui-button ui-button-label-x ui-widget ui-state-default ui-corner-all\" input type=\"submit\">x</button>" +
			"</div>" +
		"</div>"
	$(x).prepend(str)
	
	/* check is label is shared or private and color it appropriately */
	if (parent.labels[labelListIndex].is_shared){
		$(".fg-button.L"+ labelUniqueId +"\"").addClass("ui-button-shared");
		$(".fg-button-x.L"+ labelUniqueId +"\"").addClass("ui-button-shared");
	}
	else{ 					
		$(".fg-button.L"+ labelUniqueId +"\"").addClass("ui-button-private");
		$(".fg-button-x.L"+ labelUniqueId +"\"").addClass("ui-button-private");
	}
	str = "<div class=\"commentbox L" + labelUniqueId + "\">" +
				"<textarea class=\"commentcontent\" id=\"L" + labelUniqueId + "\"></textarea>" +
				"<div class=\"button_block\" id=\"L" + labelUniqueId +"\">" +
					"<input type=\"submit\" id=\"save\" value=\" Save \"/>" +
					"<input type=\"submit\" id=\"close\" value=\" Close\" />" +
				"</div>" +
			"</div>" 
	$(x).append(str)
	$(".commentbox.L" + labelUniqueId).hide()	
	labelUniqueId+=1
	return labelUniqueId;
}


/* recolor labels that were marked as private/shared*/
function recolorLabels(label_name, is_shared){
	$(".fg-button").each(function(intIndex, objValue){
		if ($(this).text() == label_name){
			if (is_shared){
				$(this).removeClass("ui-button-private")
				$(this).addClass("ui-button-shared");
				$(this).next().removeClass("ui-button-private")
				$(this).next().addClass("ui-button-shared");		
			}
			else{
				$(this).removeClass("ui-button-shared")
				$(this).addClass("ui-button-private");
				$(this).next().removeClass("ui-button-shared")
				$(this).next().addClass("ui-button-private");			
			}
		}
	});
}


/* display a label that was just added to an article */
function displayLabelOnArticleByKey(labelArticleKey,label_name){
	
	x= $("#"+labelArticleKey)
	
	str = "<div style=\"display: inline\" class=\"labelButton L" + labelUniqueId + " " + labelArticleKey + "\">" +
			"<div style=\"display: inline\">" +
				"<button id=\"labelname\" class=\"fg-button L" + labelUniqueId +" ui-button ui-button-label ui-widget ui-state-default ui-corner-all\" input type=\"submit\">" + label_name + "</button>" +
				"<button id=\"closelabel\" class=\"fg-button-x L" + labelUniqueId + " ui-button ui-button-label-x ui-widget ui-state-default ui-corner-all\" input type=\"submit\">x</button>" +
			"</div>" +
		"</div>"
	$(x).prepend(str)
	/* new labels are 'private' by default */
	$(".fg-button.L"+ labelUniqueId +"\"").addClass("ui-button-private");
	$(".fg-button-x.L"+ labelUniqueId +"\"").addClass("ui-button-private");
	
	str = "<div class=\"commentbox L" + labelUniqueId + "\">" +
				"<textarea class=\"commentcontent\" id=\"L" + labelUniqueId + "\"></textarea>" +
				"<div class=\"button_block\" id=\"L" + labelUniqueId +"\">" +
					"<input type=\"submit\" id=\"save\" value=\" Save \"/>" +
					"<input type=\"submit\" id=\"close\" value=\" Close\" />" +
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
			if (objValue.number == 0){
				removeLabelFromUniqueLabelsNamesList(label_name);
			}
			return false
		}
	});
}	



function removeLabelFromUniqueLabelsNamesList(label_name){
	parent.uniqueLabelsNames = $.grep(parent.uniqueLabelsNames, function(val) { return val != label_name; });
}

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
	labelToRemoveFromDB = {
			   label_name:label_name,
			   article_key:article_key
				}
	$.ajax({
		  type: 'POST',
		  url: "/RemoveLabelDB",
		  data: labelToRemoveFromDB
		});	
}

function findLabelIndexInGlobalLabelsByKeyAndName(article_key, label_name){
	index = -1
	$.each(parent.labels, function(intIndex,objValue){
		if (objValue.label_name == label_name && objValue.article_key == article_key){
			index = intIndex
		};
	});
	return index
}

function saveComment(commentContent, article_key, label_name){

	labelIndex = findLabelIndexInGlobalLabelsByKeyAndName(article_key, label_name)
	parent.labels[labelIndex].comment = commentContent
	
	commentToDB = {
				   comment_content:commentContent,
				   label_name:label_name,
				   article_key:article_key
				}
	$.ajax({
		  type: 'POST',
		  url: "/UpdateArticleLabelDB",
		  data: commentToDB
		 
		});	
}


function iFrameHeightIncrement(value){
	newHeight = iFrameHeight + value;
	jQuery("iframe",top.document).height(newHeight);	
	iFrameHeight = newHeight
}



function iFrameHeightDecrement(value){
	newHeight = iFrameHeight - value;
	jQuery("iframe",top.document).height(newHeight);
	iFrameHeight = newHeight
}

function iFrameHeightInit(){
	iFrameHeight = jQuery("iframe",top.document).contents().find('body').attr('scrollHeight')
}

$(function(){
	
	
	$(".labelBox").hide()
	
	$(".commentcontent").live("click", function(){
        $(this).focus()
        classList = $(this).parent().attr('class').split(' ');
        labelKey = classList[1]
        $(".commentcontent.#"+labelKey).animate({"height": "85px", "width": "500px"}, "fast" );
        $(".button_block.#"+labelKey).slideDown("fast");
        return false;
    });
  
	$(".commentcontent").live("click", function(){
		$(this).focus()
		classList = $(this).parent().attr('class').split(' ');
		labelKey = classList[1]            
		$(".commentcontent.#"+labelKey).animate({"height": "85px", "width": "500px"}, "fast" );
		$(".button_block.#"+labelKey).slideDown("fast");
		return false;
	});

    $("#close").live("click",function(){
        classList = $(this).parent().parent().attr('class').split(' ');
        labelKey = classList[1]
        $(".commentcontent.#"+labelKey).animate({"height": "30px", "width": "200px"}, "fast" );
        $(".button_block.#"+labelKey).slideUp("fast");
        $(".commentcontent.#"+labelKey).blur()
        $(".commentbox."+labelKey).hide()
        iFrameHeightDecrement(100)
        return false;
        });
	

    $("#save").live("click",function(){
        classList = $(this).parent().parent().attr('class').split(' ');
        labelKey = classList[1]
        $(".commentcontent.#"+labelKey).blur()
         $(".commentcontent.#"+labelKey).animate({"height": "30px", "width": "200px"}, "fast" );
         $(".button_block.#"+labelKey).slideUp("fast");
        commentContent = $(".commentcontent.#"+labelKey).val()
        label_name = $(".fg-button."+labelKey).text()
        article_key = $(this).parent().parent().parent().closest("div").attr("id");
        saveComment(commentContent,article_key,label_name)
         return false;

    });
	
	$(".fg-button").livequery(function(){
		/* open comment box */
		$(this).button();
		$(this).click(function() {
			classList = $(this).parent().parent().attr('class').split(' ');
			labelKey = classList[1]
			article_key = classList[2]
			label_name = $(this).text();
			labelIndex = findLabelIndexInGlobalLabelsByKeyAndName(article_key,label_name)
			comment = parent.labels[labelIndex].comment
			$(".commentbox."+labelKey+" .commentcontent").val(comment)
		
			$(".commentbox."+labelKey).show()
			iFrameHeightIncrement(100)
			/* update DB and globals*/
		});
	});
	
	$(".fg-button-x").livequery(function(){
		$(this).button( {
		text: false,
		icons: {
			primary: "ui-icon-circle-close"
		}
		});
		$(this).click(function(){
		/* remove tag from DB and global variables */
			classList = $(this).parent().parent().attr('class').split(' ');
			labelKey = classList[1]
			article_key = classList[2];
			label_name = $(this).prev().text();
			removeLabelFromArticle(label_name, article_key)
		/* look for an open comment box and close it */
			$(".commentbox."+labelKey).hide()
			$(".commentcontent.#"+labelKey).hide()
		/* remove tag from HTML */
			$(this).prev().remove();
			$(this).remove();
		});
	});
	
	$(".labelButton").livequery(function(){
		$(this).buttonset();
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
            select: function(data, value){ // Callback function, triggered if one of the suggested options is selected,
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
	    selectedLabelBox.focus();
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


