################################################
#
#  Developed by Dr. Renzhi Cao
#  Pacific Lutheran University
#  Email: caora@plu.edu
#  Website: https://cs.plu.edu/~caora/
#  April 2020
###############################################

from __future__ import unicode_literals, print_function, division
from io import open
import unicodedata
import string
import re
import random
import sys
import os
import torch
import torch.nn as nn
from torch import optim
import torch.nn.functional as F
import time
import math
from os import listdir
from os.path import isfile, join

import numpy as np


#torch.nn.Module.dump_patches = True

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
device = torch.device("cpu")
print(device)

SOS_token = 0
EOS_token = 1

class Lang:
    def __init__(self, name):
        self.name = name
        self.word2index = {}
        self.word2count = {}
        self.index2word = {0: "SOS", 1: "EOS"}
        self.n_words = 2  # Count SOS and EOS

    def addSentence(self, sentence):
        for word in sentence.split(' '):
            self.addWord(word)

    def addWord(self, word):
        if word not in self.word2index:
            self.word2index[word] = self.n_words
            self.word2count[word] = 1
            self.index2word[self.n_words] = word
            self.n_words += 1
        else:
            self.word2count[word] += 1

def unicodeToAscii(s):
    return ''.join(
        c for c in unicodedata.normalize('NFD', s)
        if unicodedata.category(c) != 'Mn'
    )
# Lowercase, trim, and remove non-letter characters

def normalizeString(s):
    #s = unicodeToAscii(s.lower().strip())
    #s = re.sub(r"([.!?])", r" \1", s)
    #s = re.sub(r"[^a-zA-Z.!?]+", r" ", s)
    return s.lower().strip()


def readLangs(lang, reverse=False):
    print("Reading lines...")

    # Read the file and split into lines
    lines = []
    with open(lang, "r") as fh:
      for line in fh:
        tem = line.strip().split("|")
        lines.append(tem[0]+"\t"+tem[1])

    # Split every line into pairs and normalize
    pairs = [[normalizeString(s) for s in l.split('\t')] for l in lines]

    return pairs



class EncoderRNN(nn.Module):
    def __init__(self, input_size, hidden_size):
        super(EncoderRNN, self).__init__()
        self.hidden_size = hidden_size

        self.embedding = nn.Embedding(input_size, hidden_size)
        self.gru = nn.GRU(hidden_size, hidden_size)

    def forward(self, input, hidden):
        embedded = self.embedding(input).view(1, 1, -1)
        output = embedded
        output, hidden = self.gru(output, hidden)
        return output, hidden

    def initHidden(self):
        return torch.zeros(1, 1, self.hidden_size, device=device)

class DecoderRNN(nn.Module):
    def __init__(self, hidden_size, output_size):
        super(DecoderRNN, self).__init__()
        self.hidden_size = hidden_size

        self.embedding = nn.Embedding(output_size, hidden_size)
        self.gru = nn.GRU(hidden_size, hidden_size)
        self.out = nn.Linear(hidden_size, output_size)
        self.softmax = nn.LogSoftmax(dim=1)

    def forward(self, input, hidden):
        output = self.embedding(input).view(1, 1, -1)
        output = F.relu(output)
        output, hidden = self.gru(output, hidden)
        output = self.softmax(self.out(output[0]))
        return output, hidden

    def initHidden(self):
        return torch.zeros(1, 1, self.hidden_size, device=device)

class AttnDecoderRNN(nn.Module):
    def __init__(self, hidden_size, output_size, dropout_p=0.1, max_length = 50):
        super(AttnDecoderRNN, self).__init__()
        self.hidden_size = hidden_size
        self.output_size = output_size
        self.dropout_p = dropout_p
        self.max_length = max_length

        self.embedding = nn.Embedding(self.output_size, self.hidden_size)
        self.attn = nn.Linear(self.hidden_size * 2, self.max_length)
        self.attn_combine = nn.Linear(self.hidden_size * 2, self.hidden_size)
        self.dropout = nn.Dropout(self.dropout_p)
        self.gru = nn.GRU(self.hidden_size, self.hidden_size)
        self.out = nn.Linear(self.hidden_size, self.output_size)

    def forward(self, input, hidden, encoder_outputs):
        embedded = self.embedding(input).view(1, 1, -1)
        embedded = self.dropout(embedded)

        attn_weights = F.softmax(
            self.attn(torch.cat((embedded[0], hidden[0]), 1)), dim=1)
        attn_applied = torch.bmm(attn_weights.unsqueeze(0),
                                 encoder_outputs.unsqueeze(0))

        output = torch.cat((embedded[0], attn_applied[0]), 1)
        output = self.attn_combine(output).unsqueeze(0)

        output = F.relu(output)
        output, hidden = self.gru(output, hidden)

        output = F.log_softmax(self.out(output[0]), dim=1)
        return output, hidden, attn_weights

    def initHidden(self):
        return torch.zeros(1, 1, self.hidden_size, device=device)

# preparing training data
def indexesFromSentence(lang, sentence):
    return [lang.word2index[word] for word in sentence.split(' ')]


def tensorFromSentence(lang, sentence):
    indexes = indexesFromSentence(lang, sentence)
    indexes.append(EOS_token)
    return torch.tensor(indexes, dtype=torch.long, device=device).view(-1, 1)


def tensorsFromPair(pair):
    input_tensor = tensorFromSentence(input_lang, pair[0])
    target_tensor = tensorFromSentence(output_lang, pair[1])
    return (input_tensor, target_tensor)


# evaluation
def evaluate(encoder, decoder, sentence, max_length):
    with torch.no_grad():
        input_tensor = tensorFromSentence(input_lang, sentence)
        input_length = input_tensor.size()[0]
        encoder_hidden = encoder.initHidden()

        encoder_outputs = torch.zeros(max_length, encoder.hidden_size, device=device)

        for ei in range(input_length):
            try:
                encoder_output, encoder_hidden = encoder(input_tensor[ei],
                                                         encoder_hidden)
                encoder_outputs[ei] += encoder_output[0, 0]
            except:
                print("Something is wrong for "+str(ei))
        decoder_input = torch.tensor([[SOS_token]], device=device)  # SOS

        decoder_hidden = encoder_hidden

        decoded_words = []
        decoder_attentions = torch.zeros(max_length, max_length)

        for di in range(max_length):
            decoder_output, decoder_hidden, decoder_attention = decoder(
                decoder_input, decoder_hidden, encoder_outputs)
            decoder_attentions[di] = decoder_attention.data
            topv, topi = decoder_output.data.topk(1)
            if topi.item() == EOS_token:
                decoded_words.append('<EOS>')
                break
            else:
                decoded_words.append(output_lang.index2word[topi.item()])

            decoder_input = topi.squeeze().detach()

        return decoded_words, decoder_attentions[:di + 1]

def evalPreRecall(realSentence, predSentence):
    allwordsReal = realSentence.split()
    allwordsPred = predSentence.split()[:-1]    # we know the last word is EOS
    if len(allwordsPred)==0:
        return (0,0)
    temp = set(allwordsReal)
    totalL = len([value for value in allwordsPred if value in temp])
    prec = totalL/len(allwordsPred)
    recall = totalL/len(allwordsReal)
    #print("precision="+str(prec))
    #print("Recall="+str(recall))
    return (prec,recall)

def evaluateOnTest(encoder, decoder, pairs, theMax_length):
    Ave_precision = 0
    Ave_recall = 0
    count=0
    for i in range(len(pairs)):
        pair = pairs[i]
        print('>', pair[0])
        print('=', pair[1])
        output_words, attentions = evaluate(encoder, decoder, pair[0], theMax_length)
        output_sentence = ' '.join(output_words)
        print('<', output_sentence)
        print('')
        (pre, rec) = evalPreRecall(pair[1], output_sentence)
        count+=1
        Ave_precision+=pre
        Ave_recall+=rec
    if count>0:
        Ave_precision/=count
        Ave_recall/=count
    print("Average Precision: "+str(Ave_precision))
    print("Average Recall: "+str(Ave_recall))


def selectwords(s,start,end):
    tem = s.split()
    tem2 = tem[start:end-1]
    if len(tem2) == 0:
        return ""
    else:
        result = tem2[0]
    for i in range(1,len(tem2)):
        result=result+" "+tem2[i]
    return result

if len(sys.argv) < 5:
    print("ProLanX program for prediction. Assembly method, several models are needed (name rule: model_maxLen_Fscore)")
    print("Need five parameters: input k-mers data or directory for several input files, max length of k-mers (this should match with your trained model max length), dir_trained_model, GO table, output folder")

    print("python "+sys.argv[0]+" ../data/CAFA3_sample ../../../upload_Google/result/Generated100_models ../database/F_3_GO_table.DAT ../test/PredictionCAFA4")
    #print("python "+sys.argv[0]+" ../result/CAFA4_folder_for_prediction_filteredOnly ../trained_model_and_data/myModels1/ ../database/F_3_GO_table.DAT ../result/CAFA4_prediction_temp1")

    sys.exit(0)


inputTest = sys.argv[1]
TrainedModels = sys.argv[2]
GOTable = sys.argv[3]
dir_output = sys.argv[4]

try:
    os.stat(dir_output)
except:
    os.mkdir(dir_output)

pre_dir = dir_output+"/Predictions"
try:
    os.stat(pre_dir)
except:
    os.mkdir(pre_dir)

if not os.path.isdir(inputTest):
    temdir = dir_output+"/TemInput"
    try:
        os.mkdir(temdir)
    except:
        print(temdir+" exists already")
    os.system("cp "+inputTest+" "+temdir)
    inputTest = temdir


# load GO table
hashGO = {}
with open(GOTable,"r") as fh:
    for line in fh:
        tem = line.strip().split()
        hashGO[tem[1].lower()] = tem[0]

#print(hashGO)
score = 0.9



#(encoder, attn_decoder, output_lang) = torch.load(TrainedModel, map_location='cpu')
# now get the test data
onlyfiles = [f for f in listdir(inputTest) if isfile(join(inputTest, f))]

finalPredictHash = {}         # this is for final prediction. ["filename":{"targetname":{"GO term":score}}]
allModels = [f for f in listdir(TrainedModels) if isfile(join(TrainedModels, f))]
for MyModel in allModels:
    TrainedModel = TrainedModels+"/"+MyModel
    score = float(MyModel.split('_')[-1])
    MAX_LENGTH = int(MyModel.split('_')[-2])
    # first load the trained model
    if True:
        print("use cpu")
        (encoder, attn_decoder, input_lang, output_lang) = torch.load(TrainedModel, map_location='cpu')
    else:
        print("use GPU")
        (encoder, attn_decoder, input_lang, output_lang) = torch.load(TrainedModel, map_location='cuda:0')
    encoder.eval()
    attn_decoder.eval()

    for eachfile in onlyfiles:
        inputData = join(inputTest,eachfile)
        pairs = readLangs(inputData, False)
        for i in range(len(pairs)):
            #print("now checking ... " + pairs[i][0])
            #print(type(pairs[i][0]))
            totalSlice = int(len(pairs[i][0].split())/MAX_LENGTH)
            #print(len(pairs[i][0].split()))
            #print(MAX_LENGTH)
            #print("total slice is "+str(totalSlice))
            output_words = "NULL"
            for Slicei in range(totalSlice):
                myselectedwords = selectwords(pairs[i][0],Slicei*MAX_LENGTH,(Slicei+1)*MAX_LENGTH)
                if myselectedwords == "":
                    continue
                if output_words == "NULL":
                    #print("evaluating from "+str(Slicei*MAX_LENGTH)+" to " + str((Slicei+1)*MAX_LENGTH))
                    #print(pairs[i][0][Slicei*MAX_LENGTH:(Slicei+1)*MAX_LENGTH])
                    try:
                        output_words, attentions = evaluate(encoder, attn_decoder, myselectedwords, MAX_LENGTH)
                    except:
                        print("Something is wrong for this prediction "+str(myselectedwords))
                        
                else:
                    try:
                        output_words_tem, attentions = evaluate(encoder, attn_decoder,myselectedwords, MAX_LENGTH)
                    except:
                        print("Something is wrong for this prediction "+str(myselectedwords))
                        output_words_tem = []     # do nothing 
                    output_words = output_words + output_words_tem
            myselectedwords = selectwords(pairs[i][0],totalSlice*MAX_LENGTH,len(pairs[i][0].split()))
            if myselectedwords == "":
                if output_words == "NULL":
                    continue
            else:
                try:
                    output_words_tem, attentions = evaluate(encoder, attn_decoder, myselectedwords,MAX_LENGTH)
                except:
                    print("Something is wrong for this prediction "+str(myselectedwords))
                    output_words_tem = []
                if output_words == "NULL":
                    output_words = output_words_tem
                else:
                    output_words = output_words + output_words_tem

            #print(output_words)
            if output_words == "NULL" or len(output_words)==0:
                continue         # nothing to do 
            output_words = list(set(output_words))     # we just filter the duplicates in the output

            for each in output_words:
                if each in hashGO:
                    GOterm = hashGO[each]
                    if eachfile not in finalPredictHash:
                        finalPredictHash[eachfile] = {}
                    catName = pairs[i][1][1:].upper()
                    if catName not in finalPredictHash[eachfile]:
                        finalPredictHash[eachfile][catName] = {}
                    if GOterm in finalPredictHash[eachfile][catName]:
                        finalPredictHash[eachfile][catName][GOterm] = 1 - (1-score)*(1-finalPredictHash[eachfile][catName][GOterm])
                    else:
                        finalPredictHash[eachfile][catName][GOterm] = score


for eachfile in onlyfiles:
    outputFile = pre_dir+"/"+eachfile
    fout = open(outputFile,"w")
    if eachfile in finalPredictHash:
        for eachCategory in finalPredictHash[eachfile]:
            for eachGO, valueGO in sorted(finalPredictHash[eachfile][eachCategory].items(), key=lambda item: item[1], reverse=True):
                fout.write(eachCategory+"\t"+eachGO+"\t"+str(valueGO)+"\n")

    fout.close()



#evaluateOnTest(encoder, attn_decoder, pairs, theMax_length = MAX_LENGTH)
