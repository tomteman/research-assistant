from ArticleData import ArticleData
from getHTML import getHTML
from bibtexParser import parser
from ArticleURLandTitle import ArticleURLandTitle
#import parser



# TODO: Handle "Did You Mean?" Scenario

class HTMLparser:
    def __init__(self, url, html):
        self.url = url
        self.html = html
        self.results = {}

    def get_url(self):
        return self.url


    def get_html(self):
        return self.html


    def get_results(self):
        return self.results


    def set_url(self, value):
        self.url = value


    def set_html(self, value):
        self.html = value


    def set_results(self, value):
        self.results = value


    def del_url(self):
        del self.url


    def del_html(self):
        del self.html


    def del_results(self):
        del self.results

        
    # RegularQuery = TRUE -> used or user searches. get results without BibTexData, with HTMLdata    
    # RegularQuery = FALSE -> used for follow searches. get results with BibTexData, with HTMLdata
    # BibTexDataFlag = TRUE  -> get results with BibTex Data
    # BibTexDataFlag = FALSE -> get results without BibTex Data
    # Default - TRUE (with BibTex Data)
    
    def parseHTML(self):           
        
        results = []
        # remove everything prior to the results
        position = self.html.find(">Results")
        sandboxHTML = self.html[position:]
        position = 0
        
        articleCounter = 0
        
        # TODO: look for DID YOU MEAN?
        
        # didYouMean = sandboxHTML.find("Did you mean:")
        
        
        # start parsing the results
        
        # end of results indicated by "next" link
        while (not isEndOfPage(sandboxHTML, position)):
            
            # create new Article object
            
            newArticle = ArticleData()
            articleCounter += 1
            
            
            # end of article indicated by abstract tag (class=gs_a)
            while (not isEndOfArticleLinks(sandboxHTML, position)):
                # find the next article title (maybe with URL)
                temp = findNextLinkOrCitation(sandboxHTML, position)
                newArticle.add_item_to_HTML_urlList(parseURLandTitleSurroundingTag(sandboxHTML, temp[1], temp[0]))
                
                # remove all HTML up to last indicator
                sandboxHTML = sandboxHTML[temp[1]+5:]
                # set position to beginning of modified sandboxHTML
                position = 0
                
            # finished getting titles and URLS. Now retrieve HTML fields - author+year+pub and abstract
            
            position = parseHTMLdata(sandboxHTML, position, newArticle)
            sandboxHTML = sandboxHTML[position:]
            position = 0
            
            position = getGoogleScholarLinks(sandboxHTML, position, newArticle)
            sandboxHTML = sandboxHTML[position:]
            position = 0
            
            results.append(newArticle)
            
        
        self.set_results(results)
            
            
            
    
# this function parses the Google Scholar links (citations, related items, all versions, bibtex), and returns
# the position of the next article link    
def getGoogleScholarLinks(sandboxHTML, position, newArticle):
    stillParsing = 1
    lastPosition = 0
    
    position = sandboxHTML.find("/scholar", position)
    
    # stop parsing after parsing the BibTex link (always last, always there)
    while(stillParsing):
    
        # find next link
        
        
        # get articleCitation URL
        if ("/scholar?cites" == sandboxHTML[position:position+len("/scholar?cites")]):
            tmp = sandboxHTML.find("\"",position+1)
            articleCITATIONS = sandboxHTML[position:tmp]
            CitationsID = getCitationsIDfromURL(articleCITATIONS)
            newArticle.set_citations_ID(CitationsID)
            newArticle.set_citations_url(createCitationsURL(CitationsID))
            position = tmp
            sandboxHTML = sandboxHTML[position:]
            lastPosition += position
            position = sandboxHTML.find("/scholar", 0)
            
        # get articleRelatedItems URL    
        elif ("/scholar?q=related" == sandboxHTML[position:position+len("/scholar?q=related")]):
            tmp = sandboxHTML.find("\"",position+1)
            articleRELATED = sandboxHTML[position:tmp]
            RelatedArticlesID = getCitationsIDfromURL(articleRELATED)
            newArticle.set_related_articls_ID(RelatedArticlesID)
            newArticle.set_related_articles_url(createRelatedArticlesURL(RelatedArticlesID))
            position = tmp
            sandboxHTML = sandboxHTML[position:]
            lastPosition += position
            position = sandboxHTML.find("/scholar", 0)
            
        elif ("/scholar?q=cache" == sandboxHTML[position:position+len("/scholar?q=cache")]):
            URLend = sandboxHTML.find("\"",position+1)
            URLstart = sandboxHTML.rfind("\"", 0, URLend)
            articleCACHE = sandboxHTML[URLstart+1:URLend]
            CacheID = getCacheIDfromURL(articleCACHE)
            newArticle.set_cache_ID(CacheID)
            newArticle.set_cache_url(articleCACHE)
            position = URLend
            sandboxHTML = sandboxHTML[position:]
            lastPosition += position
            position = sandboxHTML.find("/scholar", 0)


        # get allVersions URL    
        elif ("/scholar?cluster" == sandboxHTML[position:position+len("/scholar?cluster")]):
            tmp = sandboxHTML.find("\"",position+1)
            articleVERSIONS = sandboxHTML[position:tmp]
            AllVersionsID = getAllVersionsIDfromURL(articleVERSIONS)
            newArticle.set_all_versions_ID(AllVersionsID)
            newArticle.set_all_versions_url(createAllVersionsURL(AllVersionsID))
            position = tmp
            sandboxHTML = sandboxHTML[position:]
            lastPosition += position
            position = sandboxHTML.find("/scholar", 0)

        # get articleBibtex URL
        elif ("/scholar.bib" == sandboxHTML[position:position+len("/scholar.bib")]):
            tmp = sandboxHTML.find("\"",position+1)
            articleBIBTEX = sandboxHTML[position:tmp]    
            bibtexID = getBibTexIDfromURL(articleBIBTEX)
            newArticle.set_key(bibtexID)
            newArticle.set_bib_tex_url(createBibTexURL(bibtexID))
            
            position = tmp 
            lastPosition += position
            stillParsing = 0
            
           
            # finished getting all the data for this article entry.
    
    return lastPosition
            

# checks if there are additional articles to parse
def isEndOfPage(sandboxHTML, position): 
    
    # check if indication for end of all results on page appears before indication for next article
    if (sandboxHTML.find("/scholar.bib", position) == -1):  
        return True
    else:
        return False

# checks if there are no more links for this article
def isEndOfArticleLinks(sandboxHTML, position):
    # check if indication for end of results for current article appears before indication for next article/citation:
    googleLinks = sandboxHTML.find("class=gs_fl", position)
    if (
        
        ((sandboxHTML.rfind("class=yC", 0, googleLinks) == -1) and (sandboxHTML.rfind("class=gs_ctu", 0, googleLinks) == -1)) 
#    # check if the beginning of HTML data appears before another article title+link (regular scenario)
#        ((((sandboxHTML.find("class=gs_a", position)) < sandboxHTML.find("class=yC", position))
#          and (sandboxHTML.find("class=yC", position) != -1))
#    # or if the beginning of HTML data appears before a [CITATION] without a link        
#        or (((sandboxHTML.find("class=gs_a", position)) < sandboxHTML.find("class=gs_ctu", position))
#        and (sandboxHTML.find("class=gs_ctu", position) != -1)))
    
    # in case this is one article before the last one, and the last one is a citation:
    # there will be no more "class=yC"
    or (isOneArticleBeforeLast(sandboxHTML, position) and (sandboxHTML.find("class=yC", position) == -1))

    
    # in case this is the last article
    or ((isLastArticle(sandboxHTML, position)) and
        # and it has a link (also make sure it's not a citation)
        ((((sandboxHTML.find("class=gs_a", position) < sandboxHTML.find("class=yC", position))
          and sandboxHTML.find("class=yC", position) != -1)
        # or it's the last citation
        or ((sandboxHTML.find("class=yC", position) == -1) and (sandboxHTML.find("[CITATION]", position) == -1)))))
    ):      
        return True
    else:
        return False

def isOneArticleBeforeLast(sandboxHTML, position):
    occurence1 = sandboxHTML.find("/scholar.bib", position)
    occurence2 = sandboxHTML.find("/scholar.bib", occurence1+len("/scholar.bib"))
    occurence3 = sandboxHTML.find("/scholar.bib", occurence2+len("/scholar.bib"))
    
    # only 2 more bibtex links
    if ((occurence1 > 0) and (occurence2 > 0) and (occurence3 == -1)):
        return True
    else:
        return False 

# checks if the next article is the last one
def isLastArticle(sandboxHTML, position):
    occurence1 = sandboxHTML.find("/scholar.bib", position)
    occurence2 = sandboxHTML.find("/scholar.bib", occurence1+len("/scholar.bib"))
    
    # at least 2 more bibtex links
    if ((occurence1 > 0) and (occurence2 > 0)):
        return False
    else:
        return True 
        
# finds the next article title. 
# If it has a link as well, returns a tuple
# with the position of "class=yC" and the flag False (not a citation).
# if it is only a citation (no link), returns a tuple
# with the position of "[CITATION]" and the flag True (is a citation).
# input: HTML to look through and starting position to start looking from

def findNextLinkOrCitation(sandboxHTML, position):
    withLink = sandboxHTML.find("class=yC", position)
    withoutLink = sandboxHTML.find("gs_ctu", position)
    
    if ((withLink == -1) and (withoutLink == -1)):
        print "ERROR - supposed to find another article (isEndOfPage == False), but can't"
    
    if (withLink == -1):
        return (True, withoutLink)
    
    if (withoutLink == -1):
        return (False, withLink)
    
    if (withLink < withoutLink):
        return (False, withLink)
    
    if (withoutLink < withLink):
        return (True, withoutLink)
    

# updates an ArticleData object with two fields from the HTML: HTML_author_year_pub and HTML_abstract
# return value: position at the end of the abstract

def parseHTMLdata(sandboxHTML, position, newArticle):
    authorStart = sandboxHTML.find("class=gs_a>", position)
    authorEnd = sandboxHTML.find("</span>", authorStart)
    newArticle.set_HTML_author_year_pub(sandboxHTML[authorStart+len("class=gs_a>"):authorEnd])
    abstractEnd = sandboxHTML.find("<span", authorEnd)
    newArticle.set_HTML_abstract(sandboxHTML[authorEnd+len("</span>"):abstractEnd])
    
    return abstractEnd

# given an HTML to look through, the starting position and a flag
# indicating whether this is a CITATION or URL (in addition to a title),
# this function will return an ArticleURLandTitle object    
    
def parseURLandTitleSurroundingTag(sandboxHTML, position, isCitation):
    results = ArticleURLandTitle()
    
    # if this tag has the title name in front of it, and the URL behind it
    if (not isCitation):
        # parse title
        titleStart = (sandboxHTML.find(">",position) + 1)
        titleEnd = sandboxHTML.find("</a>", titleStart)
        results.set_article_title(sandboxHTML[titleStart:titleEnd])
        #parse URL
        
        urlStart = sandboxHTML.rfind("<a href=", 0, position)
        urlEnd = sandboxHTML.find("class=yC", urlStart)
        results.set_article_url(sandboxHTML[urlStart+len("<a href=")+1:urlEnd-2])
        
    
    # if this tag only has a title name in front of it
    if (isCitation):
        # check if this citation has a link:
        hasLink = sandboxHTML.rfind("class=gs_ctc", position-2-len("class=gs_ctc"), position)
        # if this citation is linked - treat as regular article title + url
        if (hasLink > 0):
            # find the next "class=yC" instance
            temp = findNextLinkOrCitation(sandboxHTML, position+1)
            # call this function, which this time will receive NOT isCitation
            return parseURLandTitleSurroundingTag(sandboxHTML, temp[0], temp[1])
        
        # we didn't find an indication that this citation has a link
        if (hasLink == -1):
            titleStart = sandboxHTML.find("</span>", position)
            titleEnd = sandboxHTML.find("</h3>", titleStart)
            results.set_article_title(sandboxHTML[titleStart+len("</span> "):titleEnd])
            results.set_article_url("")
            
            results.set_has_link(False) 
    
    return results     
            
def getBibTexIDfromURL(url):
    start = url.find(":")
    finish = url.find(":", start+1)
    return url[start+1:finish]

def getCitationsIDfromURL(url):
    start = url.find("cites=")
    finish = url.find("&", start)
    return url[start+len("cites="):finish]

def getRelatedArticlesIDfromURL(url):
    start = url.find("related:")
    finish = url.find(":", start+len("related:")+1)
    return url[start+len("related:")+1:finish]

def getAllVersionsIDfromURL(url):
    start = url.find("cluster=")
    finish = url.find("&", start)
    return url[start+len("cluster="):finish]

def getCacheIDfromURL(url):
    start = url.find("cache:")
    finish = url.find(":", start+len("cache:")+1)
    return url[start+len("cache:")+1:finish]


def createBibTexURL(bibtexID):
    return "http://scholar.google.com/scholar.bib?q=info:" + str(bibtexID) + ":scholar.google.com/&output=citation&hl=en&as_sdt=2000&ct=citation&cd=0"

def createCitationsURL(CitationsID):
    return "http://scholar.google.com/scholar?cites=" + str(CitationsID) + "&hl=en&num=10&as_sdt=2000"

def createRelatedArticlesURL(RelatedArticlesID):
    return "http://scholar.google.com/scholar?q=related:" + str(RelatedArticlesID) + ":scholar.google.com/&hl=en&num=10&as_sdt=2000"

def createAllVersionsURL(AllVersionsID):
    return "http://scholar.google.com/scholar?cluster=" + str(AllVersionsID) + "&hl=en&num=10&as_sdt=2000"    

def parseBibTexItems(bibtexID):
    # get the BibTex HTML
    bibtexHTML = getHTML(createBibTexURL(bibtexID))
    bibtexHTML.getHTMLfromURL()
    
    HTML = bibtexHTML.get_html()
    
    # parse the BibTex HTML into a dictionary and return it
    return (parser.parse_string(HTML, 0))

# BibTexDataFlag = TRUE  -> get results with BibTex Data
# BibTexDataFlag = FALSE -> get results without BibTex Data
# Default - TRUE (with BibTex Data)    
    
def getResultsFromURL(url):
    # first we fetch the HTML from Google Scholar
    newHTML = getHTML(url)
    newHTML.getHTMLfromURL()
    
    # parse the results
    newHTMLParser = HTMLparser(url,newHTML.get_html())
    newHTMLParser.parseHTML()
    return newHTMLParser.get_results()
    
    
             
    
        
        
        
        
        
        
        
        