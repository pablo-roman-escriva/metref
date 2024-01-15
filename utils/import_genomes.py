import os
import sys
sys.path.append("/home/pablo/metref")
print(sys.path)
import subprocess
import django 
import pandas as pd

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "metref.settings")
django.setup()

from taxonomy.models import Genome
from taxonomy.models import Version

initial_version = Version.objects.get(pk=1)

df = pd.read_csv("data/assembly_summary_refseq_dic_2023.txt", sep="\t", usecols=[0,4,5,11,19,20], header=None, names=["accession", "category", "taxid", "level", "path", "excluded"], dtype={'accession':str,'category':str,'taxid':str,'level':str,'excluded':str,'path':str}, skiprows=2)
df = df[(df["category"] == "reference genome") | (df["category"] == "representative genome")]
df = df[(df["excluded"] == "na")]
df = df.drop("excluded", axis=1)
df = df[(df["level"] == "Chromosome") | (df["category"] == "Complete Genome")]
df["path"] =df["path"].apply(lambda x: x + "/" + x.split("/")[-1] + "_genomic.fna.gz")

#for ind in df.index:
#    subprocess.run(["rsync", "-r", "--times", "--verbose", df['path'][ind].replace("https", "rsync"), "data/genomes/"])

