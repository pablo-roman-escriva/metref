from django.db import models

class Version(models.Model):
    version_id = models.PositiveIntegerField(default=1)
    name = models.CharField(max_length=200,default='')
    date = models.DateField()
    status = models.PositiveSmallIntegerField(default=1)

    def __str__(self):
        return f"{self.name}"

class Taxon(models.Model):
    tax_id = models.PositiveIntegerField(default=0)
    parent_tax_id = models.PositiveIntegerField(default=0)
    name = models.CharField(max_length=200, default='')
    rank = models.CharField(max_length=200, default='')
    version = models.ManyToManyField(Version)

    def __str__(self):
        return f"{self.name} #{self.rank}"
    
    def children(self):
        return Taxon.objects.filter(parent=self.pk)
    
    def serializable_object(self):
        obj = {'name': self.name, 'children': []}
        for child in self.children():
            obj['children'].append(child.serializable_object())
        return 

class Traits(models.Model):
    genomic_signature = models.FloatField()
    biobit = models.FloatField()
    genome_size = models.PositiveBigIntegerField(default=0)
    number_acgt_bases = models.PositiveBigIntegerField(default=0)
    annotated_genes = models.PositiveIntegerField()
    protein_coding_genes = models.PositiveIntegerField()
    non_coding_genes = models.PositiveIntegerField()
    hapaxes = models.FloatField()
    gc_content = models.FloatField()
    entropy = models.FloatField()
    k_gs = models.SmallIntegerField()
    k1_bb = models.SmallIntegerField() 

class Genome(models.Model):
    accession = models.CharField(unique=True)
    assembly_level = models.CharField(max_length=200, default='')
    category = models.CharField(max_length=200, default='')
    group = models.CharField(max_length=200, default='')
    file = models.FileField(upload_to="data/genomes",default="")
    taxon = models.ForeignKey(Taxon, on_delete=set)
    version = models.ManyToManyField(Version)
    trait = models.ForeignKey(Traits, on_delete=models.DO_NOTHING, default=0)
    
