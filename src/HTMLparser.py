from ArticleData import ArticleData
from getHTML import getHTML
from bibtexParser import parser
from ArticleURLandTitle import ArticleURLandTitle
from time import sleep
from urllib import quote_plus
import re



# TODO: Handle "Did You Mean?" Scenario

class HTMLparser:
    def __init__(self, url, html):
        self.url = url
        self.html = html
        self.results = []
        self.noResultsFlag = False
        self.refinedSearchNoResultsFlag = False  # flag indicating if refined search (search within citation) yielded no results
        self.numOfResults = 0
        self.didYouMeanFlag = False
        self.didYouMeanHTML = ""
        self.didYouMeanURL = ""
        self.didYouMeanKeywords = ""

    def get_url(self):
        return self.url


    def get_html(self):
        return self.html


    def get_results(self):
        return self.results
    
    def isNoResultsFlag(self):
        return self.noResultsFlag
    
    def isRefinedSearchNoResultsFlag(self):
        return self.refinedSearchNoResultsFlag

    def get_numOfResults(self):
        return self.numOfResults
    
    def isDidYouMeanFlag(self):
        return self.didYouMeanFlag
    
    def get_didYouMeanHTML(self):
        return self.didYouMeanHTML
    
    def get_didYouMeanURL(self):
        return self.didYouMeanURL
    
    def get_didYouMeanKeywords(self):
        return self.didYouMeanKeywords
    
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
        # check if there are no results at all
        if (position < 0):
            self.noResultsFlag = True
            sandboxHTML = self.html[0:]
        else:
            sandboxHTML = self.html[position:]
            position = 0
        
            resultsPosition = sandboxHTML.find("of", position)
            numOfResultsStart = sandboxHTML.find("<b>", resultsPosition) + 3
            numOfResultsEnd = sandboxHTML.find("</b>", numOfResultsStart)
            self.numOfResults = sandboxHTML[numOfResultsStart:numOfResultsEnd]

        
        # handle "Did you mean:" scenario
        didYouMeanPosition = sandboxHTML.find("Did you mean", 0)
        if (didYouMeanPosition > 0):
            self.didYouMeanFlag = True
            didYouMeanURLstart = sandboxHTML.find("<a href", didYouMeanPosition)+len("<a href=")+1
            didYouMeanURLend = sandboxHTML.find("\">", didYouMeanURLstart)
            self.didYouMeanURL = "http://scholar.google.co.il" + sandboxHTML[didYouMeanURLstart:didYouMeanURLend]
            
            didYouMeanHTMLstart = didYouMeanURLend + 2
            didYouMeanHTMLend = sandboxHTML.find("</a>", didYouMeanHTMLstart)
            self.didYouMeanHTML = sandboxHTML[didYouMeanHTMLstart:didYouMeanHTMLend]
            
            self.didYouMeanKeywords = quote_plus(remove_html_tags(self.didYouMeanHTML),"")
        
        
        if (self.noResultsFlag == False):
            sandboxHTML = sandboxHTML[numOfResultsEnd:]

        
        if (self.noResultsFlag == True):
            # check if this was a refined search (search within citations)
            position = self.html.find("Sorry, we didn't find any articles that cite", 0)
            if (position>0):
                self.refinedSearchNoResultsFlag = True
            self.results = results
            return 0
        
        
        articleCounter = 0
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
            
            articleTitle = newArticle.HTML_urlList[0].articleTitle
            newArticle.articleTitle = articleTitle
            
            articleTitleQuoted = quote_plus(articleTitle,"")
            newArticle.articleTitleQuoted = articleTitleQuoted 
            
            articleURL = newArticle.HTML_urlList[0].articleURL
            newArticle.articleURL = articleURL
            
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
            endOfLink = sandboxHTML.find("\"",position+1)
            articleCITATIONS = sandboxHTML[position:endOfLink]
            CitationsID = getCitationsIDfromURL(articleCITATIONS)
            newArticle.set_citations_ID(CitationsID)
            newArticle.set_citations_url(createCitationsURL(CitationsID))
            endOfNum = sandboxHTML.find("<", endOfLink)
            numOfCitations = sandboxHTML[endOfLink+2+len("Cited by "):endOfNum]
            newArticle.set_citations_NUM(numOfCitations)
            position = endOfLink
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
    
    # in case this is one article before the last one, and the last one is a citation:
    # i.e. there will be no more "class=yC"
        #or (isOneArticleBeforeLast(sandboxHTML, position) and (sandboxHTML.find("class=yC", position) == -1))

    
    # in case this is the last article
        or ((isLastArticle(sandboxHTML, position)) and
        # and it has a link (also make sure it's not a citation)
            ((((sandboxHTML.find("class=gs_a", position) < sandboxHTML.find("class=yC", position))
               and (sandboxHTML.find("class=yC", position) != -1) and ((sandboxHTML.find("/scholar.bib") - sandboxHTML.find("class=yC")>300))) #handle ULI scenario
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
  
def remove_html_tags(data):
   p = re.compile(r'<.*?>')
   return p.sub('', data)            
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
    newHTMLdata = HTMLparser(url,newHTML.get_html())
    newHTMLdata.parseHTML()
    
    return newHTMLdata

def getResultsFromURLwithProxy(url):
    # first we fetch the HTML from Google Scholar
    newHTML = getHTML(url)
    newHTML.getHTMLfromURLwithProxy("202.44.12.72", 3128)
    #newHTML.getHTMLfromURLwithProxy("206.224.254.10", 80)
    
    # parse the results
    if type(newHTML.html) == int:
        return newHTML.html
    newHTMLdata = HTMLparser(url,newHTML.get_html())
    newHTMLdata.parseHTML()
    
    return newHTMLdata    


def getResultsFromURL_OFFLINE(url):

    html = """
    
    <html><head><meta http-equiv="content-type" content="text/html;charset=UTF-8"><meta http-equiv="imagetoolbar" content="no"><title>dna - Google Scholar</title><style>#gbar,#guser{font-size:13px;padding-top:1px !important}#gbar{float:left;height:22px}#guser{padding-bottom:7px !important;text-align:right}.gbh,.gbd{border-top:1px solid #c9d7f1;font-size:1px}.gbh{height:0;position:absolute;top:24px;width:100%}#gbs,.gbm{background:#fff;left:0;position:absolute;text-align:left;visibility:hidden;z-index:1000}.gbm{border:1px solid;border-color:#c9d7f1 #36c #36c #a2bae7;z-index:1001}.gb1{margin-right:.5em}.gb1,.gb3{zoom:1}.gb2{display:block;padding:.2em .5em;}.gb2,.gb3{text-decoration:none;border-bottom:none}a.gb1,a.gb2,a.gb3,a.gb4{color:#00c !important}.gbi .gb3,.gbi .gb2,.gbi .gb4{color:#dd8e27 !important}.gbf .gb3,.gbf .gb2,.gbf .gb4{color:#900 !important}a.gb2:hover{background:#36c;color:#fff !important}
body,td,div,a{font-family:arial,sans-serif}a:link{color:#00c}a:visited{color:#551a8b}a:active{color:#f00}.gs_r{position:relative}.gs_rt{width:44.5em}.gs_ggs{position:absolute;left:45em;top:0;white-space:nowrap}.gs_ctc{color:#00c;font-size:x-small;font-weight:bold}.gs_ctu{font-size:x-small;font-weight:bold}.gs_ctg{color:#7777cc;font-size:small;font-weight:bold}.gs_r h3{display:inline;font-weight:normal;font-size:100%;margin:0}a.gs_fl:link,.gs_fl a:link{color:#7777cc}a.gs_fl:visited,.gs_fl a:visited{color:#551a8b}a.gs_fl:active,.gs_fl a:active{color:#f00}.gs_a{color:#008000}.k{background-color:#008000}.i{color:#a90a08}.n a{font-size:10pt;color:#000}.n .i{font-size:10pt;font-weight:bold}.b{font-size:12pt;color:#00c;font-weight:bold}
table#scife_hdr{clear:both;margin:7px 3px 7px 3px}</style><script>window.gbar={};(function(){function h(a,b,d){var c="on"+b;if(a.addEventListener)a.addEventListener(b,d,false);else if(a.attachEvent)a.attachEvent(c,d);else{var f=a[c];a[c]=function(){var e=f.apply(this,arguments),g=d.apply(this,arguments);return e==undefined?g:g==undefined?e:g&&e}}};var i=window.gbar,k,l,m;function n(a){var b=window.encodeURIComponent&&(document.forms[0].q||"").value;if(b)a.href=a.href.replace(/([?&])q=[^&]*|$/,function(d,c){return(c||"&")+"q="+encodeURIComponent(b)})}i.qs=n;function o(a,b,d,c,f,e){var g=document.getElementById(a);if(g){var j=g.style;j.left=c?"auto":b+"px";j.right=c?b+"px":"auto";j.top=d+"px";j.visibility=l?"hidden":"visible";if(f&&e){j.width=f+"px";j.height=e+"px"}else{o(k,b,d,c,g.offsetWidth,g.offsetHeight);l=l?"":a}}}i.tg=function(a){a=a||window.event;var b,d=a.target||a.srcElement;a.cancelBubble=true;if(k!=null)p(d);else{b=document.createElement(Array.every||window.createPopup?"iframe":"div");b.frameBorder="0";k=b.id="gbs";b.src="javascript:''";d.parentNode.appendChild(b);h(document,"click",i.close);p(d);i.alld&&i.alld(function(){var c=document.getElementById("gbli");if(c){var f=c.parentNode;q(f,c);var e=c.prevSibling;f.removeChild(c);i.removeExtraDelimiters(f,e);b.style.height=f.offsetHeight+"px"}})}};function r(a){var b,d=document.defaultView;if(d&&d.getComputedStyle){if(a=d.getComputedStyle(a,""))b=a.direction}else b=a.currentStyle?a.currentStyle.direction:a.style.direction;return b=="rtl"}function p(a){var b=0;if(a.className!="gb3")a=a.parentNode;var d=a.getAttribute("aria-owns")||"gbi",c=a.offsetWidth,f=a.offsetTop>20?46:24,e=false;do b+=a.offsetLeft||0;while(a=a.offsetParent);a=(document.documentElement.clientWidth||document.body.clientWidth)-b-c;c=r(document.body);if(d=="gbi"){var g=document.getElementById("gbi");q(g,document.getElementById("gbli")||g.firstChild);if(c){b=a;e=true}}else if(!c){b=a;e=true}l!=d&&i.close();o(d,b,f,e)}i.close=function(){l&&o(l,0,0)};function s(a,b,d){if(!m){m="gb2";if(i.alld){var c=i.findClassName(a);if(c)m=c}}a.insertBefore(b,d).className=m}function q(a,b){for(var d,c=window.navExtra;c&&(d=c.pop());)s(a,d,b)}i.addLink=function(a,b,d){if((b=document.getElementById(b))&&a){a.className="gb4";var c=document.createElement("span");c.appendChild(a);c.appendChild(document.createTextNode(" | "));c.id=d;b.appendChild(c)}}})();

function fnGw(f,x){var e=document.createElement('span');e.innerHTML='<font size='+f+'>MMMMM</font>';x.appendChild(e);return (e.offsetWidth||0)/5.0;}function fnGss(n){var s=document.styleSheets;if(s){for(var i=s.length-1;i>=0;i--)if(s[i]){var r=s[i].cssRules||s[i].rules;if(r){for(var j=r.length-1;j>=0;j--){if(r[j]&&(r[j].selectorText||'').toLowerCase()==n){return r[j].style;}}}}}return null;}function fnGacal(){var s=fnGss('.gs_ggs');var q=fnGss('.gs_rt');if(s&&q){var d=document;var x=d.createElement('div');x.setAttribute('style','position:absolute;left:-1000;top:-1000');d.body.appendChild(x);var w0=(window.innerWidth||(document.documentElement?document.documentElement.clientWidth:0)||(document.body?document.body.clientWidth:0)||0);var w3=fnGw('3',x);var w2=fnGw('2',x);d.body.removeChild(x);if(w3-w2>=2&&w3-w2>=0.15*w2&&w2>10.5&&w0<w3*60){s.left='40em';q.width='39.5em';}}}</script></head><body bgcolor="#ffffff" onload="document.gs.reset()" topmargin=2 marginheight=2><div id=gbar><nobr><a href="http://www.google.co.il/search?hl=en&q=dna&sa=N&tab=sw" onclick=gbar.qs(this) class=gb1>Web</a> <a href="http://www.google.co.il/images?hl=en&q=dna&source=og&sa=N&tab=si" onclick=gbar.qs(this) class=gb1>Images</a> <a href="http://www.google.co.il/search?hl=en&q=dna&tbo=u&tbs=nws:1&source=og&sa=N&tab=sn" onclick=gbar.qs(this) class=gb1>News</a> <a href="http://translate.google.co.il/translate_t?hl=en&q=dna&sa=N&tab=sT" onclick=gbar.qs(this) class=gb1>Translate</a> <b class=gb1>Scholar</b> <a href="http://www.youtube.com/results?hl=en&q=dna&sa=N&tab=s1&gl=IL" onclick=gbar.qs(this) class=gb1>YouTube</a> <a href="http://mail.google.com/mail/?hl=en&tab=sm" class=gb1>Gmail</a> <a href="http://www.google.co.il/intl/en/options/" onclick="this.blur();gbar.tg(event);return !1" aria-haspopup=true class=gb3><u>more</u> <small>&#9660;</small></a><div class=gbm id=gbi><a href="http://www.google.com/calendar/render?hl=en&tab=sc" class=gb2>Calendar</a> <a href="http://docs.google.com/?hl=en&tab=so" class=gb2>Documents</a> <a href="http://www.google.co.il/reader/view/?hl=en&tab=sy" class=gb2>Reader</a> <a href="http://sites.google.com/?hl=en&tab=s3" class=gb2>Sites</a> <a href="http://groups.google.co.il/groups?hl=en&q=dna&sa=N&tab=sg" onclick=gbar.qs(this) class=gb2>Groups</a> <div class=gb2><div class=gbd></div></div><a href="http://www.google.co.il/intl/en/options/" class=gb2>even more &raquo;</a> </div></nobr></div><div class=gbh style=left:0></div><div class=gbh style=right:0></div><div align=right id=guser style="font-size:84%;padding:0 0 4px" width=100%><nobr><b>romalabunsky@gmail.com</b> | <a href="https://www.google.com/accounts/ManageAccount">My Account</a> | <a href="/accounts/ClearSID?continue=http://www.google.com/accounts/Logout%3Fcontinue%3Dhttp://scholar.google.co.il/scholar%253Fhl%253Den%2526q%253Ddna%2526btnG%253DSearch%2526as_sdt%253D2000%2526as_ylo%253D%2526as_vis%253D0">Sign out</a></nobr></div><script><!--
fnGacal();//-->

</script><form name=gs method=GET action="/scholar"><table border=0 cellpadding=0 cellspacing=0 id="scife_hdr"><tr><td valign=top><a href="/schhp?hl=en&amp;as_sdt=2000" target="_top"><img src="/intl/en/images/scholar_logo_md_2009.gif" width="189" height="40" alt="Scholar Home" border=0 vspace=2></a>&nbsp;&nbsp;</td><td valign=top><table cellpadding=0 cellspacing=0 border=0 style="margin:1px 3px 1px 0px"><tr><td nowrap><input type=hidden name=hl value="en"><input type=text name=q size=41 maxlength=2048 value="dna"><font size=-1> <input type=submit name="btnG" value="Search"></font></td><td>&nbsp;&nbsp;</td><td valign="top" nowrap><font size=-2><a href="/advanced_scholar_search?q=dna&amp;hl=en&amp;as_sdt=2000">Advanced Scholar Search</a><br><a href="/scholar_preferences?q=dna&amp;hl=en&amp;as_sdt=2000">Scholar Preferences</a><br></font></td></tr></table></td></tr></table><table width=100% border=0 cellpadding=0 cellspacing=0 bgcolor=#dcf6db><tr><td colspan=2 bgcolor=#008000><img width=1 height=1 alt=""></td></tr><tr><td bgcolor=#dcf6db nowrap><font size=+1> <b>Scholar</b></font>&nbsp; <a href="/scholar_alerts?view_op=create_alert_options&amp;hl=en&amp;alert_query=intitle:dna&amp;alert_params=hl%3Den%26as_sdt%3D2000"><img src="/scholar/scholar_envelope.png" width="22" height="19" title="Create email alert" border=0 align="texttop"></a><sup>&nbsp;<font color="red">New!</font></sup> <select name="as_sdt" onChange="document.gs.submit()"><option value="2000" selected>Articles and patents<option value="2001">&nbsp;&nbsp;Articles excluding patents<option value="2002">Legal opinions and journals<option value="2003">&nbsp;&nbsp;Federal cases<option value="2004">&nbsp;&nbsp;California cases<option value="2000!">  Advanced search&hellip;</select> <select name="as_ylo" onChange="document.gs.submit()"><option value="" selected>anytime<option value="2010">since 2010<option value="2009">since 2009<option value="2008">since 2008<option value="2007">since 2007<option value="2006">since 2006<option value="2005">since 2005<option value="2004">since 2004<option value="2003">since 2003<option value="2002">since 2002<option value="2001">since 2001<option value="2000">since 2000<option value="1999">since 1999<option value="1998">since 1998<option value="1997">since 1997<option value="1996">since 1996<option value="1995">since 1995<option value="1994">since 1994<option value="1993">since 1993<option value="1992">since 1992<option value="1991">since 1991</select> <select name="as_vis" onChange="document.gs.submit()"><option value="0" selected>include citations<option value="1">at least summaries</select></td><td bgcolor=#dcf6db align=right nowrap><font size=-1>Results <b>1</b> - <b>10</b> of about <b>2,930,000</b>.   (<b>0.08</b> sec)&nbsp;</font></td></tr></table></form><p><div class=gs_r><div class=gs_rt><h3><a href="http://www.liebertonline.com/doi/abs/10.1089/dna.1985.4.165" class=yC0>Supercoil sequencing: a fast and simple method for sequencing plasmid <b>DNA</b></a></h3></div><font size=-1><span class=gs_a>EY CHEN, PH Seeburg - <b>DNA</b>, 1985 - liebertonline.com</span><br><b>...</b> LABORATORY METHODS Supercoil Sequencing: A Fast and Simple Method for Sequencing<br>

Plasmid <b>DNA</b> ELLSON Y. CHEN and PETER H. SEEBURG 4\BSTRACT A method for obtaining<br>
sequence information directly from plasmid <b>DNA</b> is presented. The procedure in- <b>...</b> 
<br><span class=gs_fl><a href="/scholar?cites=12514014065693661259&amp;hl=en&amp;as_sdt=2000">Cited by 1932</a> - <a href="/scholar?q=related:S5jpm321qq0J:scholar.google.com/&amp;hl=en&amp;as_sdt=2000">Related articles</a> - <a href="/scholar?cluster=12514014065693661259&amp;hl=en&amp;as_sdt=2000">All 6 versions</a> - <a href="/scholar.bib?q=info:S5jpm321qq0J:scholar.google.com/&amp;output=citation&amp;hl=en&amp;as_sdt=2000&amp;ct=citation&amp;cd=0">Import into BibTeX</a></span></font>  </div>  <p><div class=gs_r><div class=gs_rt><h3><a href="http://www.liebertonline.com/doi/abs/10.1089/dna.1.1984.3.479" class=yC1>Oligonucleotide-directed mutagenesis: a simple method using two oligonucleotide primers and a single-stranded <b>DNA </b>template</a></h3></div><font size=-1><span class=gs_a>MJ Zoller, M Smith - <b>DNA</b>, 1984 - liebertonline.com</span><br>Page 1. <b>DNA</b> Volume 3, Number 6, 1984 Mary Ann Liebert, Inc., Publishers LABORATORY<br>

METHODS Oligonucleotide-Directed Mutagenesis: A Simple Method Using Two Oligonucleotide<br>
Primers and a Single-Stranded <b>DNA</b> Template MARK J. ZOLLER* and MICHAEL SMITHt <b>...</b> 
<br><span class=gs_fl><a href="/scholar?cites=15635484437270465994&amp;hl=en&amp;as_sdt=2000">Cited by 919</a> - <a href="/scholar?q=related:yo2nXkFm_NgJ:scholar.google.com/&amp;hl=en&amp;as_sdt=2000">Related articles</a> - <a href="/scholar?cluster=15635484437270465994&amp;hl=en&amp;as_sdt=2000">All 4 versions</a> - <a href="/scholar.bib?q=info:yo2nXkFm_NgJ:scholar.google.com/&amp;output=citation&amp;hl=en&amp;as_sdt=2000&amp;ct=citation&amp;cd=1">Import into BibTeX</a></span></font>  </div>  <p><div class=gs_r><div class=gs_rt><h3><span class=gs_ctc>[CITATION]</span> <a href="http://www.ncbi.nlm.nih.gov/pubmed/6246368" class=yC2>Sequencing end-labeled <b>DNA </b>with base-specific chemical cleavages.</a></h3></div><font size=-1><span class=gs_a>AM Maxam, W Gilbert - Methods in enzymology, 1980 - ncbi.nlm.nih.gov</span><br>1980;65(1):499-560. Sequencing end-labeled <b>DNA</b> with base-specific chemical cleavages.<br>

Maxam AM, Gilbert W. Publication Types: Research Support, US Gov&#39;t, PHS. Mesh Terms: Base<br>
Sequence*; Chromatography, Ion Exchange/methods; <b>DNA</b>*; <b>DNA</b> Restriction Enzymes*; <b>...</b> 
<br><span class=gs_fl><a href="/scholar?cites=12851970067551012640&amp;hl=en&amp;as_sdt=2000">Cited by 13081</a> - <a href="/scholar?q=related:IMdUDK9eW7IJ:scholar.google.com/&amp;hl=en&amp;as_sdt=2000">Related articles</a> - <a href="/scholar.bib?q=info:IMdUDK9eW7IJ:scholar.google.com/&amp;output=citation&amp;hl=en&amp;as_sdt=2000&amp;ct=citation&amp;cd=2">Import into BibTeX</a></span></font>  </div>  <p><div class=gs_r><div class=gs_rt><h3><a href="http://linkinghub.elsevier.com/retrieve/pii/0003269783904189" class=yC3>A technique for radiolabeling <b>DNA </b>restriction endonuclease fragments to high specific activity</a></h3></div><span class="gs_ggs gs_fl">  <a href="http://www.tdnet.com/TAU/resolver/default.asp?sid=google&amp;auinit=AP&amp;aulast=Feinberg&amp;atitle=A+technique+for+radiolabeling+DNA+restriction+endonuclease+fragments+to+high+specific+activity&amp;title=Analytical+Biochemistry&amp;volume=132&amp;issue=1&amp;date=1983&amp;spage=6&amp;issn=0003-2697" class=yC4>TAU full text</a></span><font size=-1><span class=gs_a>AP Feinberg, B Vogelstein - Analytical Biochemistry, 1983 - Elsevier</span><br>A technique for conveniently radiolabeling <b>DNA</b> restriction endonuclease fragments to high specific <br>

activity is described. <b>DNA</b> fragments are purified from agarose gels directly by ethanol precipitation <br>
and are then denatured and labeled with the large fragment of <b>DNA</b> polymerase I, using <b> ...</b> <br><span class=gs_fl><a href="/scholar?cites=17127367576355477966&amp;hl=en&amp;as_sdt=2000">Cited by 21988</a> - <a href="/scholar?q=related:zhk25hCisO0J:scholar.google.com/&amp;hl=en&amp;as_sdt=2000">Related articles</a> - <a href="/scholar?cluster=17127367576355477966&amp;hl=en&amp;as_sdt=2000">All 4 versions</a> - <a href="/scholar.bib?q=info:zhk25hCisO0J:scholar.google.com/&amp;output=citation&amp;hl=en&amp;as_sdt=2000&amp;ct=citation&amp;cd=3">Import into BibTeX</a></span></font>  </div>  <p><div class=gs_r><div class=gs_rt><h3><a href="http://nar.oxfordjournals.org/cgi/reprint/16/3/1215.pdf" class=yC5>A simple salting out procedure for extracting <b>DNA </b>from human nucleated cells</a></h3></div><span class="gs_ggs gs_fl">  <a href="http://www.tdnet.com/TAU/resolver/default.asp?sid=google&amp;auinit=SA&amp;aulast=Miller&amp;atitle=A+simple+salting+out+procedure+for+extracting+DNA+from+human+nucleated+cells&amp;id=doi:10.1093/nar/16.3.1215&amp;title=Nucleic+Acids+Research&amp;volume=16&amp;issue=3&amp;date=1988&amp;spage=1215&amp;issn=0305-1048" class=yC6>TAU full text</a></span><font size=-1><span class=gs_a>SA Miller, DD Dykes, HF Polesky - Nucleic acids research, 1988 - Oxford Univ Press</span><br>One of the obstacles encountered when extracting <b>DNA</b> from a large number of samples is the <br>

cumbersome method of deprotein- izing cell digests with the hazardous organic solvents phenol <br>
and isochloroform. Several other non-toxic extraction pro- cedures have been published, <b> ...</b> <br><span class=gs_fl><a href="/scholar?cites=17231930799021592101&amp;hl=en&amp;as_sdt=2000">Cited by 10292</a> - <a href="/scholar?q=related:JY7LVcMdJO8J:scholar.google.com/&amp;hl=en&amp;as_sdt=2000">Related articles</a> - <a href="/scholar?cluster=17231930799021592101&amp;hl=en&amp;as_sdt=2000">All 8 versions</a> - <a href="/scholar.bib?q=info:JY7LVcMdJO8J:scholar.google.com/&amp;output=citation&amp;hl=en&amp;as_sdt=2000&amp;ct=citation&amp;cd=4">Import into BibTeX</a></span></font>  </div>  <p><div class=gs_r><div class=gs_rt><h3><span class=gs_ctc>[HTML]</span> <a href="http://breast-cancer-research.com/content/7/6/R1058/ref" class=yC7>1. King CR, Kraus MH, Aaronson SA: Amplification of a novel v-erbB-related gene in a human mammary carcinoma.</a></h3></div><span class="gs_ggs gs_fl"><b><a href="http://breast-cancer-research.com/content/7/6/R1058/ref" class=yC8>breast-cancer-research.com</a> <span class=gs_ctg>[HTML]</span></b>  <br><a href="http://www.tdnet.com/TAU/resolver/default.asp?sid=google&amp;auinit=MC&amp;aulast=Biol&amp;atitle=1.+King+CR,+Kraus+MH,+Aaronson+SA:+Amplification+of+a+novel+v-erbB-related+gene+in+a+human+mammary+carcinoma.&amp;title=Science&amp;volume=229&amp;date=1985&amp;spage=974" class=yC9>TAU full text</a></span><font size=-1><span class=gs_a>MC Biol, JC Oncol, JB Sci, NRMC Biol, JB  &hellip; -  &hellip;, 1985 - breast-cancer-research.com</span><br>King CR, Kraus MH, Aaronson SA: Amplification of a novel v-erbB-related gene in a human mammary <br>

carcinoma.  <b> ...</b> Coussens L, Yang-Feng TL, Liao YC, Chen E, Gray A, McGrath J, Seeburg <br>
PH, Libermann TA, Schlessinger J, Francke U, et al.: Tyrosine kinase receptor with <b> ...</b> <br><span class=gs_fl><a href="/scholar?cites=16818414828254677243&amp;hl=en&amp;as_sdt=2000">Cited by 669</a> - <a href="/scholar?q=related:-0hIsy0DZ-kJ:scholar.google.com/&amp;hl=en&amp;as_sdt=2000">Related articles</a> - <a href="http://74.125.155.132/scholar?q=cache:-0hIsy0DZ-kJ:scholar.google.com/+dna&amp;hl=en&amp;as_sdt=2000">Cached</a> - <a href="/scholar?cluster=16818414828254677243&amp;hl=en&amp;as_sdt=2000">All 6 versions</a> - <a href="/scholar.bib?q=info:-0hIsy0DZ-kJ:scholar.google.com/&amp;output=citation&amp;hl=en&amp;as_sdt=2000&amp;ct=citation&amp;cd=5">Import into BibTeX</a></span></font>  </div>  <p><div class=gs_r><div class=gs_rt><h3><a href="http://www.ncbi.nlm.nih.gov/pmc/articles/PMC342324/" class=yCA>A rapid alkaline extraction procedure for screening recombinant plasmid <b>DNA</b>.</a></h3></div><span class="gs_ggs gs_fl"><b><a href="http://www.pubmedcentral.nih.gov/picrender.fcgi?artid=342324&amp;blobtype=pdf" class=yCB>nih.gov</a> <span class=gs_ctg>[PDF]</span></b>  <br><a href="http://www.tdnet.com/TAU/resolver/default.asp?sid=google&amp;auinit=HC&amp;aulast=Birnboim&amp;atitle=A+rapid+alkaline+extraction+procedure+for+screening+recombinant+plasmid+DNA.&amp;title=Nucleic+Acids+Research&amp;volume=7&amp;issue=6&amp;date=1979&amp;spage=1513&amp;issn=0305-1048" class=yCC>TAU full text</a></span><font size=-1><span class=gs_a>HC Birnboim, J Doly - Nucleic acids research, 1979 - ncbi.nlm.nih.gov</span><br>A procedure for extracting plasmid <b>DNA</b> from bacterial cells is described. The method is simple <br>

enough to permit the analysis by gel electrophoresis of 100 or more clones per day yet yields <br>
plasmid <b>DNA</b> which is pure enough to be digestible by restriction enzymes. The principle <b> ...</b> <br><span class=gs_fl><a href="/scholar?cites=8236556212916941990&amp;hl=en&amp;as_sdt=2000">Cited by 11005</a> - <a href="/scholar?q=related:pnRzizwgTnIJ:scholar.google.com/&amp;hl=en&amp;as_sdt=2000">Related articles</a> - <a href="/scholar?cluster=8236556212916941990&amp;hl=en&amp;as_sdt=2000">All 6 versions</a> - <a href="/scholar.bib?q=info:pnRzizwgTnIJ:scholar.google.com/&amp;output=citation&amp;hl=en&amp;as_sdt=2000&amp;ct=citation&amp;cd=6">Import into BibTeX</a></span></font>  </div>  <p><div class=gs_r><div class=gs_rt><h3><a href="http://www.nature.com/nbt/wilma/v16n1.882370413.html" class=yCD><b>DNA </b>chips: an array of possibilities.</a></h3></div><font size=-1><span class=gs_a>A Marshall, J Hodgson - <b>DNA</b>, 1998 - nature.com</span><br>One year ago, the remarkable thing about <b>DNA</b> chips was that anyone could make them at <br>

all. Now, it seems everyone is finding new ways of making them. With many of the technological <br>
hurdles to array fabrication overcome, numerous companies and academic groups are <b> ...</b> <br><span class=gs_fl><a href="/scholar?cites=5816991942497716849&amp;hl=en&amp;as_sdt=2000">Cited by 471</a> - <a href="/scholar?q=related:ccriGVobulAJ:scholar.google.com/&amp;hl=en&amp;as_sdt=2000">Related articles</a> - <a href="http://direct.bl.uk/research/1A/44/RN037961280.html?source=googlescholar" class=yCE>BL Direct</a> - <a href="/scholar?cluster=5816991942497716849&amp;hl=en&amp;as_sdt=2000">All 4 versions</a> - <a href="/scholar.bib?q=info:ccriGVobulAJ:scholar.google.com/&amp;output=citation&amp;hl=en&amp;as_sdt=2000&amp;ct=citation&amp;cd=7">Import into BibTeX</a></span></font>  </div>  <p><div class=gs_r><div class=gs_rt><h3><a href="http://bioinformatics.oxfordjournals.org/cgi/content/abstract/14/9/817" class=yCF>Modeltest: testing the model of <b>DNA </b>substitution</a></h3></div><span class="gs_ggs gs_fl"><b><a href="http://bioinformatics.oxfordjournals.org/cgi/reprint/14/9/817.pdf" class=yC10>oxfordjournals.org</a> <span class=gs_ctg>[PDF]</span></b>  <br><a href="http://www.tdnet.com/TAU/resolver/default.asp?sid=google&amp;auinit=D&amp;aulast=Posada&amp;atitle=Modeltest:+testing+the+model+of+DNA+substitution&amp;id=doi:10.1093/bioinformatics/14.9.817&amp;title=Bioinformatics&amp;volume=14&amp;issue=9&amp;date=1998&amp;spage=817&amp;issn=1367-4803" class=yC11>TAU full text</a></span><font size=-1><span class=gs_a>D Posada, KA Crandall - Bioinformatics, 1998 - Oxford Univ Press</span><br>All phylogenetic methods make assumptions, whether ex- <br>

plicitorimplicit,abouttheprocessofDNAsubstitution(Fel- senstein, 1988). For example, an assumption <br>
common to many phylogenetic methods is a bifurcating tree to describe the phylogeny of <b> ...</b> <br><span class=gs_fl><a href="/scholar?cites=6289883537372548310&amp;hl=en&amp;as_sdt=2000">Cited by 9349</a> - <a href="/scholar?q=related:1gyrg8AnSlcJ:scholar.google.com/&amp;hl=en&amp;as_sdt=2000">Related articles</a> - <a href="http://direct.bl.uk/research/47/5C/RN053703653.html?source=googlescholar" class=yC12>BL Direct</a> - <a href="/scholar?cluster=6289883537372548310&amp;hl=en&amp;as_sdt=2000">All 25 versions</a> - <a href="/scholar.bib?q=info:1gyrg8AnSlcJ:scholar.google.com/&amp;output=citation&amp;hl=en&amp;as_sdt=2000&amp;ct=citation&amp;cd=8">Import into BibTeX</a></span></font>  </div>  <p><div class=gs_r><div class=gs_rt><h3><a href="http://nar.oxfordjournals.org/cgi/content/abstract/8/19/4321" class=yC13>Rapid isolation of high molecular weight plant <b>DNA</b></a></h3></div><span class="gs_ggs gs_fl"><b><a href="http://www.ncbi.nlm.nih.gov/pmc/articles/PMC324241/pdf/nar00436-0009.pdf" class=yC14>nih.gov</a> <span class=gs_ctg>[PDF]</span></b>  <br><a href="http://www.tdnet.com/TAU/resolver/default.asp?sid=google&amp;auinit=MG&amp;aulast=Murray&amp;atitle=Rapid+isolation+of+high+molecular+weight+plant+DNA&amp;id=doi:10.1093/nar/8.19.4321&amp;title=Nucleic+Acids+Research&amp;volume=8&amp;issue=19&amp;date=1980&amp;spage=4321&amp;issn=0305-1048" class=yC15>TAU full text</a></span><font size=-1><span class=gs_a>MG Murray, WF Thompson - Nucleic Acids Research, 1980 - Oxford Univ Press</span><br>With the increasing use of recombinant <b>DNA</b> techniques in plant research the preparation of <br>

long, pure <b>DNA</b> has become a major concern. Since the same forces which are required to break <br>
cell walls can also shear <b>DNA</b>, consider- able care must be taken and one must often <b> ...</b> <br><span class=gs_fl><a href="/scholar?cites=181829391196496209&amp;hl=en&amp;as_sdt=2000">Cited by 4214</a> - <a href="/scholar?q=related:USH-L978hQIJ:scholar.google.com/&amp;hl=en&amp;as_sdt=2000">Related articles</a> - <a href="/scholar?cluster=181829391196496209&amp;hl=en&amp;as_sdt=2000">All 6 versions</a> - <a href="/scholar.bib?q=info:USH-L978hQIJ:scholar.google.com/&amp;output=citation&amp;hl=en&amp;as_sdt=2000&amp;ct=citation&amp;cd=9">Import into BibTeX</a></span></font>  </div>    <br><a href="/scholar_alerts?view_op=create_alert_options&amp;hl=en&amp;alert_query=intitle:dna&amp;alert_params=hl%3Den%26as_sdt%3D2000"><img src="/scholar/scholar_envelope.png" width="22" height="19" title="Create email alert" border=0 align="texttop"></a>&nbsp;<a href="/scholar_alerts?view_op=create_alert_options&amp;hl=en&amp;alert_query=intitle:dna&amp;alert_params=hl%3Den%26as_sdt%3D2000">Create email alert</a><sup>&nbsp;<font color="red">New!</font></sup><br clear=all><br><div class=n><table align=center border=0 cellpadding=0 cellspacing=0 width="1%"><tr align=center valign=top><td valign=bottom nowrap><font size=-1>Result&nbsp;Page:&nbsp;</font></td><td><img src="/intl/en/nav_first.gif" width="18" height="26" border=0><br></td><td><img src="/intl/en/nav_current.gif" width="16" height="26" border=0><br><span class="i">1</span></td><td><a href="/scholar?start=10&amp;q=dna&amp;hl=en&amp;as_sdt=2000"><img src="/intl/en/nav_page.gif" width="16" height="26" border=0><br>2</a></td><td><a href="/scholar?start=20&amp;q=dna&amp;hl=en&amp;as_sdt=2000"><img src="/intl/en/nav_page.gif" width="16" height="26" border=0><br>3</a></td><td><a href="/scholar?start=30&amp;q=dna&amp;hl=en&amp;as_sdt=2000"><img src="/intl/en/nav_page.gif" width="16" height="26" border=0><br>4</a></td><td><a href="/scholar?start=40&amp;q=dna&amp;hl=en&amp;as_sdt=2000"><img src="/intl/en/nav_page.gif" width="16" height="26" border=0><br>5</a></td><td><a href="/scholar?start=50&amp;q=dna&amp;hl=en&amp;as_sdt=2000"><img src="/intl/en/nav_page.gif" width="16" height="26" border=0><br>6</a></td><td><a href="/scholar?start=60&amp;q=dna&amp;hl=en&amp;as_sdt=2000"><img src="/intl/en/nav_page.gif" width="16" height="26" border=0><br>7</a></td><td><a href="/scholar?start=70&amp;q=dna&amp;hl=en&amp;as_sdt=2000"><img src="/intl/en/nav_page.gif" width="16" height="26" border=0><br>8</a></td><td><a href="/scholar?start=80&amp;q=dna&amp;hl=en&amp;as_sdt=2000"><img src="/intl/en/nav_page.gif" width="16" height="26" border=0><br>9</a></td><td><a href="/scholar?start=90&amp;q=dna&amp;hl=en&amp;as_sdt=2000"><img src="/intl/en/nav_page.gif" width="16" height="26" border=0><br>10</a></td><td nowrap><a href="/scholar?start=10&amp;q=dna&amp;hl=en&amp;as_sdt=2000"><img src="/intl/en/nav_next.gif" width="100" height="26" border=0><br><span class="b">Next</span></a></td></tr></table></div><center><br clear=all><br><table cellspacing=0 cellpadding=0 border=0 width="100%"><tr><td class=k><img height=1 alt="" width=1></td></tr><tr><td align=center bgcolor=#dcf6db>&nbsp;<br><table border=0 cellpadding=0 cellspacing=0 align=center><tr><td nowrap><form method=GET action=/scholar><font size=-1><input type=text name=q size=31 maxlength=2048 value="dna"><input type=submit name=btnG VALUE="Search"><input type=hidden name=hl value="en"><input type=hidden name=as_sdt value="2000"></font></form></td></tr></table><br></td></tr><tr><td class=k><img height=1 alt="" width=1></td></tr></table></center><center><p><font size=-1><a href="http://www.google.co.il/webhp?hl=en" target="_top">Go to Google Home</a> <span>-</span> <a href="http://www.google.co.il/intl/en/about.html" target="_top">About Google</a> <span>-</span> <a href="/intl/en/scholar/about.html" target="_top">About Google Scholar</a></font><p><font size=-2>&copy;2010 Google</font></center><style>.yC0:active,.yC0:focus:hover{background:url("/scholar_url?sa=T&ct=res&cd=0&url=http://www.liebertonline.com/doi/abs/10.1089/dna.1985.4.165&ei=z_D_S-ChDIyS6AKH2IzXCg")}.yC1:active,.yC1:focus:hover{background:url("/scholar_url?sa=T&ct=res&cd=1&url=http://www.liebertonline.com/doi/abs/10.1089/dna.1.1984.3.479&ei=z_D_S-ChDIyS6AKH2IzXCg")}.yC2:active,.yC2:focus:hover{background:url("/scholar_url?sa=T&ct=res&cd=2&url=http://www.ncbi.nlm.nih.gov/pubmed/6246368&ei=z_D_S-ChDIyS6AKH2IzXCg")}.yC3:active,.yC3:focus:hover{background:url("/scholar_url?sa=T&ct=res&cd=3&url=http://linkinghub.elsevier.com/retrieve/pii/0003269783904189&ei=z_D_S-ChDIyS6AKH2IzXCg")}.yC4:active,.yC4:focus:hover{background:url("/scholar_url?sa=T&oi=institution&ct=llp&cd=3&url=http://www.tdnet.com/TAU/resolver/default.asp%3Fsid%3Dgoogle%26auinit%3DAP%26aulast%3DFeinberg%26atitle%3DA%2Btechnique%2Bfor%2Bradiolabeling%2BDNA%2Brestriction%2Bendonuclease%2Bfragments%2Bto%2Bhigh%2Bspecific%2Bactivity%26title%3DAnalytical%2BBiochemistry%26volume%3D132%26issue%3D1%26date%3D1983%26spage%3D6%26issn%3D0003-2697&ei=z_D_S-ChDIyS6AKH2IzXCg")}.yC5:active,.yC5:focus:hover{background:url("/scholar_url?sa=T&ct=res&cd=4&url=http://nar.oxfordjournals.org/cgi/reprint/16/3/1215.pdf&ei=z_D_S-ChDIyS6AKH2IzXCg")}.yC6:active,.yC6:focus:hover{background:url("/scholar_url?sa=T&oi=institution&ct=llp&cd=4&url=http://www.tdnet.com/TAU/resolver/default.asp%3Fsid%3Dgoogle%26auinit%3DSA%26aulast%3DMiller%26atitle%3DA%2Bsimple%2Bsalting%2Bout%2Bprocedure%2Bfor%2Bextracting%2BDNA%2Bfrom%2Bhuman%2Bnucleated%2Bcells%26id%3Ddoi:10.1093/nar/16.3.1215%26title%3DNucleic%2BAcids%2BResearch%26volume%3D16%26issue%3D3%26date%3D1988%26spage%3D1215%26issn%3D0305-1048&ei=z_D_S-ChDIyS6AKH2IzXCg")}.yC7:active,.yC7:focus:hover{background:url("/scholar_url?sa=T&oi=ggp&ct=res&cd=5&url=http://breast-cancer-research.com/content/7/6/R1058/ref&ei=z_D_S-ChDIyS6AKH2IzXCg")}.yC8:active,.yC8:focus:hover{background:url("/scholar_url?sa=T&oi=gga&ct=gga&cd=5&url=http://breast-cancer-research.com/content/7/6/R1058/ref&ei=z_D_S-ChDIyS6AKH2IzXCg")}.yC9:active,.yC9:focus:hover{background:url("/scholar_url?sa=T&oi=institution&ct=llp&cd=5&url=http://www.tdnet.com/TAU/resolver/default.asp%3Fsid%3Dgoogle%26auinit%3DMC%26aulast%3DBiol%26atitle%3D1.%2BKing%2BCR,%2BKraus%2BMH,%2BAaronson%2BSA:%2BAmplification%2Bof%2Ba%2Bnovel%2Bv-erbB-related%2Bgene%2Bin%2Ba%2Bhuman%2Bmammary%2Bcarcinoma.%26title%3DScience%26volume%3D229%26date%3D1985%26spage%3D974&ei=z_D_S-ChDIyS6AKH2IzXCg")}.yCA:active,.yCA:focus:hover{background:url("/scholar_url?sa=T&ct=res&cd=6&url=http://www.ncbi.nlm.nih.gov/pmc/articles/PMC342324/&ei=z_D_S-ChDIyS6AKH2IzXCg")}.yCB:active,.yCB:focus:hover{background:url("/scholar_url?sa=T&oi=gga&ct=gga&cd=6&url=http://www.pubmedcentral.nih.gov/picrender.fcgi%3Fartid%3D342324%26blobtype%3Dpdf&ei=z_D_S-ChDIyS6AKH2IzXCg")}.yCC:active,.yCC:focus:hover{background:url("/scholar_url?sa=T&oi=institution&ct=llp&cd=6&url=http://www.tdnet.com/TAU/resolver/default.asp%3Fsid%3Dgoogle%26auinit%3DHC%26aulast%3DBirnboim%26atitle%3DA%2Brapid%2Balkaline%2Bextraction%2Bprocedure%2Bfor%2Bscreening%2Brecombinant%2Bplasmid%2BDNA.%26title%3DNucleic%2BAcids%2BResearch%26volume%3D7%26issue%3D6%26date%3D1979%26spage%3D1513%26issn%3D0305-1048&ei=z_D_S-ChDIyS6AKH2IzXCg")}.yCD:active,.yCD:focus:hover{background:url("/scholar_url?sa=T&ct=res&cd=7&url=http://www.nature.com/nbt/wilma/v16n1.882370413.html&ei=z_D_S-ChDIyS6AKH2IzXCg")}.yCE:active,.yCE:focus:hover{background:url("/scholar_url?sa=T&ct=docdel&cd=7&url=http://direct.bl.uk/research/1A/44/RN037961280.html%3Fsource%3Dgooglescholar&ei=z_D_S-ChDIyS6AKH2IzXCg")}.yCF:active,.yCF:focus:hover{background:url("/scholar_url?sa=T&ct=res&cd=8&url=http://bioinformatics.oxfordjournals.org/cgi/content/abstract/14/9/817&ei=z_D_S-ChDIyS6AKH2IzXCg")}.yC10:active,.yC10:focus:hover{background:url("/scholar_url?sa=T&oi=gga&ct=gga&cd=8&url=http://bioinformatics.oxfordjournals.org/cgi/reprint/14/9/817.pdf&ei=z_D_S-ChDIyS6AKH2IzXCg")}.yC11:active,.yC11:focus:hover{background:url("/scholar_url?sa=T&oi=institution&ct=llp&cd=8&url=http://www.tdnet.com/TAU/resolver/default.asp%3Fsid%3Dgoogle%26auinit%3DD%26aulast%3DPosada%26atitle%3DModeltest:%2Btesting%2Bthe%2Bmodel%2Bof%2BDNA%2Bsubstitution%26id%3Ddoi:10.1093/bioinformatics/14.9.817%26title%3DBioinformatics%26volume%3D14%26issue%3D9%26date%3D1998%26spage%3D817%26issn%3D1367-4803&ei=z_D_S-ChDIyS6AKH2IzXCg")}.yC12:active,.yC12:focus:hover{background:url("/scholar_url?sa=T&ct=docdel&cd=8&url=http://direct.bl.uk/research/47/5C/RN053703653.html%3Fsource%3Dgooglescholar&ei=z_D_S-ChDIyS6AKH2IzXCg")}.yC13:active,.yC13:focus:hover{background:url("/scholar_url?sa=T&ct=res&cd=9&url=http://nar.oxfordjournals.org/cgi/content/abstract/8/19/4321&ei=z_D_S-ChDIyS6AKH2IzXCg")}.yC14:active,.yC14:focus:hover{background:url("/scholar_url?sa=T&oi=gga&ct=gga&cd=9&url=http://www.ncbi.nlm.nih.gov/pmc/articles/PMC324241/pdf/nar00436-0009.pdf&ei=z_D_S-ChDIyS6AKH2IzXCg")}.yC15:active,.yC15:focus:hover{background:url("/scholar_url?sa=T&oi=institution&ct=llp&cd=9&url=http://www.tdnet.com/TAU/resolver/default.asp%3Fsid%3Dgoogle%26auinit%3DMG%26aulast%3DMurray%26atitle%3DRapid%2Bisolation%2Bof%2Bhigh%2Bmolecular%2Bweight%2Bplant%2BDNA%26id%3Ddoi:10.1093/nar/8.19.4321%26title%3DNucleic%2BAcids%2BResearch%26volume%3D8%26issue%3D19%26date%3D1980%26spage%3D4321%26issn%3D0305-1048&ei=z_D_S-ChDIyS6AKH2IzXCg")}</style></body></html>
    
    
    """
    newHTMLdata = HTMLparser(url, html)
    newHTMLdata.parseHTML()
    
    return newHTMLdata    


# this function receives a searchParams object and returns ALL results for the query
# used for creating / updating follows
def getAllResultsFromURL(searchParams):
    isFinished = False
    
    searchParams.updateNumOfResults(100)
    searchParams.updateYearStart(2010)
    searchURL = searchParams.constructURL()
    
    HTMLdata = getResultsFromURL(searchURL)
    
    if HTMLdata.get_numOfResults() <= 100:
        return HTMLdata.get_results()
    else:
        i = 1
        allResults = HTMLdata.get_results()
        while (not isFinished):
            sleep(10)
            searchParams.updateStartFrom(i*100)
            searchURL = searchParams.constructURL()
            HTMLdata = getResultsFromURL(searchURL)
            currentResults = HTMLdata.get_results()
            allResults.extend(currentResults)
            if len(currentResults)<100:
                isFinished = True
            i+=1
        
        return allResults

            
                    
    

# this function receives a searchParams object and returns ALL results for the query
# used for creating / updating follows
def getAllResultsFromURLwithProxy(searchParams):
    isFinished = False
    
    searchParams.updateNumOfResults(100)
    searchParams.updateYearStart(2010)
    
    searchURL = searchParams.constructURL()
    
    HTMLdata = getResultsFromURLwithProxy(searchURL)
    
    if HTMLdata.get_numOfResults() <= 100:
        return HTMLdata.get_results()
    else:
        i = 1
        allResults = HTMLdata.get_results()
        while (not isFinished):
            searchParams.updateStartFrom(i*100)
            searchURL = searchParams.constructURL()
            HTMLdata = getResultsFromURLwithProxy(searchURL)
            currentResults = HTMLdata.get_results()
            allResults.extend(currentResults)
            if len(currentResults)<100:
                isFinished = True
            i+=1
        
        return allResults

            
                    
            
        
        
        
        
        
        
        