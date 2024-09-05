import pandas as pd

df_tax = pd.read_csv("/home/pablo/metref/data/nodes.dmp", sep="|", usecols=[0,1,2], header=None, names=["tax_id", "parent_tax_id", "rank"])
df_tax = df_tax.replace("\t","", regex=True)

df2_tax = pd.read_csv("/home/pablo/metref/data/names.dmp", sep="|", usecols=[0,1,3], header=None, names=["tax_id", "name", "type"])
df2_tax = df2_tax.replace("\t","", regex=True)
df2_tax = df2_tax[df2_tax["type"]=="scientific name"]
df2_tax = df2_tax.drop(columns=["type"])

df3_tax = df_tax.merge(df2_tax)

df4_tax = df3_tax[df3_tax["tax_id"] == 1906744]

merged_tax = pd.read_csv("/home/pablo/metref/data/merged.dmp", sep="\t", usecols=[0,2], header=None, names=["old_tax", "new_tax"], dtype={'old_tax':str,'new_tax':str})
filtered_tax = merged_tax[merged_tax["old_tax"] == "1906744"]
new_tax = filtered_tax["new_tax"].iloc[0]
print(new_tax)