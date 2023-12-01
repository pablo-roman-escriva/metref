from django.db import models

class Version(models.Model):
    name = models.CharField(max_length=200,default='')
    date = models.DateField()
    status = models.PositiveSmallIntegerField(default=1)

class Taxon(models.Model):
    tax_id = models.PositiveIntegerField(default=0, primary_key=True)
    parent_tax_id = models.PositiveIntegerField(default=0)
    name = models.CharField(max_length=200, default='')
    unique_name = models.CharField(max_length=200, default='')
    rank = models.CharField(max_length=200, default='')
    version = models.ManyToManyField(Version)

