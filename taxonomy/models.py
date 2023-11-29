from django.db import models

class Taxonomy(models.Model):
    tax_id = models.PositiveIntegerField(default=0)
    parent_tax_id = models.PositiveIntegerField(default=0)
    name = models.CharField(max_length=200, default='')
    unique_name = models.CharField(max_length=200, default='')
    rank = models.CharField(max_length=200, default='')
    version = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = "taxonomy"