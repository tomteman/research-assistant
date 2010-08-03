import urllib

class SearchParams:
    """
    search parameters:
        pass any specified parameter in form: parametr_name = "value"
        example:
        user specified keywords = "matrix": param = SearchParams(keywords = "matrix" )
        user specified exact_phrase = "matrix multiplication" and number of results = 20: 
                param = SearchParams(exact_phrase = "matrix multiplication", num_of_results = 20)
              
    """
    def __init__(self,
                 keywords = "",               #search keywords
                 exact_phrase = "",           #search for exact keywords 
                 without_the_words = "",       #search within the words
                 one_of_the_words = "",       #at least one of the words
                 occurence = "any",           #where the words occur: any/title 
                 num_of_results = 10,         #number of results per page
                 author = "",                 #author              
                 journal = "",                #articles published in journal
                 year_start = "",             #articles published since
                 year_finish = "",            #articles published till   
                 search_domain = "1.",        #Search in all subject areas: as_sdt= "1."
                                              #Search articles in the subject areas: as_sdt= "1" + subjects
                 include_patents = "on",      
                 subjects = "",               #works only if search_domain = "1"
                                              #string bio /med /bus /phy /chm /soc /eng (or  " bio med bus")
                 no_citation = "0",           #1=at least summaries 0=include citations      
            
                 start_from = 0,              #start from # result
                 citationsID = None,                #search within articles citing "#"
                 relatedArticles = None,  #create a relatedArticles link for parsing
                 allVersions = None,       #create allVersions link for parsing
                 bibTex = None,            # create bibTex link for getHTML
                 citesArticleName = ""                   
                 ):
        
        self.keywords = urllib.quote_plus(keywords)
        self.exact_phrase = urllib.quote_plus(exact_phrase)   
        self.without_the_words = urllib.quote_plus(without_the_words)
        self.one_of_the_words = urllib.quote_plus(one_of_the_words)
        self.occurence = occurence
        self.num_of_results = num_of_results              
        self.author = urllib.quote_plus(author)                              
        self.journal = urllib.quote_plus(journal)
        self.year_start = year_start            
        self.year_finish = year_finish                       
        self.search_domain = search_domain                                                        
        self.include_patents = include_patents      
        self.subjects = subjects                
        self.no_citation = no_citation 
        self.start_from = start_from   
        self.citationsID = citationsID 
        self.relatedArticles = relatedArticles
        self.allVersions = allVersions
        self.bibTex = bibTex
        self.citesArticleName = citesArticleName
                      
    def updateStartFrom(self, start_from):
        self.start_from = start_from    
        
    def updateNumOfResults(self, num):
        self.num_of_results = num
    
    def updateYearStart(self, year):
        self.year_start = str(year)

# TODO: change this thing
    def __str__(self):
        msg = "Keywords: " + str(self.keywords)
        return msg
    
    def constructURL(self):
            
        url = "http://scholar.google.com/scholar?"
        
                        
        urlParametrs = {"as_q":self.keywords, "num":self.num_of_results,
                        "as_epq":self.exact_phrase, "as_oq":self.one_of_the_words, "as_eq":self.without_the_words,
                        "as_occt":self.occurence,"as_sauthors":self.author, "as_publication":self.journal,
                        "as_ylo":self.year_start,"as_yhi":self.year_finish,"as_sdt": self.search_domain,
                        "as_sdtp":self.include_patents, "as_subj":self.subjects, "as_vis":self.no_citation,
                         "start":self.start_from, "btnG":"Search+Scholar", "hl":"en"}    
       
        #replace " " by "+" in strings containing more than one word 
        for k, v in urlParametrs.items():
            if type(v) == str and str.count(v," ") != 0:
                urlParametrs[k] = v.replace(" ", "+") 
 
        #add cites=# if the search is within articles citing #
        if self.citationsID != None:
            urlParametrs.update({"cites":self.citationsID})
            urlParametrs["sciodt"]=2000
            urlParametrs["scipsc"]=1
            
        
        if self.relatedArticles != None:
            tempStr = "related:" + str(self.relatedArticles) + ":scholar.google.com/"
            urlParametrs.update({"as_q": tempStr})
                   
        if self.bibTex != None:
            tempStr = "info:" + str(self.bibTex) + ":scholar.google.com/&output=citation"
            urlParametrs.update({"as_q": tempStr})
        
        if self.allVersions != None:
            urlParametrs.update({"cluster": self.allVersions})
                   
                        
             
        url += "&".join(["%s=%s" % (k, v) for k, v in urlParametrs.items()])
        
        # anonymize link
        #url = "http://anonymouse.org/cgi-bin/anon-www.cgi/" + url
          
        return url
    