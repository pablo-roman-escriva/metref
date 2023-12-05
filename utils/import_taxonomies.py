import os
import sys
sys.path.append("/home/pablo/metref")
print(sys.path)
import django 
import pandas as pd

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "metref.settings")
django.setup()

from taxonomy.models import Taxon
from taxonomy.models import Version

initial_version = Version.objects.get(pk=1)

""" df = pd.DataFrame(columns=["tax_id", "parent_tax_id", "rank"]) """

df = pd.read_csv("data/nodes.dmp", sep="|", usecols=[0,1,2], header=None, names=["tax_id", "parent_tax_id", "rank"])
df = df.replace("\t","", regex=True)

df2 = pd.read_csv("data/names.dmp", sep="|", usecols=[0,1,3], header=None, names=["tax_id", "name", "type"])
df2 = df2.replace("\t","", regex=True)
df2 = df2[df2["type"]=="scientific name"]
df2 = df2.drop(columns=["type"])
""" df2 = pd.DataFrame(columns=["tax_id", "name"])

with open("data/names.dmp") as names:
    for l in names:
        list = l.split("|")
        if list[3].strip("\t") == "scientific name":
            tax_id = int(list[0].strip("\t"))
            df2.loc[len(df2)] = {'tax_id':tax_id, 'name':list[1].strip("\t")}

print(df2.head()) """   
df3 = df.merge(df2)
for ind in df3.index:
    t = Taxon(tax_id=df3['tax_id'][ind],parent_tax_id=df3['parent_tax_id'][ind],rank=df3['rank'][ind],name=df3['name'][ind])
    t.save()
    t.version.add(initial_version)
