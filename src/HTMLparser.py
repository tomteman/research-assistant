
from ArticleData import Article
from getHTML import getHTML
from bibtexParser import parser
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

        
        
    # BibTexDataFlag = TRUE  -> get results with BibTex Data
    # BibTexDataFlag = FALSE -> get results without BibTex Data
    # Default - TRUE (with BibTex Data)
    
    def parseHTML(self, BibTexDataFlag=1):           
        # remove everything prior to the results
        tmp = self.html.find(">Results")
        sandboxHTML = self.html[tmp:]
        justACitation = 0
        isNewArticle = 1
        notEndOfResults = 1
        articleCounter = 0
        while notEndOfResults:
            # find the next url
            thisURL = sandboxHTML.find("<a href=")
            if isNewArticle == 1:
                
                articleCounter = articleCounter + 1                
                
                newArticle = Article()
                            
                # parse the article URLs
                
                stillParsingArticleURLs = 1
                          
                while stillParsingArticleURLs:
                
                    # check if the next link is of an articleURL
                    urlOccurenceStart = sandboxHTML.find("http",thisURL)
                    urlOccurenceEnd = sandboxHTML.find("\"",(urlOccurenceStart+1))
                    nextURL = sandboxHTML.find("<a href=",(thisURL+1))    
    
                    # check if this is indeed an Article URL
                    if (urlOccurenceStart<nextURL) and (urlOccurenceStart>thisURL):
                        # get the URL
                        articleURL = sandboxHTML[urlOccurenceStart:urlOccurenceEnd]
                        newArticle.addURLto_urlList(articleURL)
                        # cut the HTML leading to the next link
                        sandboxHTML = sandboxHTML[nextURL:]
                        isNewArticle = 0
                    
                    #check if this just a citations
                    elif ("/scholar.bib" == sandboxHTML[(thisURL+9):(thisURL+9+len("/scholar.bib"))]):
                        isNewArticle = 0
                        stillParsingArticleURLs = 0
                        justACitation = 1 
                    
                    # no more article URLs
                    else:
                        isNewArticle = 0
                        stillParsingArticleURLs = 0 
                    
            # we are parsing other info about the article
            else:
                # get articleCitation URL
                if ("/scholar?cites" == sandboxHTML[(thisURL+9):(thisURL+9+len("/scholar?cites"))]):
                    tmp = sandboxHTML.find("\"",thisURL+10)
                    articleCITATIONS = sandboxHTML[thisURL+9:(tmp)]
                    newArticle.set_citations_url(articleCITATIONS)
                # get articleRelatedItems URL    
                elif ("/scholar?q=related" == sandboxHTML[(thisURL+9):(thisURL+9+len("/scholar?q=related"))]):
                    tmp = sandboxHTML.find("\"",thisURL+10)
                    articleRELATED = sandboxHTML[thisURL+9:(tmp)]
                    newArticle.set_related_articles_url(articleRELATED)
                    
                # get allVersions URL    
                elif ("/scholar?cluster" == sandboxHTML[(thisURL+9):(thisURL+9+len("/scholar?cluster"))]):
                    tmp = sandboxHTML.find("\"",thisURL+10)
                    articleVERSIONS = sandboxHTML[thisURL+9:(tmp)]
                    newArticle.set_all_versions_url(articleVERSIONS)
                    
                # get articleBibtex URL
                elif ("/scholar.bib" == sandboxHTML[(thisURL+9):(thisURL+9+len("/scholar.bib"))]):
                    if (justACitation):
                        justACitation = 0
                    tmp = sandboxHTML.find("\"",thisURL+10)
                    articleBIBTEX = sandboxHTML[thisURL+9:(tmp)]
                    
                    bibtexID = getIDfromURL(articleBIBTEX)

                    # save the BibTex ID to the new article entry
                    newArticle.set_key(bibtexID)
                    
                    # save the BibTex URL to the new article entry
                    newArticle.set_bib_tex_url(createBibTexURL(bibtexID))
                   
                    # fetch the BibTex Data
                    if BibTexDataFlag:
                        newArticle.set_bib_tex_dict(parseBibTexItems(getIDfromURL(articleBIBTEX)))
                    
                    # finished getting all the data for this article entry.
                    # Save it to the results, using its BibTex ID as the 
                    # dictionary KEY and the article info as the VALUE
                    self.results[newArticle.get_key()] = newArticle
                    
                    isNewArticle = 1
                    #print("-=FINISHED PARSING ARTICLE NUMBER %d=-" % articleCounter)
                    
                
                # find next link and remove all html leading up to it
                thisURL = sandboxHTML.find("<a href=", (thisURL+1))            
                sandboxHTML = sandboxHTML[thisURL:]
                
                # check if we reached the end of the results
                if ((sandboxHTML.find("/scholar?start", len("<a href="))) < sandboxHTML.find("<a href=")):  
                    notEndOfResults = 0
    
    url = property(get_url, set_url, del_url, "url's docstring")
    html = property(get_html, set_html, del_html, "html's docstring")
    results = property(get_results, set_results, del_results, "results's docstring")
             
            
def getIDfromURL(url):
    start = url.find(":")
    finish = url.find(":", start+1)
    return url[start+1:finish]

def createBibTexURL(bibtexID):
    return "http://scholar.google.com/scholar.bib?q=info:" + str(bibtexID) + ":scholar.google.com/&output=citation&hl=en&as_sdt=2000&ct=citation&cd=0"
    

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
    
def getResultsFromURL(url, BibTexDataFlag=1):
    # first we fetch the HTML from Google Scholar
    newHTML = getHTML(url)
    newHTML.getHTMLfromURL()
    
    # parse the results
    newHTMLParser = HTMLparser(url,newHTML.get_html())
    newHTMLParser.parseHTML(BibTexDataFlag)
    return newHTMLParser.get_results()
    
    
             
    
        
        
        
        
        
        
        
        