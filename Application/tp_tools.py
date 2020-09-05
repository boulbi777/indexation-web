"""This file contain the style applied to markdown in the notebook and other functions for app !!
"""
from PyInquirer import Separator, prompt
import getopt, sys
import pandas as pd
from indexation import var, vect_TFIDF, rank_by_frequency, queries_index

#K = 5

class Accueil():
    """Accueil.
    """

    def display_info(self):
        with open('accueil.txt', 'r', encoding="utf-8") as asset:
            print(asset.read())

    def make_choice(self):
        reponse = prompt(Q.get_question(1))
        if reponse['Menu'] == 'Faire une recherche':
            return Menu().lancement()
        else:
            print("!!!!!!!!!!!!!! BYE !!!!!!!!!!!!!!!!!!!!")
            sys.exit(2)


class Menu:
    def lancement(self):
        """Fonction de lancement du menu principal.
        """
        
        answer = prompt(Q.get_question(0))

        if answer['menu principal'] == 'Recherche efficace (I\'m lucky)':
            return display_smart_search()
        elif answer['menu principal'] == 'Recherche efficace par frequence':
            freq_search()
        elif answer['menu principal'] == 'Recherche à mots succesifs exacts':
            #queries_index
            exact_macthes()
        elif answer['menu principal'] == 'Créer mon propre index':
            pass
        else:
            print("!!!!!!!!!!!!!! BYE !!!!!!!!!!!!!!!!!!!!")
            sys.exit(2)



class Questions:
    """Classe permettant d'accéder aux questions du menu.
    """

    def __init__(self):
        self.questions = [
            
            {
                'number': 0,
                'type': 'list',
                'name': 'menu principal',
                'message': 'Que souhaitez-vous faire?',
                'choices': [
                    'Recherche efficace (I\'m lucky)',
                    Separator(),
                    'Recherche efficace par frequence',
                    Separator(),
                    'Recherche à mots succesifs exacts',
                    Separator(),
                    'Recherche à mots partiels',
                    Separator(),
                    'Créer mon propre index',
                    Separator(),
                    'Informations sur le moteur de recherche',
                    Separator(),
                    "Quitter"
                ]
            },

            {
                'number': 1,
                'type': 'list',
                'name': 'Menu',
                'message': 'Bienvenue dans BZ-Search !!!',
                'choices': [
                    'Faire une recherche',
                    Separator(),
                    'Quitter',
                ]
            },

            {
                'number': 2,
                'type': 'list',
                'name': 'continue',
                'message': 'Sur quel critère souhaitez-vous effectuer votre recherche?',
                'choices': [
                    'Continuer à lire',
                    Separator(),
                    'Retour',
                    Separator(),
                    'Revenir au menu',
                    Separator(),
                    'Quitter',

                ]
            },

        ]
    

    def get_question(self, number):
        """Retourne la question concernée
        
        Arguments:
            number {[int]} -- Le numéro de la question concernée.
        
        Returns:
            [dict] -- Un dictionnaire correspondant à une question posée dans le menu.
        """

        return self.questions[number]

    def set_question(self, dataframe):
        self.questions.append(
            {
                'number': len(self.questions),
                'type': 'list',
                'name': 'choix_suggestion',
                'message': 'Choisissez un article',
                'choices': intersperse(
                    sequence = [str(i) + '. ' + ' '.join([row.doc, str(row.score)]) for i,row in dataframe.iterrows()], 
                    value = Separator()
                )
            }
        )

def intersperse(sequence, value):
    """Permet d'injecter des valeurs entre chaque double élément de notre liste.
        Est utilisé pour pour découper automatiquement les réponses proposées par
        notre algorithme en différents choix.
    """

    res = [value] * (2*len(sequence) - 1)
    res[::2] = sequence
    return res



def display_smart_search():

    answer = input("Search: ")
    #print("la valeur de k", var.K)
    best_k_series = round(vect_TFIDF(query = answer),2)
    idx = best_k_series.index.values
    #print(best_k_series)
    #print(idx)
    var_series = pd.Series(var.documents_infos)
    #print(var_series.index)
    var_series = var_series[var_series.index.isin(idx)]
    #print(var_series)
    titles = [dico['title'][:80] + '...' for dico in var_series]
    # for i in range(len(var_series)):
    #     print(idx[i])
    #     print(var_series.iloc[i])


    #print(titles[0])
    show_df = pd.DataFrame({'_id': idx,'doc' : titles, 'score': best_k_series.values}).set_index('_id')
    #print(show_df)
    Q.set_question(show_df)

    def article_choice():

        answer = prompt(Q.questions[len(Q.questions) - 1])

        for i, _idx in enumerate(idx):
            if answer['choix_suggestion'].startswith(str(_idx)+'.'):
                print('as idx', str(_idx))
                selected_idx = i
                break


        print('-'*120)
        print('Author : ', var.documents_infos[idx[selected_idx]]['author'])
        print('title  : ', var.documents_infos[idx[selected_idx]]['title'])

        print('-'*120)
        print(idx)
        print(var.documents[idx[selected_idx]][:1000] + '.....')

        answer = prompt(Q.get_question(2))

        if answer['continue'] == "Continuer à lire":
            print(var.documents[idx[selected_idx]])
            article_choice()
        elif answer['continue'] == "Retour":
            article_choice()
        elif answer['continue'] == "Revenir au menu":
            Menu().lancement()
        else:
            print("BYE")
            sys.exit(2)

    article_choice()


def freq_search():
    answer = input("Search: ")
    #print("la valeur de k", var.K)
    best_k_series = round(rank_by_frequency(query = answer, k=var.K),2)
    idx = best_k_series.index.values
    var_series = pd.Series(var.documents_infos)
    var_series = var_series[var_series.index.isin(idx)]
    titles = [dico['title'][:80] + '...' for dico in var_series]


    #print(titles[0])
    show_df = pd.DataFrame({'_id': idx,'doc' : titles, 'score': best_k_series.values}).set_index('_id')
    #print(show_df)
    Q.set_question(show_df)

    def article_choice():

        answer = prompt(Q.questions[len(Q.questions) - 1])

        for i, _idx in enumerate(idx):
            if answer['choix_suggestion'].startswith(str(_idx)+'.'):
                print('as idx', str(_idx))
                selected_idx = i
                break


        print('-'*120)
        print('Author : ', var.documents_infos[idx[selected_idx]]['author'])
        print('title  : ', var.documents_infos[idx[selected_idx]]['title'])

        print('-'*120)
        print(idx)
        print(var.documents[idx[selected_idx]][:1000] + '.....')

        answer = prompt(Q.get_question(2))

        if answer['continue'] == "Continuer à lire":
            print(var.documents[idx[selected_idx]])
            article_choice()
        elif answer['continue'] == "Retour":
            article_choice()
        elif answer['continue'] == "Revenir au menu":
            Menu().lancement()
        else:
            print("BYE")
            sys.exit(2)
        
    article_choice()

def exact_macthes():
    
    answer = input("Search: ")
    #print("la valeur de k", var.K)
    try:
        queries_index(answer)
        Menu().lancement()
    except:
        print("Aucun document trouvé")

    Menu().lancement()



def main(k):
    #nombre optionnel
    var.K = k
    
    # on démarre sur l'écran accueil
    current_vue = Accueil()

    # tant qu'on a un écran à afficher, on continue
    while current_vue:
        # on affiche une bordure pour séparer les vue
        # with open('assets/border.txt', 'r', encoding="utf-8") as asset:
        #     print(asset.read())
        # les infos à afficher
        current_vue.display_info()
        
        # le choix que doit saisir l'utilisateur
        current_vue = current_vue.make_choice()

### creation de la varible Globale contenant les questions #########
Q = Questions()
