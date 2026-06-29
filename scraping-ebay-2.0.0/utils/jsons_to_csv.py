import os
import shutil
import pandas as pd
import json
allpaths=[]
print("getting all json files")
for root, directories, files in os.walk("./", topdown=False):
    for name in files:
        f=(os.path.join(root, name))
        if f.endswith((".json")):
            allpaths.append(f)
            
dflist=[]
for filepath in allpaths:
    
    filename=(os.path.basename(filepath))
    filename=filename.split(".")[0]
    with open(filepath) as json_file:
        data = json.load(json_file)

    df = pd.DataFrame(data, index=[0])
    df["prod_id"]=filename
    dflist.append(df)
df1 = pd.concat(dflist,axis=0, ignore_index=True)
df1 = df1[ ['prod_id'] + [ col for col in df1.columns if col != 'prod_id' ] ]
df1.to_csv("spects.csv")
print("CSV file generated")
