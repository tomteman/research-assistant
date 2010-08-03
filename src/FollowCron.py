from google.appengine.ext import db
from Follow import Follow, DBFollow
import datetime
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
#from google.appengine.ext.webapp.util import wsgiref
import re
import wsgiref.handlers

# get all follows from DB
query = db.GqlQuery("SELECT * FROM DBFollow")
dbfollows = query.fetch(1000)

class FollowCron(webapp.RequestHandler):
#print "lalalal\n"
    def get(self):
        #print "lalalla\n"
        for dbfollow in dbfollows:
            if (dbfollow.update_frequency == "Daily"):
                if ((datetime.datetime.now() - dbfollow.time_last_updated) > datetime.timedelta(hours=24)):
                    print "updated follow named:" + str(dbfollow.follow_name) + "\n"
                    dbfollow.update_DBfollow()
                    break
             
            if (dbfollow.update_frequency == "Weekly"):
                if ((datetime.datetime.now() - dbfollow.time_last_updated) > datetime.timedelta(days=7)):
                    print "updated follow named:" + str(dbfollow.follow_name) + "\n"
                    dbfollow.update_DBfollow()
                    break
               
            if (dbfollow.update_frequency == "Monthly"):
                if ((datetime.datetime.now() - dbfollow.time_last_updated) > datetime.timedelta(days=30)):
                    print "updated follow named:" + str(dbfollow.follow_name) + "\n"
                    dbfollow.update_DBfollow()
                    break
         
# get first follow which should be updated
# update this follow


application = webapp.WSGIApplication([('/followcron', FollowCron)], 
                                      debug=True)
def main():
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
    main()
