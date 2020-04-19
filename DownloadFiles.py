# By Prof. Renzhi Cao at April 2020
# Email: caora@plu.edu
# Pacific Lutheran University

import pathlib
import os
import os.path
import requests

softwareRoot = pathlib.Path(__file__).parent.absolute()

### You could customize by yourself ###
url_go = "https://cs.plu.edu/~caora/materials/gene_ontology_edit.obo.2016-06-01"

url_model = "https://cs.plu.edu/~caora/materials/ProLanGO2_model1.zip"  # you could also download ProLanGo2_model2.zip or model3.zip, you need to change ProLanGO2.py to use this model          
modelName = "model1"    # if you download model 2 in url_model, please also use model2 here 
#######################################

#print(softwareRoot)
# 1. Download gene ontology database
databaseDir = str(softwareRoot)+"/database"
pathGO = databaseDir+"/gene_ontology_edit.obo.2016-06-01"
if not os.path.isfile(pathGO):
    open(pathGO,'wb').write(requests.get(url_go).content)

# 2. Download models 
modelDir = str(softwareRoot)+"/FinalModels"
pathModel = modelDir+"/"+modelName
pathModelZip = modelDir+"/"+"model.zip"
if not os.path.isdir(pathModel):
    open(pathModelZip,'wb').write(requests.get(url_model).content)
    os.chdir(modelDir)
    os.system("unzip "+pathModelZip)






