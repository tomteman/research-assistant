import cgi
import os

from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

import datetime

import SearchParams
import Follow
from ArticleData import Article

class FollowFormDone(webapp.RequestHandler):
    def post(self):
        self.response.out.write("""<html>
                                <head><title>Done Filling Follow Form </title></head>
                                <body><b>Thank you for sending the follow!</b><br><br>
                                We Will Soon send you some interesting updates!</body></html>""")

        forms = ("follow_name","regular_update","ch_keywords","keywords",
                 "ch_all_words","all_words","ch_exact_phrase", "exact_phrase",
                  "ch_within_the_words","within_the_words", "ch_author", "author",
                  "ch_journal", "journal","ch_one_of_the_words","one_of_the_words",
                 "citation_update","ch_citing", "citing", "ch_keywords_citing",
                 "keywords_citing", "update_frequency" )
        
       
        vars = {}
        for form in forms:
            vars[form] = self.request.get(form)
           
        keywords = vars["keywords"] if vars['ch_keywords'] =="on" else ""
        #all_words = vars["all_words"] if vars['ch_all_words'] == "on" else "" 
        exact_phrase = vars["exact_phrase"] if vars["ch_exact_phrase"] == "on" else "" 
        one_of_the_words = vars["one_of_the_words"] if vars["ch_one_of_the_words"] == "on" else ""
        within_the_words = vars["within_the_words"] if vars["within_the_words"] == "on" else ""
        author = vars["author"] if vars["ch_author"] else ""              
        journal = vars["journal"] if vars["ch_journal"] else ""
        
        #cites_param = cites if cites!=None else ""
        
        
               
        s_params = SearchParams.SearchParams(keywords = keywords,
                                            exact_phrase = exact_phrase, one_of_the_words=one_of_the_words,
                                            within_the_words=within_the_words, author=author, journal=journal)
                                            #cites = sites_param)
        
        first_created = lambda x: datetime.datetime.strptime(x, '%m/%d/%Y').date()

        follow = Follow.Follow( username = "", follow_name = vars["follow_name"], search_params=s_params, 
                                update_frequency = vars["update_frequency"],
                                num_of_updates = 0, num_of_successful_updates = 0,url=None)
          #       first_created = first_created, last_updated = "", pastResultsDict="", url = None)
        
        
        db_follow = follow.convert2DBFollow()
        #db_follow.put()
      
        # TODO: change this thing. It is not supposed to be here
        #follow.update_follow()
        #follow.put()
        
#        self.response.out.write("""<html>
#                                <head><title>Done Filling Follow Form </title></head>
#                                <body>Thank you for sending the follow! 
#                                We Will Soon send you some interesting updates!</body></html>""")
#
#        forms = ("follow_name","regular_update","ch_keywords","keywords",
#                 "ch_all_words","all_words","ch_exact_phrase", "ch_within_words",
#                 "within_words", "ch_author", "author", "ch_journal", "journal",
#                 "citation_update","ch_citing", "citing", "ch_keywords_citing",
#                 "keywords_citing", "update_frequency" )
#        
#        #self.request.get('article_lea')
#        #self.response.out.write(str('article_lea'))
#        vars = {}
#        for form in forms:
#            vars[form] = self.request.get(form)
#        
#        s_params = SearchParams.SearchParams(vars["keywords"])
#        # Fill this object
#        
#       # s_params.set_keywords(vars["keywords"])
#        
#        first_created = lambda x: datetime.datetime.strptime(x, '%m/%d/%Y').date()
#
#        follow = Follow.Follow( username = "", follow_name = vars["follow_name"], search_params=s_params, 
#                 update_frequency = vars["update_frequency"],
#                 num_of_updates = 0, num_of_successful_updates = 0,url=None)
#          #       first_created = first_created, last_updated = "", pastResultsDict="", url = None)
#        
#        
#        db_follow = follow.convert2DBFollow()
#        db_follow.put()
#        # TODO: change this thing. It is not supposed to be here
#        #follow.update_follow()
#        #follow.put()
#          
#        self.response.out.write(str(follow.get_searchParams()))
# 
class FollowForm (webapp.RequestHandler):

    def __init__(self):
        self.title = "create a new follow"
        self.heading = "create a new follow" 
    
        

    def get(self, article_title, article_year_start): 
        
        s_params = SearchParams.SearchParams()
        s_params.year_start = article_year_start
        s_params.title = article_title
        
        self.response.out.write(self.generateHead() + self.generateBody(s_params, article_title) 
                                + (self.generateTrailer()))  
        
        
    def generateHead(self ):
        str_head = "<html>\n"
        str_head +="<head>\n"
        str_head += "<title>" + self.title + "</title>\n"
        str_head += "</head>\n"
        str_head += "<h1 align=center>" + self.heading + "</h1>\n"
        return str_head
        
        
    def generateBody(self,s_params,article_title):
        
        strBody = "<body>\n"
        strBody += """<form action="/FollowFormDone" method="post" name = "follow_form">\n"""
        
        strBody += self.generateTextBox( text="Name this follow", inner_text = "new follow", name="follow_name" ) 
        strBody += "</br>"
        
        strBody += "<input type=\"radio\" name=\"regular_update\" value=\"1\" />"
        strBody += "Notify me on new article:" + "</br>"

        strBody += "</br>"
        strBody += "<ul>\n"
        
        strBody += "<table>"

        #with same keywords
        strColumn1 = self.generateCheckBox(name="ch_keywords", value="on", text="with keywords:")
        strColumn2 = self.generateTextBox( inner_text = s_params.keywords, name = "keywords" )
        strBody += self.generateTableLine(strColumn1, strColumn2)
  
        #with all off the words 
        strColumn1 = self.generateCheckBox(name="ch_all_words", text="with all of the words:")
        strColumn2 = self.generateTextBox( inner_text = s_params.keywords, name = "all_words" )
        strBody += self.generateTableLine(strColumn1, strColumn2)
          
        
        #with exactly phrase
        strColumn1 = self.generateCheckBox(name="ch_exact_phrase", text="with exact phrase:")
        strColumn2 = self.generateTextBox( inner_text = s_params.exact_phrase, name = "exact_phrase" )
        strBody += self.generateTableLine(strColumn1, strColumn2)
          
        #within the words
        strColumn1 = self.generateCheckBox(name="ch_within_words", text="with keywords within the words:")
        strColumn2 = self.generateTextBox( inner_text = s_params.within_the_words, name = "within_words" )
        strBody += self.generateTableLine(strColumn1, strColumn2)
        
        #new from author
        strColumn1 = self.generateCheckBox(name="ch_author", text="written by (author):")
        strColumn2 = self.generateTextBox( inner_text = s_params.author, name="author" )
        strBody += self.generateTableLine(strColumn1, strColumn2)
        
        #journal    
        strColumn1 = self.generateCheckBox(name="ch_journal", text="published in (journal):")
        strColumn2 = self.generateTextBox( inner_text = s_params.journal, name = "journal" )
        strBody += self.generateTableLine(strColumn1, strColumn2)
        
        strBody += "</table>"
        strBody += "</ul>\n"
        
        ##################################
    #   strBody += self.generateCheckBox(name="keywords", text="Notify me about:"))
        strBody += "<input type=\"radio\" name=\"citation_update\" value=\"2\" />"
        strBody += "Notify me on:" + "</br>"
        strBody += "</br>"
        
        strBody += "<ul>\n"
        strBody += "<table>\n"
        ############TODO
        strColumn1 = self.generateCheckBox(name="ch_citing", text="new article citing:")
    ##########TODO - article    
        strColumn2 = self.generateTextBox( inner_text =  article_title, name="citing")
        strBody += self.generateTableLine(strColumn1, strColumn2)
        
        strColumn1 = self.generateCheckBox(name="ch_keywords_citing", text="with keywords:")
        strColumn2 = self.generateTextBox( inner_text = s_params.keywords, name = "keywords_citing" )
        strBody += self.generateTableLine(strColumn1, strColumn2)
        
        strBody += "</table>\n"
        strBody += "</ul>\n"
        
        #define update frequency
        strBody += self.generateSelect(name = "update_frequency", text="send me update once a ",
                                         options = ("week", "day","2 weeks"))
        strBody += "</br>"
        strBody += "</br>"
        
        #submit button
        strBody += "<input type="+"\"submit\"" +"value="+"\" Submit\" />\n"
        strBody += "</br>"
        
        strBody += "</form>\n"
        strBody += "</body>\n"
    
        
        return strBody

            
    def generateTableLine(self, column1, column2):
        strTableLine =  "<tr>\n"
        strTableLine += "<td>" + str(column1) + "</td>" + "\n"
        strTableLine += "<td>" + str(column2) + "</td>" + "\n"
        strTableLine += "</tr>\n"
        return strTableLine
        
             
            
    def generateTextBox(self, name="", width=30, rows=1, text = "", inner_text="" ):  
        strTextBox = text 
        strTextBox += "<textarea name= \""+ name + "\"  cols= \"%d\" rows= \"%d\">"  %(width, rows)
        strTextBox += inner_text
        strTextBox += "</textarea><br>\n"
        return strTextBox
        
 
    def generateCheckBox(self, name = "", text="", value="off"):
        strCheckBox = "<input type=\"checkbox\" value=\"" + value+ "\" name= \""+ name + "\" />\n"
        strCheckBox += text
        return strCheckBox   
    
    def generateSelect(self, options, name="", text=""):
        strSelect = text + "\n"
        strSelect += "<select name= \""+ name + "\">\n"
        for option in options:
            strSelect += "<option>" + option + "</option>\n" 
        strSelect += "</select>\n"
        return strSelect    
              
              
    def generateTrailer(self ):
        strTrailer = "</body>\n"   
        strTrailer += "</html>\n"
        return strTrailer

    # This is what runs when Submit is pressed on the full FollowForm
    def postFollow(self):
            pass
#if __name__ == "__main__":  
 #   follow = FollowForm( )