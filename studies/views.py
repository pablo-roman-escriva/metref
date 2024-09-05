from django.shortcuts import render
from django.http import HttpResponse, FileResponse
from django.views.generic import CreateView, DeleteView, UpdateView
from studies.models import Study, GenomeList
from django.urls import reverse_lazy
from django.views.generic import DetailView
from .forms import StudyForm
from dal import autocomplete
from taxonomy.models import Version, Taxon, Genome
from .models import GenomeList
import csv
from django.views.generic.list import ListView

class StudyListView(ListView):
    model = Study
    paginate_by = 10  # if pagination is desired

    def get_queryset(self):
        return Study.objects.filter(user=self.request.user)
    
class StudyCreateView(CreateView):
    model = Study
    form_class = StudyForm

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class StudyUpdateView(UpdateView):
    model = Study
    form_class = StudyForm

class StudyDeleteView(DeleteView):
    model = Study
    success_url = reverse_lazy("study-list")

class StudyDetailView(DetailView):
    model = Study
    template_name = 'study_detail.html'
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        num_items = 0
        num_lists = 0
        num_lists_inactive = 0
        genomeslist = GenomeList.objects.filter(study_id=self.kwargs['pk'])
        lists_inactive = GenomeList.objects.filter(study_id=self.kwargs['pk'],status=0)
        num_lists_inactive = lists_inactive.count()
        num_lists = genomeslist.count()
        num_items = GenomeList.objects.filter(study_id=self.kwargs['pk']).values('genomes').count()
        context["num_items"] = num_items
        context["num_lists"] = num_lists
        context["num_lists_inactive"] = num_lists_inactive
        return context
    
def export_to_csv (request, pk):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename = study_export_'+str(pk)+'.csv'
    writer = csv.writer(response)
    writer.writerow(['accession', "tax_selection", "group", "taxon_name", "taxon_id", "assembly_level","category", "gs", "k_gs", "bb", "k1_bb", "hapaxes", "entropy", "genome_size", "acgt_bases", "gc_content", "annotated_genes", "protein_coding_genes", "non_coding_genes" ])
    genomeslist = GenomeList.objects.filter(study__exact=pk)
    for gl in genomeslist:
        genomes = Genome.objects.filter(pk__in=gl.genomes.all())
        for genome in genomes:
            writer.writerow([genome.accession, gl.taxon.name, genome.group, genome.taxon.name, genome.taxon.tax_id,genome.assembly_level,genome.category,genome.trait.genomic_signature,genome.trait.k_gs, genome.trait.biobit, genome.trait.k1_bb, genome.trait.hapaxes, genome.trait.entropy, genome.trait.genome_size, genome.trait.number_acgt_bases, genome.trait.gc_content, genome.trait.annotated_genes, genome.trait.protein_coding_genes, genome.trait.non_coding_genes ])
    return response

def download_analysis (request, pk):
    import subprocess
    with open("temp/"+str(pk)+'.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['accession', "tax_selection", "group", "taxon_name", "taxon_id", "assembly_level","category", "gs", "k_gs", "bb", "k1_bb", "hapaxes", "entropy", "genome_size", "acgt_bases", "gc_content", "annotated_genes", "protein_coding_genes", "non_coding_genes" ])
        genomeslist = GenomeList.objects.filter(study__exact=pk)
        for gl in genomeslist:
            genomes = Genome.objects.filter(pk__in=gl.genomes.all())
            for genome in genomes:
                writer.writerow([genome.accession, gl.taxon.name, genome.group, genome.taxon.name, genome.taxon.tax_id,genome.assembly_level,genome.category,genome.trait.genomic_signature,genome.trait.k_gs, genome.trait.biobit, genome.trait.k1_bb, genome.trait.hapaxes, genome.trait.entropy, genome.trait.genome_size, genome.trait.number_acgt_bases, genome.trait.gc_content, genome.trait.annotated_genes, genome.trait.protein_coding_genes, genome.trait.non_coding_genes ])
    subprocess.call(["Rscript utils/stats.R " + str(pk)], shell=True)
    return FileResponse(open("temp/study_analysis_"+str(pk)+'.pdf', 'rb'), content_type='application/pdf', as_attachment=True)

class TaxonAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        version = self.forwarded.get("version", None)
        qs = Taxon.objects.all()
        if version:
            qs = qs.filter(version=version).order_by("name")
        else: 
            qs = Taxon.objects.none()
        if self.q:
            qs = qs.filter(name__istartswith=self.q).order_by("name")

        return qs

