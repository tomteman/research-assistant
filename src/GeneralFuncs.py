#!/usr/bin/env python

import getHTML
import HTMLparser

##########
# GENERAL FUNCTIONS (NOT USING OUR SPECIAL DATA TYPES)
##########

## TOM really needs to change this thing
# 
def url2ArticleDict(url):
    # get the HTML from the URL (first 100 results)
    newHTML = getHTML.getHTML(url)
    newHTML.getHTMLfromURL()
    
    # parse the results
    newHTMLParser = HTMLparser.HTMLparser(url,newHTML.get_html())
    newHTMLParser.parseHTML()
    #print newHTMLParser.results
    return newHTMLParser.results
    
# The old function. Now I'm using compareKeysLists   
def compareDicts(oldDict, newDict):
    
    oldKeys = oldDict.keys()
    newKeys = newDict.keys()
    difference = set(newKeys).difference(set(oldKeys))
    if len(difference) == 0:
        return {}
    
    diffDict = {}
    # create the new dictionary containing only new articles
    for key in difference:
        diffDict[key] = newDict[key]
    print "compareDicts: found difference. Done Comparing.\n"
    return diffDict

# Gets two lists or articles Keys, and returns a list with the differences 
def compareKeysLists(oldKeys, newKeys):
    return list(set(newKeys).difference(set(oldKeys)))
    
## TODO: make this a real mail sender
def sendEmail(emailaddr, message):
    print "Sending mail to address "+ emailaddr + " :\n"
    print message

# This is a temporal dummy instead of Tom's parser
# returns dictionary of articles:
#   {BibteXKey : Article, BibteXKey : Article,...}
#   or None when unsuccessful

def CompareDictsofArticles(oldDict, newDict):
    oldKeys = oldDict.keys()
    newKeys = newDict.keys()
    difference = set(newKeys).difference(set(oldKeys))
    if len(difference) == 0:
        return {}
    
    diffDict = {}
    # create the new dictionary containing only new articles
    for i in difference:
        diffDict[i] = newDict[i]
   
    print "CompareDictsofArticles: found difference. Done Comparing."
    return diffDict

def PrintArticlesDict(dictionary):
    if len(dictionary) == 0:
        print "Sorry. Empty Dictionary\n"
        return
    for article in dictionary.values():
        print str(article) + "\n"
    

#def parseUrl(url):
#    
#    article1 = Article("1", 
#            "Title1", 
#            "http://journals.cambridge.org/abstract_S0021859600063048", 
#            "/scholar?cites=8649893196452540066&amp;hl=en&amp;num=100&amp;as_sdt=2000&amp;as_ylo=2009", 
#            "/scholar?q=related:oi6fdwiYCngJ:scholar.google.com/&amp;hl=en&amp;num=100&amp;as_sdt=2000&amp;as_ylo=2009")
#    article2 = Article("2", 
#            "Title2",
#            "http://journals.cambridge.org/abstract_S0021859600063048")
#    article3 = Article("3", 
#            "Title3",
#            "http://nar.oxfordjournals.org/cgi/content/abstract/gkp985")
#    
#    my_dict = {article1.key: article1, article2.key:  article2}
#    if (url == "2"):
#        print "new dict will be 3 articles\n"
#        my_dict = {article1.key: article1, article2.key:  article2, article3.key:  article3}
#        
#    return my_dict

# This is a temporal dummy instead of Dina's function
# returns the url, or None if unsuccessful.
def serachParamsToUrl(search_params):
    return "http://scholar.google.co.il/scholar?q=%22behavioral+economics%22&hl=en&cites=5723524840551782037"
