import os
import sys
sys.path.append("/home/pablo/metref")
print(sys.path)
import subprocess
import django 
import pandas as pd

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "metref.settings")
django.setup()

from django.core.files import File
from taxonomy.models import Genome
from taxonomy.models import Version
from taxonomy.models import Taxon

initial_version = Version.objects.get(pk=1)

df = pd.read_csv("../data/assembly_summary_refseq_dic_2023.txt", sep="\t", usecols=[0,4,5,11,19,20,24], header=None, names=["accession", "category", "taxid", "level", "path", "excluded","group"], dtype={'accession':str,'category':str,'taxid':str,'level':str,'excluded':str,'path':str,'group':str}, skiprows=2)
df = df[(df["category"] == "reference genome") | (df["category"] == "representative genome")]
df = df[(df["excluded"] == "na")]
df = df.drop("excluded", axis=1)
df = df[(df["level"] == "Chromosome") | (df["level"] == "Complete Genome")]
df = df[~((df["group"] == "na") | (df["group"] == "viral"))]
df["path"] =df["path"].apply(lambda x: x + "/" + x.split("/")[-1] + "_genomic.fna.gz")
print(len(df))
""" for ind in df.index:
    subprocess.run(["rsync", "-r", "--times", "--verbose", df['path'][ind].replace("https", "rsync"), "../data/genomes/"])

df["path"] = "data/genomes/"+df["path"].apply(lambda x: x.split("/")[-1])

for ind in df.index:
    with open (df["path"][ind], 'rb') as f:
        g=Genome(accession=df["accession"][ind],taxon=Taxon.objects.get(pk=df["taxid"][ind]),assembly_level=df["level"][ind],group=df["group"][ind],category=df["category"][ind])
        g.file = os.path.join('',df["path"][ind])
        g.save()
        g.version.add(initial_version) """
