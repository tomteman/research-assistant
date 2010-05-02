from bibtexParser import parser
from getHTML import getHTML

class ArticleData:
    def __init__(self):
        self.key = ""
        self.HTML_urlList = [] # list of ArticleURLandTitle objects
        self.BibTexURL = ""
        self.BibTex_dict = {}
        self.citationsURL = ""
        self.related_articlesURL = ""
        self.all_versionsURL = ""
        self.cacheURL = ""
        self.HTML_author_year_pub = ""
        self.HTML_abstract = ""
        

    def get_key(self):
        return self.key
    
    def get_bib_tex_url(self):
        return self.BibTexURL


    def get_bib_tex_dictionary(self):
        return self.BibTex_dict
 
    
    def get_HTML_urlList(self):
        return self.HTML_urlList


    def get_citations_url(self):
        return self.citationsURL


    def get_related_articles_url(self):
        return self.related_articlesURL
    
    
    def get_all_versions_url(self):
        return self.all_versionsURL
    
    
    def get_HTML_author_year_pub(self):
        return self.HTML_author_year_pub
    
    
    def get_HTML_abstract(self):
        return self.HTML_abstract
    
    
    def set_key(self, value):
        self.key = value
        
        
    def set_bib_tex_url(self, value):
        self.BibTexURL = value


    def set_bib_tex_dict(self, value):
        self.BibTex_dict = value


    def set_HTML_urlList(self, value):
        self.HTML_urlList = value


    def set_citations_url(self, value):
        self.citationsURL = value


    def set_related_articles_url(self, value):
        self.related_articlesURL = value


    def set_all_versions_url(self, value):
        self.all_versionsURL = value
        
    def set_cache_url(self, value):
        self.cacheURL = value
    
    
    def set_HTML_author_year_pub(self, value):
        self.HTML_author_year_pub = value
    
    
    def set_HTML_abstract(self, value):
        self.HTML_abstract = value
        
    def add_item_to_HTML_urlList(self, value):
        self.HTML_urlList.append(value)

# ----------------- handling BibTex Dictionary Data ----------------------
 
    # bibtex_key: A hidden field used for specifying or overriding the alphabetical order of entries (when the "author" and "editor" fields are missing). Note that this is very different from the key (mentioned just after this list) that is used to cite or cross-reference the entry.
    # address: Publisher's address (usually just the city, but can be the full address for lesser-known publishers)
    # annote: An annotation for annotated bibliography styles (not typical)
    # author: The name(s) of the author(s) (in the case of more than one author, separated by and)
    # booktitle: The title of the book, if only part of it is being cited
    # chapter: The chapter number
    # crossref: The key of the cross-referenced entry
    # edition: The edition of a book, long form (such as "first" or "second")
    # editor: The name(s) of the editor(s)
    # eprint: A specification of an electronic publication, often a preprint or a technical report
    # howpublished: How it was published, if the publishing method is nonstandard
    # institution: The institution that was involved in the publishing, but not necessarily the publisher
    # journal: The journal or magazine the work was published in 
    # month: The month of publication (or, if unpublished, the month of creation)
    # note: Miscellaneous extra information
    # number: The "number" of a journal, magazine, or tech-report, if applicable. (Most publications have a "volume", but no "number" field.)
    # organization: The conference sponsor
    # pages: Page numbers, separated either by commas or double-hyphens.
    # publisher: The publisher's name
    # school: The school where the thesis was written
    # series: The series of books the book was published in (e.g. "The Hardy Boys" or "Lecture Notes in Computer Science")
    # title: The title of the work
    # type: The type of tech-report, for example, "Research Note"
    # url: The WWW address
    # volume: The volume of a journal or multi-volume book
    # year: The year of publication (or, if unpublished, the year of creation)
 
    def get_article_title(self):
        return self.get_field_name("title")
 
 
    def get_address(self):
        return self.get_field_name("address")


    def get_annote(self):
        return self.get_field_name("annote")


    def get_author(self):
        return self.get_field_name("author")


    def get_booktitle(self):
        return self.get_field_name("booktitle")


    def get_chapter(self):
        return self.get_field_name("chapter")


    def get_crossref(self):
        return self.get_field_name("crossref")


    def get_edition(self):
        return self.get_field_name("edition")


    def get_editor(self):
        return self.get_field_name("editor")


    def get_eprint(self):
        return self.get_field_name("eprint")


    def get_howpublished(self):
        return self.get_field_name("howpublished")


    def get_institution(self):
        return self.get_field_name("institution")


    def get_journal(self):
        return self.get_field_name("journal")


    def get_bibtex_key(self):
        return self.BibTex_fields.keys()[0]


    def get_month(self):
        return self.get_field_name("month")


    def get_note(self):
        return self.get_field_name("note")


    def get_number(self):
        return self.get_field_name("number")


    def get_organization(self):
        return self.get_field_name("organization")


    def get_pages(self):
        return self.get_field_name("pages")


    def get_publisher(self):
        return self.get_field_name("publisher")


    def get_school(self):
        return self.get_field_name("school")


    def get_series(self):
        return self.get_field_name("series")


    def get_type(self):
        return self.get_field_name("type")


    def get_url(self):
        return self.get_field_name("url")


    def get_volume(self):
        return self.get_field_name("volume")


    def get_year(self):
        return self.get_field_name("year")
    
  
  
 # ----------------- END OF handling BibTex Dictionary Data ----------------------

 #TODO: change this function to do it nicely and 
    def __str__(self):
        msg =  "key: " + self.get_key() + "\n"
        for articleTitleAndURL in self.get_HTML_urlList():
            msg = msg +  "Article title: " + articleTitleAndURL.get_article_title() + "\n"
            if articleTitleAndURL.get_has_link():
                msg = msg + "Article URL: " + articleTitleAndURL.get_article_url() + "\n"
            else:
                msg = msg + "[CITATION]" + "\n"
        msg = msg +  "Green text: " + self.get_HTML_author_year_pub() + "\n"
        msg = msg +  "Abstract: " + self.get_HTML_abstract() + "\n"
        msg = msg + "-------------------------------------------------\n"
        msg = msg +  "BibTex URL: " + self.get_bib_tex_url() + "\n"
        msg = msg +  "Citations URL: " + self.get_citations_url() + "\n"
        msg = msg +  "Related Articles URL: " + self.get_related_articles_url() + "\n"
        msg = msg +  "All Versions URL: " + self.get_all_versions_url() + "\n"
        msg = msg + "==-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-==\n"
        return msg

    def addURLto_HTML_urlList(self, url):
        self.HTML_urlList.append(url)
        
    def printArticle(self):
        print "key: " + self.key
        print "BibTex URL: " + self.BibTexURL
        print "____BibTex Data:____"
        self.BibTex_data.print_bibtex_items()
        for url in self.HTML_urlList:
            print "Article URL: " + url.get_article_url()
        
        print "Citations URL: " + self.citationsURL
        print "Related Articles URL: " + self.related_articlesURL
        print "All Versions URL: " + self.all_versionsURL
    
    def get_field_name(self, fieldname):
        # if the dictionary is empty - get the values from the BibTexURL (HTML request)
        if (len(self.BibTex_dict)) == 0:
            self.BibTex_dict = parseBibTexItems(self.key)
        values = self.BibTex_dict.values()[0]
        #return the value of the requested fieldname
        return values.get(fieldname)
        
def parseBibTexItems(bibtexID):
    # get the BibTex HTML
    bibtexHTML = getHTML(createBibTexURL(bibtexID))
    bibtexHTML.getHTMLfromURL()
    
    HTML = bibtexHTML.get_html()
    
    # parse the BibTex HTML into a dictionary and return it
    return (parser.parse_string(HTML, 0))

def createBibTexURL(bibtexID):
    return "http://scholar.google.com/scholar.bib?q=info:" + str(bibtexID) + ":scholar.google.com/&output=citation&hl=en&as_sdt=2000&ct=citation&cd=0"
    


