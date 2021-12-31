import random;
import numpy as np;
import spacy;
from unicodedata import normalize;
   
# pyTypo v0.1
# written by Tim Howard, 2019


# Supports all these types of mistakes:
# 1. Reversed letters  (e.g. "Please join me for lnuch")        50%
# 2. Wrong letters (nearby) (e.g. "Please join me for lumch")   20%
# 3. Missing letters  (e.g. "Please join me for luch")          15%
# 4. Extra letters (nearby)  (e.g. "Please join me for lunmch") 15%
# 5. Corrompe a acentuação
# 6. Corrompe os espacos entre o text oe os tamanhos

def geraIOB(doc):
    iobs = [];
    for token in doc:
        iob = token.ent_iob_;
        if iob != 'O':
           iob = iob + '-' + token.ent_type_;
        iobs.append(iob);
    return iobs;    

def retiraEspacos(doc, tipo):
    iobs = geraIOB(doc);
    texto = '';
    for i in range(len(doc)):
        if tipo == 1:
           if iobs[i] == 'B-TAMANHO':
              texto = texto.strip();
        elif tipo == 2:
           if iobs[i] == 'I-TAMANHO':
              texto = texto.strip();
        elif tipo == 3:
           if i > 0: 
              if iobs[i] == 'O' and iobs[i-1] == 'I-TAMANHO':
                  texto = texto.strip();
        texto = texto + doc[i].text + doc[i].whitespace_;
                    
        
    return texto; 

def geraObjetoNLPTamanho():
        nlp = spacy.load("pt_core_news_sm")
    
        config = {
           "phrase_matcher_attr": None,
           "validate": True,
           "overwrite_ents": True,
           "ent_id_sep": "||",
        }
        
        ruler = nlp.add_pipe("entity_ruler", config=config);
        
        patternsBR = [
                {"label": "DATE", "pattern": [{"SHAPE": "dd/dd/dddd"}]},
                {"label": "TIME", "pattern": [{"SHAPE": "dd:dd"}]},
                {"label": "TAMANHO", "pattern": 
                   [
                     {"LIKE_NUM": True},
                     {"IS_SPACE": True, "OP": "?"},
                     {"LOWER": 'x'},
                     {"IS_SPACE": True, "OP": "?"},
                     {"LIKE_NUM": True},
                     {"IS_SPACE": True, "OP": "?"},
                     {"LOWER": 'x'},
                     {"IS_SPACE": True, "OP": "?"},
                     {"LIKE_NUM": True},
                     {"IS_SPACE": True, "OP": "?"},
                     {"LOWER": {"IN": ["cm", "centimetros", "centimetro", "mm", "milímetro", "milimetros"]}}
                   ]
                },
                {"label": "TAMANHO", "pattern": 
                   [
                     {"LIKE_NUM": True},
                     {"IS_SPACE": True, "OP": "?"},
                     {"LOWER": 'x'},
                     {"LIKE_NUM": True},
                     {"IS_SPACE": True, "OP": "?"},
                     {"LOWER": {"IN": ["cm", "centimetros", "centimetro", "mm", "milímetro", "milimetros"]}}
                   ]
                },
                {"label": "TAMANHO", "pattern": 
                   [
                     {"LIKE_NUM": True},
                     {"IS_SPACE": True, "OP": "*"},
                     {"LOWER": {"IN": ["cm", "centimetros", "centimetro", "mm", "milímetro", "milimetros"]}}
                   ]
                },
            ]; 

        ruler.add_patterns(patternsBR);
        return nlp;


def remover_acentos(txt, maxErros = 1):
    acentos = set("áéíóúÁÉÍÓÚâêîôûÂÊÎÔÛçÇãÃõÕüÜ");
    posicoes = [];
    for i in range(len(txt)):
        if txt[i] in acentos:
           posicoes.append(i);
    random.shuffle(posicoes);
    result = list(txt);
    for i in range(min(maxErros, len(posicoes))):
        result[posicoes[i]] = normalize('NFKD', result[posicoes[i]]).encode('ASCII', 'ignore').decode('ASCII');

    return ''.join(result);

keys_nearby = {
    'A': ['Q','W','S','Z'],
    'B': ['V','G'],
    'C': ['X','D','F','V'],
    'D': ['S','E','R','F','C','X'],
    'E': ['R','D','S','W'], # 3, 4
    'F': ['R','T','G','V','C','D'],
    'G': ['T','B','V','F'],
    'H': ['Y','U','J','N'],
    'I': ['O','K','J','U'], # 8, 9
    'J': ['U','I','K','M','N','H'],
    'K': ['I','O','L',',','M','J'],
    'L': ['O','P',';','.',',','K'],
    'M': ['K',',','N','J'],
    'N': ['H','J','M'],
    'O': ['P','L','K','I'], # 0, 9
    'P': ['[',';','L','O'], #0, -
    'Q': ['W','A'],  # 2, 1
    'R': ['T','F','D','E'], # 4,5
    'S': ['E','D','X','Z','A','W'],
    'T': ['G','F','R'],  # 5, 6
    'U': ['I','J','H','Y'],  # 7, 8
    'V': ['G','B','C','F'],
    'W': ['E','S','A','Q'],  #3, 2
    'X': ['D','C','Z','S'],
    'Y': ['U','H'], # 7
    'Z': ['S','X','A'],
    ' ': ['B', 'N', 'M'],
}


def get_nearby_keyid(key):
    if key.upper() in keys_nearby:  # no options found
       key_options = keys_nearby[key.upper()];
       if not key.isupper():
          key_options = [key.lower() for key in key_options]; 
       return key_options[random.randint(1,len(key_options))-1];
    else:
       return key; 


prev_time = 0
cur_time = 0
time_threshold = 125  # low time delta triggers operation

random_percentage = 30  # to make things less predictable...

resume_operation = 0  # time until we resume operation
resume_timeout = 17000  # in milliseconds

moved_keypress_delay = 250  # milliseconds to hold before sending the keypress

stored_key_id = 0  # which keypress are we delaying for later?
stored_timing = 0  # when will we release that keypress?

in_word = False
last_key_id = 0  # what was the previous key that was pressed?
current_key_id = 0  # current key being pressed
nlp = geraObjetoNLPTamanho();
    

def generateTypo(texto):
    original = texto;
    maxErros = max(1, int(len(texto) / 50));
    erros = random.randint(1, maxErros);
    tamanho_palavra = len(texto);
    idxs = list(range(tamanho_palavra));
    random.shuffle(idxs);
    idxs = idxs[:erros];
    
    texto = list(texto);
    for idx in idxs:
         r = random.random()
         if r < 0.10:  # 10%
            type = 4;
         elif r < 0.30:  # 20%
            type = 3;
         elif r < 0.40:  # 10%
            type = 2;
         else:           # 60%
            type = 1;
        
          # decide which type of error to produce
          # 1. Reversed letters  (e.g. "Please join me for lnuch")        60%
          # 2. Wrong letters (nearby) (e.g. "Please join me for lumch")   10%
          # 3. Missing letters  (e.g. "Please join me for luch")          20%
          # 4. Extra letters (nearby)  (e.g. "Please join me for lunmch") 10%
         if idx >= len(texto)-1:
            idx = len(texto)-1; 

         if type == 1:
             aux = texto[idx];
             if idx < len(texto)-1:
                texto[idx] = texto[idx+1];
                texto[idx+1] = aux;
             else:   
                aux = texto[idx];
                texto[idx] = texto[idx-1];
                texto[idx-1] = aux;
         elif type == 2:
              texto[idx] = get_nearby_keyid(texto[idx]);
         elif type == 3:
              texto = texto[:idx] + texto[idx+1:];
         elif type == 4:
              antes = texto[:idx];
              carac = get_nearby_keyid(texto[idx]);
              depois = texto[idx+1:];
              
              antes.append(carac);
              antes.extend(depois);
              texto = antes.copy();
    
    resultado = "".join(texto);
    if original == resultado:
       resultado = generateTypo(resultado); 
    resultado = remover_acentos(resultado, random.randint(1, maxErros));
    resultado = retiraEspacos(nlp(resultado), random.randint(1, 2));  
    return resultado;
