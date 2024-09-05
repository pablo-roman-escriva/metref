from django.contrib import admin
from .models import Entry, Category
from django.forms import Textarea
from django.db import models
from tinymce.widgets import TinyMCE

# Register your models here.
class entryAdmin(admin.ModelAdmin):
    formfield_overrides = { 
    models.TextField: {'widget': TinyMCE()} #optional, set Textarea attributes `attrs={'rows':2, 'cols':8}`
    }

admin.site.register(Category)
admin.site.register(Entry, entryAdmin)

#Establish a textarea, a plain textarea, as a the TextField in Django