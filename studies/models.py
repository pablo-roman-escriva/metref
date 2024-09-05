from django.db import models
from taxonomy.models import Version, Taxon, Genome
from django.contrib.auth.models import User
from django.urls import reverse
from .tasks import taxon_to_list
from django.db import transaction
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from metref import settings
# Create your models here.

class Study(models.Model):
    title = models.CharField(max_length=200,default='')
    version = models.ForeignKey(Version, on_delete=models.CASCADE)
    taxon = models.ManyToManyField(Taxon)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def get_absolute_url(self):
        return reverse("study-detail", kwargs={"pk": self.pk})
    
    def save(self, *args, **kwargs):
        super(Study, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.title}"

@receiver(m2m_changed, sender=Study.taxon.through)
def signal(sender, instance, action, reverse, pk_set, **kwargs):
    if action == "post_remove":
        for tax_id in pk_set :
            GenomeList.objects.filter(study=instance, taxon=tax_id).delete()
        
    elif action == "post_add":
        previous_lists = list(GenomeList.objects.filter(study=instance.id).values_list('taxon', flat=True))
        print(previous_lists)
        for taxon in instance.taxon.all():
            print(taxon.id)
            if taxon.id not in previous_lists:
                gl= GenomeList()
                gl.study = instance
                gl.taxon = taxon
                gl.save()
                taxon_to_list.delay(taxon.id, instance.version.id, instance.id, gl.id)

class GenomeList(models.Model):
    study = models.ForeignKey(Study, on_delete=models.CASCADE)
    taxon = models.ForeignKey(Taxon, on_delete=models.CASCADE)
    genomes = models.ManyToManyField(Genome)
    status = models.PositiveSmallIntegerField(default=0)

       