from django import forms
from .models import Study
from taxonomy.models import Version, Taxon
from django_select2 import forms as s2forms
from dal import autocomplete
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class VersionWidget(s2forms.Select2Widget):
    search_fields = [
        "name__icontains",
    ]

""" class TaxonWidget(s2forms.Select2MultipleWidget):
    search_fields = [
        "name__icontains",
        "rank__icontains",
    ]
    dependent_fields={'version': 'version'}
 """
class StudyForm(forms.ModelForm):
    class Meta:
        model = Study
        fields = ["title", "version", "taxon"]
        widgets = {
            "version" : VersionWidget,
            "taxon" : autocomplete.ModelSelect2Multiple(url="taxon-autocomplete", forward=['version']),
        }
    def __init__(self, *args, **kwargs):
        super(StudyForm, self).__init__(*args, **kwargs)
        self.fields['version'].queryset = Version.objects.filter(status=1).order_by("-version_id")

    class Media:
        js = ['js/form_study.js']

    def clean(self):
        cleaned_data = super().clean()
        version = cleaned_data.get("version")
        taxa = cleaned_data.get("taxon")
        taxa_children = []
        if version and taxa:
            if (len(taxa) > 6):
               raise ValidationError(_("The number of taxa cannot be greater than six."),code="invalid") 
            for taxon_form in taxa: 
                taxa_parents = []
                # Primero, se comprueba si el taxon que se quiere insertar, ya es descendiente de otro taxon que ya se ha insertado. 
                # Se comprueba si está en taxa_children 
                if taxon_form in taxa_children:
                    raise ValidationError(_("%(taxon)s has ancestor/descendant relationship with another provided taxon."),code="invalid",params={"taxon": taxon_form},)
                # Si no se encuentra, se recuperan todos los taxones descendientes de ese tax_id y se añaden a new_taxa_children
                taxa_for_loop = list(Taxon.objects.filter(parent_tax_id=taxon_form.tax_id, version = version))
                new_taxa_children = list(Taxon.objects.filter(parent_tax_id=taxon_form.tax_id, version = version))
                taxa_pre_loop = []
                while True:
                    if not taxa_for_loop:
                        break
                    else:
                        for parent_tax in taxa_for_loop: 
                            taxa_list = Taxon.objects.filter(parent_tax_id=parent_tax.tax_id, version = version)
                            for taxon in taxa_list:
                                new_taxa_children.append(taxon)
                                taxa_pre_loop.append(taxon)
                        taxa_for_loop = taxa_pre_loop
                        taxa_pre_loop = []
                # Se comprueba para cada uno de estos taxones descendientes, si ya está en la selección. 
                for new_taxon in new_taxa_children: 
                    if new_taxon in taxa: 
                        raise ValidationError(_("%(taxon)s has ancestor/descendant relationship with another provided taxon."),code="invalid",params={"taxon": taxon_form},)
                taxa_children.append(new_taxa_children)
                #make loop 
                # Por último, se recuperaran todos los taxones ascendentes de ese taxon y se compara si están en la selección. 
                if (taxon_form.tax_id != 1):
                    taxa_for_loop = Taxon.objects.get(tax_id=taxon_form.parent_tax_id, version=version)
                    taxa_parents = []
                    taxa_parents.append(Taxon.objects.get(tax_id=taxon_form.parent_tax_id, version=version))
                    while True:
                        if not taxa_for_loop:
                            break
                        else: 
                            if (taxa_for_loop.tax_id != 1):
                                new_taxon = Taxon.objects.get(tax_id=taxa_for_loop.parent_tax_id, version = version)
                                taxa_parents.append(new_taxon)
                                taxa_for_loop = new_taxon
                            else: 
                                taxa_for_loop = []
                    for new_parent_taxon in taxa_parents: 
                        if new_parent_taxon in taxa: 
                            raise ValidationError(_("%(taxon)s has ancestor/descendant relationship with another provided taxon."),code="invalid",params={"taxon": taxon_form},)
