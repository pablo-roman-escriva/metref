import os
import sys
sys.path.append("/home/pablo/metref")
print(sys.path)
import subprocess
import django 
import pandas as pd

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "metref.settings")
django.setup()
from django.conf import settings
from django.core.files import File
from taxonomy.models import Genome
from taxonomy.models import Version
from taxonomy.models import Taxon
from taxonomy.models import Traits

import subprocess
import csv

BASE_URL = settings.PROJECT_ROOT
initial_version = Version.objects.get(pk=1)

df = pd.read_csv(BASE_URL+"/data/assembly_summary_refseq_dic_2023.txt", sep="\t", usecols=[0,4,5,11,19,20,24,25,27,34,35,36], header=None, names=["accession", "category", "taxid", "level", "path", "excluded","group", "genome_size", "gc_percent", "total_gene_count", "protein_coding_gene_count", "non_coding_gene_count"], dtype={'accession':str,'category':str,'taxid':str,'level':str,'excluded':str,'path':str,'group':str,'total_gene_count':str,'protein_coding_gene_count':str,'non_coding_gene_count':str, 'gc_percent':str, 'genome_size':str}, skiprows=2)
df = df[(df["category"] == "reference genome") | (df["category"] == "representative genome")]
df = df[(df["excluded"] == "na")]
df = df.drop("excluded", axis=1)
df = df[(df["level"] == "Chromosome") | (df["level"] == "Complete Genome")]
df = df[~((df["group"] == "na") | (df["group"] == "viral"))]
df["path"] =df["path"].apply(lambda x: x + "/" + x.split("/")[-1] + "_genomic.fna.gz")

df_tax = pd.read_csv(BASE_URL+"/data/nodes.dmp", sep="|", usecols=[0,1,2], header=None, names=["tax_id", "parent_tax_id", "rank"])
df_tax = df_tax.replace("\t","", regex=True)

df2_tax = pd.read_csv(BASE_URL+"/data/names.dmp", sep="|", usecols=[0,1,3], header=None, names=["tax_id", "name", "type"])
df2_tax = df2_tax.replace("\t","", regex=True)
df2_tax = df2_tax[df2_tax["type"]=="scientific name"]
df2_tax = df2_tax.drop(columns=["type"])

df3_tax = df_tax.merge(df2_tax)
#print(df3_tax)

#Descarga de los ficheros
#for ind in df.index:
 #   subprocess.run(["rsync", "-r", "--times", "--verbose", df['path'][ind].replace("https", "rsync"), BASE_URL+"/data/genomes/"])

#Restructurar path para guardado
df["path"] = "data/genomes/"+df["path"].apply(lambda x: x.split("/")[-1])

# Código para añadir el nuevo taxa o combinación de sus campos, si no existe. 
for ind in df.index:
    tax_id = df["taxid"][ind]
    tax_data = df3_tax[df3_tax["tax_id"]==int(tax_id)]
    if not Taxon.objects.filter(tax_id=tax_data["tax_id"].iloc[0], parent_tax_id = tax_data["parent_tax_id"].iloc[0], rank=tax_data["rank"].iloc[0], name = tax_data["name"].iloc[0]).exists():
        # Si no existe, crea el nuevo taxa, lo guarda y actualiza su versión.
        #print("",end="")
        taxa = Taxon(tax_id=tax_data["tax_id"].iloc[0], parent_tax_id = tax_data["parent_tax_id"].iloc[0], rank=tax_data["rank"].iloc[0], name = tax_data["name"].iloc[0])
        taxa.save()
        taxa.version.add(initial_version)
    else:
        print("exists")
        taxa = Taxon.objects.get(tax_id=tax_data["tax_id"].iloc[0], parent_tax_id = tax_data["parent_tax_id"].iloc[0], rank=tax_data["rank"].iloc[0], name = tax_data["name"].iloc[0])
    taxa2 = taxa 
    while (taxa2.tax_id != 1) :
        parent_taxa_info = df3_tax[df3_tax["tax_id"] == taxa2.parent_tax_id]
        if not Taxon.objects.filter(tax_id=parent_taxa_info["tax_id"].iloc[0], parent_tax_id=parent_taxa_info["parent_tax_id"].iloc[0], name=parent_taxa_info["name"].iloc[0], rank = parent_taxa_info["rank"].iloc[0]).exists(): 
            taxa2 = Taxon(tax_id=parent_taxa_info['tax_id'].iloc[0],parent_tax_id=parent_taxa_info['parent_tax_id'].iloc[0],rank=parent_taxa_info['rank'].iloc[0],name=parent_taxa_info['name'].iloc[0])  
            taxa2.save()
            taxa2.version.add(initial_version) 
        else:
            taxa2 = Taxon.objects.get(tax_id=parent_taxa_info["tax_id"].iloc[0], parent_tax_id=parent_taxa_info["parent_tax_id"].iloc[0], name=parent_taxa_info["name"].iloc[0], rank = parent_taxa_info["rank"].iloc[0])
            taxa2.version.add(initial_version)   


    genome = Genome.objects.get(accession=df["accession"][ind])
    genome.taxon = taxa
    genome.save(update_fields=["taxon"])

    # if not Genome.objects.filter(accession=df["accession"][ind]).exists():
    #     g=Genome(accession=df["accession"][ind],taxon=taxa,assembly_level=df["level"][ind],group=df["group"][ind],category=df["category"][ind])
    #     g.file = os.path.join('',df["path"][ind])
    #     if os.getcwd() != BASE_URL + "/utils":
    #         os.chdir("utils")
    #     subprocess.run([BASE_URL + "/utils/gs.sh", "-f", "../" + df["path"][ind]], capture_output=True)
    #     with open("results_gs.csv") as csvfile:
    #         values = csv.reader(csvfile)
    #         next(values)
    #         row1 = next(values)
    #         n_bases = row1[1]
    #         k_gs = row1[2]
    #         entropy = row1[5]
    #         ngs = row1[8]
    #     os.remove('results_gs.csv')
    #     subprocess.run([BASE_URL + "/utils/biobit.sh", "-o", "-f", "../" + df["path"][ind]], capture_output=True)
    #     with open("results_bb.csv") as csvfile:
    #         values = csv.reader(csvfile)
    #         next(values)
    #         row1 = next(values)
    #         k1 = row1[1]
    #         bb = row1[14]
    #         hapax = row1[15]
    #     os.remove("results_bb.csv")
    #     annotated_genes = df["total_gene_count"][ind]
    #     genome_size = df["genome_size"][ind]
    #     gc_percent = df["gc_percent"][ind]
    #     protein_coding_gene_count = df["protein_coding_gene_count"][ind]
    #     non_coding_gene_count = df["non_coding_gene_count"][ind]
    #     t=Traits(genomic_signature=ngs,biobit=bb, genome_size = genome_size, number_acgt_bases = n_bases, annotated_genes = annotated_genes, protein_coding_genes = protein_coding_gene_count, non_coding_genes = non_coding_gene_count, hapaxes = hapax, gc_content = gc_percent, entropy = entropy, k_gs = k_gs, k1_bb = k1 )
    #     t.save()
    #     g.trait = t
    #     g.save()
    #     g.version.add(initial_version)
        
    
    
    




