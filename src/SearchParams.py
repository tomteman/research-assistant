#
# keywords: q=
# number of results: num=10,
# exact phrase: as_epq="",
# at least one of the words: as_oq="",
# within the words: as_eq="",
# where the words occur:  as_occt = any/title,
# author: as_sauthors="",
# publication: as_publication="",
# since year: as_ylo="",
# till year: as_yhi="",
# as_sdt=
#    Search articles in all subject areas: as_sdt= "1."
#          including patents: as_sdtp="on",
#    Search only articles in the following subject areas: as_sdt= "1" + 
#          subjects: as_subj= bio /med /bus /phy /chm /soc /eng (or &)
#    Search all legal opinions and journals.  as_sdt=  "2"
#    Search only US federal court opinions. as_sdt= "3"                        
#    Search only court opinions from the following states:   as_sdt = "4", + states = as_stds = "1" / "51"
# including citation as_vis=0 / at least summaries as_vis=1
# btnG=Search+Scholar",
# hl="en"
#
#
# citations: "cites":
#
# start

class SearchParams:
    def __init__(self,
                 keywords = "",               #search keywords
                 all_words = "",       #all of the the words 
                 exact_phrase = "",           #search for exact keywords 
                 one_of_the_words = "",       #search for at least one word
                 within_the_words = "",       #search within the words
                 occurence = "any",           #where the words occur: any/title 
                 num_of_results = 10,         #number of results per page
                 author = "",                 #author              
                 journal = "",                #publication
                 year_start = "",             #articles since
                 year_finish = "",            #articles till   
                 search_domain = "1.",        #Search in all subject areas: as_sdt= "1."
                                              #Search articles in the subject areas: as_sdt= "1" + subjects
                 include_patents = "on",      
                 subjects ="",                #string bio /med /bus /phy /chm /soc /eng (or  " bio med bus")
                 no_citation = "1",           #1=at least summaries 0=include citations      
            
                 start_from = 0,              #start from # result
                 cites = None                 #search within articles citing "#"                 
                 ):
        
        self.keywords = keywords
        self.all_words = all_words
        self.exact_phrase = exact_phrase   
        self.one_of_the_words = one_of_the_words 
        self.within_the_words = within_the_words
        self.occurence = occurence
        self.num_of_results = num_of_results              
        self.author = author                              
        self.journal = journal
        self.year_start = year_start            
        self.year_finish = year_finish                       
        self.search_domain = search_domain                                                        
        self.include_patents = include_patents      
        self.subjects = subjects                
        self.no_citation = no_citation 
        self.start_from = start_from   
        self.cites = cites 
        
                      
    def updateStartFrom(self, start_from):
        self.start_from = start_from    


# TODO: change this thing
    def __str__(self):
        msg = "Keywords: " + str(self.keywords)
        return msg
    
    def constructURL(self):
            
        url = "http://scholar.google.com/scholar?"
            
        urlParametrs = {"q":self.keywords, "as_q":self.all_words, "num":self.num_of_results,
                        "as_epq":self.exact_phrase, "as_oq":self.one_of_the_words, "as_eq":self.within_the_words,
                        "as_occt":self.occurence,"as_sauthors":self.author, "as_publication":self.journal,
                        "as_ylo":self.year_start,"as_yhi":self.year_finish,"as_sdt": self.search_domain,
                        "as_sdtp":self.include_patents, "as_subj":self.subjects, "as_vis":self.no_citation,
                         "start":self.start_from, "btnG":"Search+Scholar", "hl":"en"}    
       
        #replace " " by "+" in strings containing more than one word 
        for k, v in urlParametrs.items():
            if type(v) == str and str.count(v," ") != 0:
                urlParametrs[k] = v.replace(" ", "+") 
 
        #add cites=# if the search is within articles citing #
        if self.cites != None:
            urlParametrs.update({"cites":self.cites})           
                        
        url += "&".join(["%s=%s" % (k, v) for k, v in urlParametrs.items()])
          
        return url
     
    