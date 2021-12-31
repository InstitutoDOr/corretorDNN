# -*- coding: UTF-8 -*-
import os;
import spacy;
import re;
import sys;
from nltk import tokenize;
from typogenerator import generateTypo;
from glob import glob;
import random;

ALL_CHARS = set("0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZáéíóúÁÉÍÓÚàÀèÈìÌòÒùÙâêîôûÂÊÎÔÛçÇãÃõÕäÄëËïÏöÖüÜ()[]{}&®ò-_%/ª°º²³*·|=<>+±´ .:;,!?'­^");
ALL_CHARS.add('"');

def saveList(listToSave, fname):
    with open(fname, 'w') as f:
         for item in listToSave:
           f.write("%s\n" % item)

def tokenize_characters(text):
    text = text.strip()
    original = text;
    text = ''.join(ch if ch in ALL_CHARS else '#' for ch in text)
    if 0:
       if '#' in text and '#' not in original:
          print(original);
          print(text);
          m;

    text = re.sub(' +', ' ', text).strip()
    tokens = [ch if ch != ' ' else '_' for ch in text];
    tokens = tokens[:1023];
    return ' '.join(tokens);


def openFile(filename):
    #laudo = open(filename, 'rt', encoding='ISO-8859-1');
    laudo = open(filename, 'rt', encoding='UTF-8');
    dataPort = laudo.read();
    laudo.close();
    
    texto = dataPort.replace('\n\xa0', '');
    texto = texto.replace('\xa0', ' ');
    texto = texto.replace('\n', ' ');
    texto = texto.replace('  ', ' ');
    
    docSents = tokenize.sent_tokenize(texto);
    return texto, docSents;


def tokenizaDocumento(filename):
    texto, docSents = openFile(filename);
    originais = [];
    certo = [];
    errado = [];
    for sent in docSents:
        for i in range(5):
            if len(sent) > 15:
               originais.append(sent);  
               typosent = generateTypo(sent); 
               certo.append(tokenize_characters(sent));
               errado.append(tokenize_characters(typosent));
    return certo, errado, originais;

## Colocar o diretorio com seus textos aqui
dirInput = '/dadosDL/database/spacy/Laudo-eco-360d';
files = glob('%s/**/portugues.txt' % dirInput, recursive = True);

filesClipped = files;

certoTrain = [];
certoDev = [];
erradoTrain = [];
erradoDev = [];
for filename in filesClipped:
   certo, errado, originais = tokenizaDocumento(filename);
   if random.random() < 0.2: # 80 % treino 20 % teste
      certoDev.extend(certo);
      erradoDev.extend(errado);
   else:  
      certoTrain.extend(certo);
      erradoTrain.extend(errado);

if not os.path.exists('data/ptbr/'):
   os.makedirs('data/ptbr/');

saveList(certoTrain, 'data/ptbr/train.tok.en');
saveList(certoDev, 'data/ptbr/dev.tok.en');

saveList(erradoTrain, 'data/ptbr/train.tok.fr');
saveList(erradoDev, 'data/ptbr/dev.tok.fr');
