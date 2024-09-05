from django.db import models

# Create your models here.

class Category(models.Model):
    title = models.CharField(max_length=200)
    order = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return f"{self.title+" ("+str(self.order)+")"}"

class Entry(models.Model):
    title = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null = True)
    text = models.TextField(default="")
    order = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return f"{self.title+" ("+str(self.order)+")"}"
