# Indexation web

Ce projet porte sur la création d'un mini moteur de recherche comme google. Elle se base sur un ensemble de documents existant dans un corpus (documents disponibles sur les sites internet par exemple) pour afficher les résultats d'une requête par ordre de pertinence.


- Le notebook **TP_indexation_final_version** contient toutes les étapes de préprocessing des textes et modélisations nécessaires pour créer ce moteur d'indexation web.

## Nettoyage du texte
- supprimer les ponctuations à cause de leur apparition dans tous les langages
- supprimer les mots qui n'ont qu'un seul caractère car une seule lettre n'est d'aucune utilité pour identifier un document
- remettre tous les mots en miniscule afin d'éviter la sensibilité à la casse des mots du vocabulaire
transformer les chiffres d'un document en lettre (1000 --> 'one thousand')
- supprimer les stop_words de la langue anglaise contenant les mots usuels utilisés fréquemment dans la langue (ex: my, our, them, etc..)
- faire de la lemmatisation

## Indexation et requêtes
- Création de l'index graâce à un dictionnaire contenant toutes les informations des documents
- Parallélisation du process d'indexation (multiprocessing et map reduce)
- Création de différents types de requêtes (simples, personnalisés, avancés,...)
- Vectorisation, TFDIDF et autres modèles pour le ranking des résultats

## Application
Le fichier **indexation.py** dans le dossier "Application" permet de lancer une interface pour tester en temps réel le projet. Il suffit de lancer `python indexation.py` dans un terminal pour démérrer le moteur de recherche sous forme d'interface où la navigation est gérée grâce aux directions du clavier. Enjoy 😃 !
