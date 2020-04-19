import os
import sys
from os import listdir
from os.path import isfile, join

if len(sys.argv)<10:
   print("This script will call other scripts to make predictions for a fasta sequence")
   print("python "+sys.argv[0]+" 2_RNN_Prediction_assemble_CPU_only.py SetAuthorModelCAFA4.pl ../database/gene_ontology_edit.obo.2016-06-01 ../database/F_3_GO_table.DAT 1 ../database/Missing_GO_prediction.txt ../data/TargetFiles ../result/CAFA4_folder_for_prediction_filteredOnly ../FinalModels/model1 ../result/CaoLab_model1")
   print("python "+sys.argv[0]+" 2_RNN_Prediction_assemble.py SetAuthorModelCAFA4.pl ../database/gene_ontology_edit.obo.2016-06-01 ../database/F_3_GO_table.DAT 2 ../database/Missing_GO_prediction.txt ../data/TargetFiles ../result/CAFA4_folder_for_prediction_filteredOnly ../FinalModels/model2 ../result/CaoLab_model2")
   print("python "+sys.argv[0]+" 2_RNN_Prediction_assemble.py SetAuthorModelCAFA4.pl ../database/gene_ontology_edit.obo.2016-06-01 ../database/F_3_GO_table.DAT 3 ../database/Missing_GO_prediction.txt ../data/TargetFiles ../result/CAFA4_folder_for_prediction_filteredOnly ../FinalModels/model3 ../result/CaoLab_model3")
   sys.exit(0)

p1 = sys.argv[1]
p2 = sys.argv[2]

GOTree = sys.argv[3]
FGOTable = sys.argv[4]

modelName = sys.argv[5]
MissingGO = sys.argv[6]

OrigData = sys.argv[7]
dataIn = sys.argv[8]
models = sys.argv[9] 

dirOut = sys.argv[10]

os.system("mkdir "+dirOut) 

#temOutDir = dirOut+"/"+dirOut.split('/')[-1]+"_tem"
os.system("python "+p1+" "+dataIn+" "+models+" "+FGOTable+" "+dirOut)

# now we have the Predictions output folder, and will add the missing GO predictions for the missing target. OrigData 

MissingGOL = []
with open(MissingGO,"r") as fh:
    for line in fh:
        MissingGOL.append(line.strip())

onlyfiles = [f for f in listdir(OrigData) if isfile(join(OrigData, f))]

dirFilter = dirOut+"/filteredPrediction"
os.system("mkdir "+dirFilter)

for f in onlyfiles:
    allTargets = {}
    spec = f.split('.')[1] 
    fFilter = dirFilter+"/"+f
    origf = OrigData+"/"+f   # this is the original file 
    filterf = dirOut+"/Predictions/"+f+".filteredProlanguageGO"
    if not os.path.exists(filterf):
        print("Something is wrong, why we cannot find predictions for this category file:"+filterf+", but you have target file"+origf)
        sys.exit(0)
    fin = open(filterf,"r")
    fout = open(fFilter,"w")
    for line in fin:
        tem = line.strip().split() 
        if tem[0] not in allTargets:
            allTargets[tem[0]] = 1 
        fout.write(line)
    # now check the missing predictions  MissingGOL  one by one 
    missingTarget = {} 
    with open(origf,"r") as fh:
        for line in fh:
            if ">" in line:
                targName = line.split()[0][1:] 
                if targName not in allTargets:
                    print("Missing target prediction "+targName)
                    for i in range(len(MissingGOL)):
                        fout.write(targName+"\t"+MissingGOL[i]+"\n")
    fout.close()
    fin.close()

os.system("perl "+p2+" "+dirOut+"/filteredPrediction"+" "+"ProLanGO2 "+modelName+" "+dirOut+"/ProLanGO2")


