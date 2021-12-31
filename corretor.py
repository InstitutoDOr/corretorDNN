# -*- coding: UTF-8 -*-

from fairseq.models.transformer import TransformerModel;
import re;

ALL_CHARS  = set("0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZáéíóúÁÉÍÓÚàÀèÈìÌòÒùÙâêîôûÂÊÎÔÛçÇãÃõÕäÄëËïÏöÖüÜ()[]{}&®ò-_%/ª°º²³*·|=<>+±´ .:;,!?'­^");
ALL_CHARS.add('"');

def tokenize_characters(text):
    text = text.strip()
    text = ''.join(ch if ch in ALL_CHARS else '#' for ch in text)
    text = re.sub(' +', ' ', text).strip()
    tokens = [ch if ch != ' ' else '_' for ch in text];
    return tokens

def corrige(corretor, input):
    tokens = tokenize_characters(input)[:1023]
    tokenizado = ' '.join(tokens);
    output = corretor.translate(tokenizado, beam=5, max_len_b = 1024, max_len = 1024);
    
    tokens = output.split(' ')
    text = ''.join(tokens);
    text = text.replace('_', ' ')
    text = text.replace('#', ' ')
    return text;

def criaCorretor(models_dir = 'models/ptbr01', checkpoint_file='checkpoint_best.pt', data_path='bin/ptbr'):
   corretor = TransformerModel.from_pretrained(
      models_dir,
      checkpoint_file=checkpoint_file,
      data_name_or_path=data_path   
   )
   return corretor;

