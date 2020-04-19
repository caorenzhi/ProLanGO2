# ProLanGO2

ProLanGO2 is a novel machine learning and natural language processing method for protein function
 prediction

# Citation
--------------------------------------------------------------------------------------
Cao, Renzhi, Colton Freitas, Leong Chan, Miao Sun, Haiqing Jiang, and Zhangxin Chen. "ProLanGO: protein function prediction using neural machine translation based on a recurrent neural network." Molecules 22, no. 10 (2017): 1732.


# Test Environment
--------------------------------------------------------------------------------------
Ubuntu, Centos

# Requirements
--------------------------------------------------------------------------------------
(1). Python3+

(2). Pytorch version 1.0.1
```
https://pytorch.org/

#conda install pytorch==1.0.1 torchvision -c pytorch
```
GPU is NOT required.

(3). requests
```
pip install request
```
(4). Download model and Gene Ontology file<br>
There is a python script DownloadFiles.py in the software to help you download all needed files, please run it for the first time. If it didn't work, you could manually downloaded the files as follows:<br>
We need gene ontology database gene_ontology_edit.obo.2016-06-01 in database directory, which could be downloaded from https://cs.plu.edu/~caora/materials/gene_ontology_edit.obo.2016-06-01, and also the folder model1 in FinalModels which contains models could be downloaded from https://cs.plu.edu/~caora/materials/ProLanGO2_model1.zip.  


# Test example
--------------------------------------------------------------------------------------
You should provide folder with fasta format sequence files, and run the python script ProLanGO2.py 

#cd script

#python ProLanGO2.py ../test/fastaFiles ../test/testout

You should be able to find the GO term prediction files in the output folder ProLanGO2_pred.


--------------------------------------------------------------------------------------
Developed by Dr. Renzhi Cao at Pacific Lutheran University:

Please contact Dr. Cao for any questions: caora@plu.edu (PI)

