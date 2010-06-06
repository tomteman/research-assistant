var resultsWithParams
var iFrameHeight           
var labelUniqueId = 0
var uniqueLabelsNames = []
var user


function displayTagsOnResults(resultsJSON)
{
	 resultsWithParams = eval("("+ resultsJSON+ ")");
	 displayLabels();
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
	

function displayLabels(){
	$.each(resultsWithParams.results,function(intIndex , objValue){
		/* return list of user labels matching article key (indexes in label list) */
		labelListIndexes = articleKeyInLabelList(resultsWithParams.results[intIndex].key, intIndex);
		if (labelListIndexes.length){
			for (var i = 0, j = labelListIndexes.length; i<j; i++){
				displayLabelOnArticle(intIndex,labelListIndexes[i]);
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
				"<button id=\"labelname\" class=\"fg-button L" + labelUniqueId +" ui-button ui-button-label ui-widget ui-state-default ui-corner-all\" title=\"Click to add a Comment\" input type=\"submit\">" + parent.labels[labelListIndex].label_name + "</button>" +
				"<button id=\"closelabel\" class=\"fg-button-x L" + labelUniqueId +" ui-button ui-button-label-x ui-widget ui-state-default ui-corner-all\" input type=\"submit\">Delete this label</button>" +
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
	
	str = "<span class=\"comment_name L" + labelUniqueId + "\"></span>" + 
			"<div class=\"commentbox L" + labelUniqueId + "\">" +
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
recolorLabelInstances = function(label_name){
	$(".fg-button").each(function(intIndex, objValue){
		if ($(this).text() == label_name){
			$(this).removeClass("ui-button-private")
			$(this).addClass("ui-button-shared");
			$(this).next().removeClass("ui-button-private")
			$(this).next().addClass("ui-button-shared");		
		}
	});
}

deleteLabelInstances = function(label_name){
	$(".fg-button").each(function(intIndex, objValue){
		if ($(this).text() == label_name){
			$(this).next().remove();
			$(this).remove();
		}
	});
}

renameLabelInstances = function(old_label_name, new_label_name){
	$(".fg-button").each(function(intIndex, objValue){
		if ($(this).text() == old_label_name){
			$(this).button('option', 'label', new_label_name);

		}
	});
}

/* display a label that was just added to an article */
function displayLabelOnArticleByKey(labelArticleKey,uniqueLabelObject){
	
	label_name = uniqueLabelObject.label_name
	
	x= $("#"+labelArticleKey)
	
	str = "<div style=\"display: inline\" class=\"labelButton L" + labelUniqueId + " " + labelArticleKey + "\">" +
			"<div style=\"display: inline\">" +
				"<button id=\"labelname\" class=\"fg-button L" + labelUniqueId +" ui-button ui-button-label ui-widget ui-state-default ui-corner-all \" title=\"Click to add a Comment\" input type=\"submit\">" + label_name + "</button>" +
				"<button id=\"closelabel\" class=\"fg-button-x L" + labelUniqueId + " ui-button ui-button-label-x ui-widget ui-state-default ui-corner-all\" input type=\"submit\">Delete this label</button>" +
			"</div>" +
		"</div>"
	$(x).prepend(str)
	
	if (uniqueLabelObject.is_shared){
		$(".fg-button.L"+ labelUniqueId +"\"").addClass("ui-button-shared");
		$(".fg-button-x.L"+ labelUniqueId +"\"").addClass("ui-button-shared");
	}
	else{
		$(".fg-button.L"+ labelUniqueId +"\"").addClass("ui-button-private");
		$(".fg-button-x.L"+ labelUniqueId +"\"").addClass("ui-button-private");
	}
	
	str = "<span class=\"comment_name L" + labelUniqueId + "\"></span>" +
			"<div class=\"commentbox L" + labelUniqueId + "\">" +
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


function labelExistsInArticle(label_name, labelArticleKey){
	var flag = false
	$.each(parent.labels, function(intIndex,objValue){
		if (objValue.label_name == label_name && objValue.article_key == labelArticleKey){
			flag = true
		};
	});
	return flag
}


/* This function is called when a user inputs a new (unknown) label name */
function addNewLabel(label_name, labelArticleKey){
	if(label_name.length < 1) return false
	/* add label to labels */
	
	/* create uniqueLabel object */
	var uniqueLabelObject = {
	   		label_name: label_name,
	   		number: 1,
	   		is_shared: false			                
		   };
	
	
	
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
		data: articleJSON,
		success: function(data, textStatus){
			if (data == -7){
				alert("Error occured while uploading existing label to DB")
			}
			else{
				addLabelToGlobalLabels(uniqueLabelObject, labelArticleKey);
				parent.uniqueLabels.push(uniqueLabelObject);
				
				/* show label in HTML */
				
				displayLabelOnArticleByKey(labelArticleKey,uniqueLabelObject)
				
				/* display new label tag on the left side bar */
				parent.addLabel(uniqueLabelObject.label_name, 1)
			}
		}
	});	
			
	
}


	
/* This function is called when auto complete matches a result */
function existingLabelSelected(uniqueLabelObject, labelArticleKey){
	label_name = uniqueLabelObject.label_name

	if (!labelExistsInArticle(label_name, labelArticleKey)){
		
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
			data: articleJSON,
			success: function(data, textStatus){
				if (data == -7){
					alert("Error occured while uploading existing label to DB")
				}
				else{
					/* add label to labels */
					addLabelToGlobalLabels(uniqueLabelObject, labelArticleKey)
					/* update number of labels in uniqueLabels */
					
					incrementUniqueLabelCount(label_name);
					
					/* show label in HTML */
					
					displayLabelOnArticleByKey(labelArticleKey,uniqueLabelObject)
				}
			}
		});	
		
		
	}
}

function incrementUniqueLabelCount(label_name){
	$.each(parent.uniqueLabels, function(intIndex,objValue){
		if (objValue.label_name == label_name){
			objValue.number += 1;
			if (objValue.is_shared)
				parent.inc_shared(label_name);
			else
				parent.inc(label_name);
			return false
		}
	});
}

function decrementUniqueLabelCount(label_name){
	$.each(parent.uniqueLabels, function(intIndex,objValue){
		if (objValue.label_name == label_name){
			objValue.number -= 1;
			if (objValue.is_shared){
				parent.dec_shared(label_name);
			}
			else
				parent.dec(label_name);
			if (objValue.number == 0){
				/* delete the label button from the left sidebar */
				parent.deleteTag(label_name)
				/* remove the uniqueLabelObject from the uniqueLabel list */
				parent.uniqueLabels = $.grep(parent.uniqueLabels, function(val){return val.number!=0;});
			}
			return false
		}
	});
}	



function removeLabelFromGlobalLabels(label_name, article_key){
	parent.labels = $.grep(parent.labels, function(label , i) { 
		return (label.label_name != label_name || label.article_key != article_key);
	});
}


/* save the new/existing article label locally */
function addLabelToGlobalLabels(uniqueLabelObject, labelArticleKey){
	var labelObject = {
	   		comment: "",
	   		is_shared: uniqueLabelObject.is_shared,
	   		users_list: [],
	   		serialized_article: "",
	   		label_name: uniqueLabelObject.label_name,
	   		article_key: labelArticleKey			                
		   };
	parent.labels.push(labelObject)
}

/* called when a user presses the X button on a label */
function removeLabelFromArticle(label_name, article_key){
	
	labelToRemoveFromDB = {
			   label_name:label_name,
			   article_key:article_key
				}
	$.ajax({
		type: 'POST',
		url: "/RemoveLabelDB",
		data: labelToRemoveFromDB,
		success: function(data, textStatus){
			if (data == false){
				alert("Error occured while deleting label from DB")
			}
			else{
				/* decrement label occurence in uniqueLabels (and remove it if reached 0) */
				decrementUniqueLabelCount(label_name);
				/* remove from global labels list */
				removeLabelFromGlobalLabels(label_name, article_key);
			}
		}
	});
}

function getUniqueLabel(label_name){
	uniqueLabelArray = $.grep(parent.uniqueLabels, function(val) { return val.label_name == label_name; });
	if (uniqueLabelArray.length){
		return uniqueLabelArray[0];
	}
	else{
		return -1;
	}
}

function findLabelIndexInGlobalLabelsByKeyAndName(article_key, label_name){
	index = -1
	$.each(parent.labels, function(intIndex,objValue){
		if (objValue.label_name == label_name && objValue.article_key == article_key){
			index = intIndex
		}
	});
	return index
}

function saveComment(commentContent, article_key, label_name){


	
	commentToDB = {
				   comment_content:commentContent,
				   label_name:label_name,
				   article_key:article_key
				}
	$.ajax({
		  type: 'POST',
		  url: "/UpdateArticleLabelDB",
		  data: commentToDB,
		  success: function(data, textStatus){
			if (data == -7){
				alert("Error occured while uploading existing label to DB")
			}
			else{
				labelIndex = findLabelIndexInGlobalLabelsByKeyAndName(article_key, label_name)
				parent.labels[labelIndex].comment = commentContent
			}
		}
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
	
	user = parent.getCurrentUser()
	$(".labelBox").livequery(function(){$(this).alphanumeric({allow:"_ "})})
	$(".labelBox").hide()
	

	$(".commentcontent").live("click", function(){
        
        classList = $(this).parent().attr('class').split(' ');
        labelKey = classList[1]
        if (parent.userAgent =="chrome"){
			$(".commentcontent.#"+labelKey).height(85)
			$(".commentcontent.#"+labelKey).width(500)
        }
        else{
	        $(this).focus()
	        $(".commentcontent.#"+labelKey).animate({"height": "85px", "width": "500px"}, "fast" );
	        $(".button_block.#"+labelKey).slideDown("fast");
        }
        return false;
    });

    $("#close").livequery(function(){
    	$(this).button();
    	$(this).click(function(){
	        classList = $(this).parent().parent().attr('class').split(' ');
	        labelKey = classList[1]
	        $(".commentcontent.#"+labelKey).animate({"height": "30px", "width": "200px"}, "fast" );
	        $(".button_block.#"+labelKey).slideUp("fast");
	        $(".commentcontent.#"+labelKey).blur()
	        $(".commentbox."+labelKey).hide()
	        $(".comment_name."+labelKey).hide()
	        iFrameHeightDecrement(100)
	        return false;
    	});
    });
	

    $("#save").livequery(function(){
    	$(this).button();
    	$(this).click(function(){
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

    });
    $(".fg-button").live("mouseover",function(){ 
    	$(this).tooltip();
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
			$(".comment_name."+labelKey).html("<br/><b>"+ label_name + "</b>    comment:")
			$(".comment_name."+labelKey).show()
			//$(".button_block.#"+labelKey).position().right(100)
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
			$(".comment_name."+labelKey).hide()
		/* remove tag from HTML */
			$(this).prev().remove();
			$(this).remove();
		});
	});
	
	$(".labelButton").livequery(function(){
		$(this).buttonset();
	});
	$(".addFollowButton").livequery(function(){
		$(this).button();
		if (user == ""){
			$(this).click(function(e){
				e.preventDefault()
				$('#popupText').html("This option is only available when logged in. <br/>");
				$('#popupText').dialog({ width: 400 , position: 'top' , buttons: { "Ok": function() { $(this).dialog("close"); } }});
			})
		}
	});
	$(".addLabel").livequery(function(){
		$(this).button();
		
		if (user == ""){
			$(this).click(function(e){
				e.preventDefault()
				$('#popupText').html("This option is only available when logged in. <br/>");
				$('#popupText').dialog({ width: 400 , position: 'top' , buttons: { "Ok": function() { $(this).dialog("close"); } }});
			})
		}else{		
		$(this).click(function() {	
			var classList =$(this).parent().parent().closest("div").attr('class').split(' ');
			var articleClassID = classList[1]
			var labelArticleKey = ($(this).parent().parent().closest("div").attr("id"));
			$(".labelBox").val("")
		    selectedLabelBox = $(this).parent().next(".labelBox")
		    selectedLabelBox.slideToggle(200)
		    uniqueLabelsNames.length = 0;
			$.each(parent.uniqueLabels, function(intIndex, objValue){
				uniqueLabelsNames.push(objValue.label_name)
			})
	    	var ac = selectedLabelBox.autocomplete({
	    		minLength: 1,
	            select: function(event, ui){ // Callback function, triggered if one of the suggested options is selected,
	    			uniqueLabelTest = getUniqueLabel(ui.item.label)
	    			existingLabelSelected(uniqueLabelTest, labelArticleKey);
	    			$(this).val("")
	    			$(this).hide()
	    			return false    			
	    			},
	
	    		open: function() {
	    			$(this).removeClass("ui-corner-all").addClass("ui-corner-top");
	    		},
	   			//close the drop down
	   			close: function() {
	   				$(this).removeClass("ui-corner-top").addClass("ui-corner-all");
	   			},
	
	
	    		delay: 0,
	    		source: uniqueLabelsNames
	
	        });
		    selectedLabelBox.focus();
		    ac.enable();
	    /* handle "user pressed Enter key" event */
		    $('.labelBox').keyup(function(e) {
		    	if(e.keyCode == 13) {
		    		label_name = $(this).val();
		    		/* recognize which article is being labeled */
		    		labelArticleKey = ($(this).parent().closest("div").attr("id"));
		    		$(this).val("")
	    			$(this).hide()
	    			uniqueLabelTest = getUniqueLabel(label_name)
	    			/* if this is a new label */
	    			if (uniqueLabelTest == -1){
	    				addNewLabel(label_name, labelArticleKey)
	    			}
		    		else
		    			existingLabelSelected(uniqueLabelTest, labelArticleKey);			
		    		}
		    	});
			})
		};//end of else	
		});
});



