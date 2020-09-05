"""fichier glogbal
"""
import os, re, sys, getopt
import numpy as np
import pandas as pd

import pickle as pkl
from nltk.corpus import stopwords, wordnet
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag
import multiprocessing as mp #paralleliser
import pickle as pkl #pour serialiser

from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer #tfidf
from sklearn.metrics.pairwise        import cosine_similarity #similarite cosine
from collections import defaultdict
from num2words   import num2words

class GetVar():
    def __init__(self):
        #self.documents  = self.cleaned_docs = None
        #self.vocabulary = 
        self.simple_tfidf = self.simple_counter_mat = None
        self.vect_tfidf = self.vect_tfidf_mat = None
        self.K = 5 # 5 par défaut à afficher
        self.PATH = './data'

        self.load_objects()

    def load_objects(self, path='./'):
        """[summary]
        
        Arguments:
            path {[type]} -- [description]
        
        Returns:
            dict -- l'index
        """
        with open(path+'objects.pkl', 'rb') as file:
            f = pkl.load(file)
            self.index, self.vocabulary, self.documents, self.cleaned_docs, self.documents_infos = f

        return self.index

#Initialistion des variables locales
var = GetVar()
K = 2

#Définition des stopwords de la langue anglaise
english_stopwords = stopwords.words('english')

#lemmatiseur
lemmatizer = WordNetLemmatizer()



############ fonctions creation index ###############

def get_vocabulary():
    if var.vocabulary is None:
        # Création du vocabulaire
        var.vocabulary = set()
        for doc in list(get_cleaned_docs()):
            for word in doc.split(' '):
                var.vocabulary.add(word)
    return var.vocabulary

def get_cleaned_docs():
    if var.cleaned_docs is None:
        var.documents = get_documents()
        var.cleaned_docs = []
        for doc in var.documents:
            var.cleaned_docs.append(clean_document(doc))
    return var.cleaned_docs

def get_documents(path=var.PATH):
    
    if var.documents == None:
        # Lecture des données
        var.documents_infos, var.documents  = [], []
        for folder in os.listdir(path):
            for file in os.listdir(path + "/" + folder):
                with open(path + '/' + folder + '/' + file, 'r') as f:
                    lines = f.readlines()
                    infos = {'title': lines[0].strip(), 'author': folder}
                    var.documents_infos.append(infos)
                    var.documents.append(''.join(lines[1:]))
    return var.documents_infos, var.documents

# Soit la fonction permettant de détecter le POS d'un mot
def convert_pos(pos):
    if pos.startswith('J'): return wordnet.ADJ
    if pos.startswith('V'): return wordnet.VERB
    if pos.startswith('R'): return wordnet.ADV
    return wordnet.NOUN


def try_convert_number(word):
    try:
        return num2words(int(word))
    except:
        return word

def clean_document(doc):
    doc   = re.sub(r'\W+', ' ', doc) # Suppression des ponctuations...
    words = doc.lower().strip().split(' ') # tokenisation des mots
    tags  = pos_tag(words)  # Contient les POS de chaque mot dans le document
    lemmatised_words = []
    for word, pos in tags:
        lemmatised_words.append(lemmatizer.lemmatize(word, convert_pos(pos)))
    words = [try_convert_number(word) for word in lemmatised_words if word not in english_stopwords and len(word)>1]
    return ' '.join(words)


def get_doc_index(doc):
    id_doc, document = doc
    index = defaultdict(list)
    doc_words = document.split(' ')
    nb_words_in_doc = len(doc_words)
    
    for word in np.unique(doc_words):
        idx = [m.start() for m in re.finditer(word, document)]
        index[word] = {'num_doc': id_doc, 'nb_fois' : len(idx), 'pos': idx, 'len_doc': nb_words_in_doc}
    return dict(index)


def build_index(path):
    """[summary]
    
    Arguments:
        path {[type]} -- [description]
    
    Returns:
        [type] -- [description]
    """
    
    var.documents_infos, var.documents = get_documents()
    
    var.cleaned_docs = get_cleaned_docs()

    # Création du vocabulaire
    vocabulary = set()
    for doc in list(var.cleaned_docs):
        for word in doc.split(' '):
            vocabulary.add(word)

    nb_process = mp.cpu_count()
    index = defaultdict(list) #indiquer que chaque valeur associée à une clée est bien une liste
    with mp.Pool(processes = nb_process-1) as pool :
        all_dicts = pool.map(get_doc_index, list(enumerate(var.cleaned_docs)))
    for dico in all_dicts:
        for key in dico.keys():
            index[key].append(dico[key])

    return index


######  les requetes basiques ####
def binary_question(word):
    doc_ids = [doc['num_doc'] for doc in var.index[word]]
    if len(doc_ids) > 0 : 
        print("'" + word + "'" , 'appears in ', len(doc_ids), 'documents')
        return doc_ids
    return print("'"+ word + "'" , "doesn't exist. Please, try again !")

def set_intersection(list_of_sets):
    if len(list_of_sets)<=2:
        return set.intersection(list_of_sets[0], list_of_sets[1])
    else:
        return set.intersection(list_of_sets[0], set_intersection(list_of_sets[1:]))
    
def set_union(list_of_sets):
    if len(list_of_sets)<=2:
        return set.union(list_of_sets[0], list_of_sets[1])
    else:
        return set.union(list_of_sets[0], set_union(list_of_sets[1:]))

def search_text(text):
    text = clean_document(text)
    id_docs = []
    word_list = text.split(' ')
    
    if len(word_list) == 1: #Cas où le texte entré n'est qu'un mot
        return binary_question(word_list)
    
    for word in word_list:
        id_docs.append(set(binary_question(word)))
     
    intersection, union = set_intersection(id_docs), set_union(id_docs)
    print("'" + text + "'" , 'has', len(intersection), 'exact matches')
    print("'" + text + "'" , 'has', len(union), 'approximates matches')
    return intersection, union

def queries_index(sentence):
    cleaned_sentence = clean_document(sentence)
    sentence_list    = cleaned_sentence.split(' ')
    intersection, _  = search_text(sentence) #obtenir les documents où tous les mots apparaissent 
    final_docs       = []
    print('---------------------------------------')
    for doc_id in intersection: #on ne s'interesse qu'aux documents contenant à la fois tous les mots de la requête
        _all_sets = [] #contiendra les positions modifiées d'apparition des mots dans le document
        for word in sentence_list:
            for docs in var.index[word]:
                if docs['num_doc'] == doc_id:
                    word_index = sentence_list.index(word)
                    new_pos=[pos - len(' '.join(sentence_list[:word_index]))-1 if word_index>0 else pos for pos in docs['pos']]
                    _all_sets.append(set(new_pos))
        if len(set_intersection(_all_sets))>0: #intersection des bons décalages trouvé, donc bon document
            final_docs.append(doc_id) 
    print("'" + cleaned_sentence + "'",'appears in exact oder in', len(final_docs), 'documents')
    print('These documents are :', final_docs)


#### Faire du ranking #############
def rank_by_ocurrence(query, k=var.K):
    cleaned_query = clean_document(query)
    words = cleaned_query.split(' ')
    
    scores = pd.Series(np.zeros(len(var.documents), dtype=int)) #initialiser les scores de tous les documents
   
    for word in words:
        if len(var.index[word]) > 0: #le mot existe dans l'index
            scores = scores.add(pd.DataFrame(var.index[word]).set_index('num_doc').nb_fois, fill_value=0)
    
    return scores.sort_values(ascending=False)[:k] #les top k premiers

def rank_by_frequency(query, k=var.K):
    cleaned_query = clean_document(query)
    words = cleaned_query.split(' ')
    
    scores = pd.Series(np.zeros(len(var.documents), dtype=int)) #initialiser les scores de tous les documents
    
    for word in words:
        if len(var.index[word]) > 0: #le mot existe dans l'index
            _df = pd.DataFrame(var.index[word]).set_index('num_doc').nb_fois
            _df = _df/pd.DataFrame(var.index[word]).set_index('num_doc').len_doc
            #print(_df.head())
            scores = scores.add(_df, fill_value=0)
    return scores.sort_values(ascending=False)[:k] #les top k premiers

def simple_TFIDF(query, k=var.K):
    
    cleaned_query = clean_document(query) #nettoyer la requete
    
    query_TFIDF = var.simple_tfidf.transform([cleaned_query]).toarray() #tfidf de la requete
    
    #produit scalaire simple(somme des tfdfs des mots apparaissants dans la requête)
    relevant_docs = pd.Series(var.simple_counter_mat.dot(query_TFIDF.T).flatten())
    
    return relevant_docs.sort_values(ascending=False)[:k]


def vect_TFIDF(query, k=var.K):

    if var.vect_tfidf == None:
        var.vocabulary     = get_vocabulary()
        var.vect_tfidf     = TfidfVectorizer(vocabulary=var.vocabulary, norm='l1')
        var.vect_tfidf_mat = var.vect_tfidf.fit_transform(var.documents)

    cleaned_query = clean_document(query) #nettoyer la requete
    
    query_TFIDF = var.vect_tfidf.transform([cleaned_query]).toarray() #tfidf de la requete
    
    #similarité cosinus
    relevant_docs = pd.Series(cosine_similarity(query_TFIDF, var.vect_tfidf_mat).flatten())
    
    return relevant_docs.sort_values(ascending=False)[:k]



### Affichage notebook
def change_font():
    """Une méthode qui retourme le fichier HTML et CSS adéquat pour les fonts dans jupyter.
    """

    html = """
    <style>
    
    .rendered_html {
         font-size: 22px; 
         font-family: Garamond;
         line-height: 140%;
         text-align: justify;
         text-justify: inter-word;
    }

    div.text_cell_render h1 { /* Main titles bigger, centered */
        text-align:center;
    # }
    
    </style>"""

    return html

# def set_K(K):
#     K = K

if __name__ == '__main__':
    
    #K = 0
    ### getion des options ###
    try:
        optlist, args = getopt.getopt(sys.argv[1:], 'k: ')
        if(len(optlist) == 1):
            #print(type(var))
            #print(var.K)
            var.K = int(optlist[0][1] if int(optlist[0][1])>0 else "error")
            #set_K(K)
            #print(var.K)

    except:
        print("Argument optionnel non reconnu. Utilisez -k suivi d'un entier strictement positif ou laissez le champ vide")
        sys.exit(2)
    ############################
    #print(var.K)

    from tp_tools import main
    main(k=var.K)



        

