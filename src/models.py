
from google.appengine.ext import db
from google.appengine.ext.db import djangoforms

class Item(db.Model):
    name = db.StringProperty()
    quantity = db.IntegerProperty(default=1)
    target_price = db.FloatProperty()
    priority = db.StringProperty(default='Medium',choices=[
      'High', 'Medium', 'Low'])
    entry_time = db.DateTimeProperty(auto_now_add=True)
    added_by = db.UserProperty()
    
class ItemForm(djangoforms.ModelForm):
    class Meta:
        model = Item
        exclude = ['added_by']    