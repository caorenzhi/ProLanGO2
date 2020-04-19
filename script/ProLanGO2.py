################################################
#
#  Developed by Dr. Renzhi Cao
#  Pacific Lutheran University
#  Email: caora@plu.edu
#  Website: https://cs.plu.edu/~caora/
#  April 2020
#
###############################################

import sys
import os
import os.path
import pathlib
softwareScript = str(pathlib.Path(__file__).parent.absolute())
softwareRoot = softwareScript[:softwareScript.rfind('/')]
#print(softwareRoot)

if len(sys.argv) < 2:
   print("Welcome to use ProLanGO2, a novel protein function prediction method using machine learning and natural language processing technique. \n")
   print("Need two parameters, a folder with fasta files, and output directory\n")
   print("python "+sys.argv[0]+" ../test/fastaFiles ../test/testout")
   sys.exit(0)

dirInput = sys.argv[1]
dirOut = sys.argv[2] 
os.system("mkdir "+dirOut)

# you may want to change the folder if you downloaded model2 or model3
data_modelFolder = softwareRoot+"/FinalModels/model1"
modelName = "1"
#### those should be downloaded when you have the software ####
script_prepareLan = softwareScript+"/1_Build_Protein_language_from_CAFA_for_prediction.pl"
data_fragDatabase = softwareRoot+"/database/New_Balanced_FragDATABASE_34567_top2000.txt"
script_RNN_assemble = softwareScript+"/2_RNN_Prediction_assemble.py"
script_setAuthor = softwareScript+"/SetAuthorModelCAFA4.pl"
data_GeneOntology = softwareRoot+"/database/gene_ontology_edit.obo.2016-06-01"
data_GOTable = softwareRoot+"/database/F_3_GO_table.DAT"
data_missingGO = softwareRoot+"/database/Missing_GO_prediction.txt"
script_predict = softwareScript+"/PredictCAFA4_ProLanX.py" 

### first check if you have downloaded the software correctly ###
if not os.path.isfile(script_prepareLan) or not os.path.isfile(data_fragDatabase) or not os.path.isfile(script_RNN_assemble) or not os.path.isfile(script_setAuthor) or not os.path.isfile(data_GOTable) or not os.path.isfile(data_missingGO) or not os.path.isfile(script_predict):
    print("It seems some files are missing, please download the ProLanGO2 software again and make sure you have downloaded all scripts and files in database folder. Contact Prof. Renzhi Cao (caora@plu.edu) for any questions")
    sys.exit(0)

### now check if this is the first time to run this code, you may need to download GO database and model 
if not os.path.isfile(data_GeneOntology) or not os.path.isdir(data_modelFolder):
    print("It seems you are running this script for the first time, and you haven't downloaded gene ontology file to "+data_GeneOntology+", also download the model 1 to "+data_modelFolder)
    print("Now trying to run the download script to get it fixed, if it is not working, please manually download the gene ontology file from: https://cs.plu.edu/~caora/materials/gene_ontology_edit.obo.2016-06-01, and model 1 from: https://cs.plu.edu/~caora/materials/ProLanGO2_model1.zip")
    
    os.chdir(softwareRoot)
    os.system("python DownloadFiles.py")
    print("The go database and model should be downloaded, please verify by re-run this program")
    sys.exit(0)

### now we are going to first process your input 
processedOut = dirOut+"/ProcessedOutput"
os.system("perl "+script_prepareLan+" "+data_fragDatabase+" "+dirInput+" "+processedOut)

prolangoPre = dirOut+"/ProLanGO2_pred"

### now we will run the prediction 
#print("python "+script_predict+" "+script_RNN_assemble+" "+script_setAuthor+" "+data_GeneOntology+" "+data_GOTable+" "+modelName+" "+data_missingGO+" "+dirInput+" "+processedOut+" "+data_modelFolder+" "+prolangoPre)

os.system("python "+script_predict+" "+script_RNN_assemble+" "+script_setAuthor+" "+data_GeneOntology+" "+data_GOTable+" "+modelName+" "+data_missingGO+" "+dirInput+" "+processedOut+" "+data_modelFolder+" "+prolangoPre)
