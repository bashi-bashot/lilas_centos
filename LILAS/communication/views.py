from django.shortcuts import render
from django.http import HttpResponse
from communication.models import *
from django.template import loader
from django.views import generic
from .forms import NameForm
# from .forms import StatSelectForm
from django import forms
from django.db.models import Q #Permet de faire des filtres complexes sur le queryset, notamment des OR.

# from .forms import secteurListe

from datetime import *
import pytz
import time

global GLOB_TAB_APPELS
global FORM_DATE
global GLOB_DATE_INIT
global GLOB_FORM_STATISTIQUES
global GLOB_DATE_END

GLOB_FORM_DATE = "XXX"
GLOB_FORM_STATISTIQUES = "XXX"
GLOB_TAB_APPELS = []
GLOB_DATE_INIT = datetime.now()
GLOB_DATE_END = datetime.now()

GLOB_TAB_SECT = [(1,"Tous secteurs"), (2,"A"),(3,"B"),(4,"C"),(5,"D"),] #Variable qui sauvegarde les choix du spinner Secteur dans formulaireDate
GLOB_TAB_CORREXTE = [(1,"Tous les correspondants")] #Variable qui sauvegarde les choix du spinner correspondants dans formulaireDate


#PENSER A CHANGER LES URLs POUR PASSER D'UNE METHODE A UNE AUTRE
#Partie sans les vues génériques
def index(request):
    #print("\n\n")
   
    
    #LISTE DE VARIABLES GLOBALES
    global GLOB_FORM_DATE #Formulaire où l'utilisateur choisit les dates entre lesquelles il veut afficher les appels
    global GLOB_FORM_STATISTIQUES #Formulaire où on choisit quelles statistiques affichées
    global GLOB_TAB_APPELS #Liste des appels affichés (ceux qui correspondent aux dates selectinnées
    global GLOB_DATE_INIT
    global GLOB_DATE_END
    global GLOB_TAB_SECT
    global GLOB_TAB_CORREXTE
    
    AppelListe = [] 
    tabExterieurs = NumExterieur.objects.all() #On récupère tous les numéros extérieurs
    tabSecteurs = NumSecteur.objects.all() #On récupère tous les secteurs
    tabNumExterieur = NumExterieur.objects.all()

    tabDatesNonEmpty = []
    #tabDatesNonEmpty = Date.objects.all()

    #for i in range(len(tampon)):
    #    tabDatesNonEmpty.append(tampon[i].date)
   
    
    listeDeTicket = []
    #formulaireDates = NameForm(request.POST, choice_list_sect = GLOB_TAB_SECT, choice_list_corr = GLOB_TAB_CORREXTE)
    formulaireDates = NameForm(request.POST)

    #Creation de la liste qui contient les dates selectionnables dans le datepicker
    bdd_datePicker = Date.objects.all()
    date__datePicker = []
    for i in range(len(bdd_datePicker)):
        #date__datePicker.append(strDate)
        tabDatesNonEmpty.append(bdd_datePicker[i].date.strftime("%d/%m/%Y"))

    # formulaireStatistiques = StatSelectForm(request.POST, )
    #---------------------------
    
    #1ère création du contexte
    context = {'AppelListe':AppelListe, 'form':formulaireDates, 'valid_date':date__datePicker, 'datesNonEmpty' : tabDatesNonEmpty} 
    
        
    if request.method == 'POST': #Si on a rempli un formulaire 
        
        if formulaireDates.is_valid(): #Si on a rempli le formulaire de choix de date / secteur / correspondant pour afficher les appels
            # process the data in form.cleaned_data as required
            #GLOB_FORM_DATES = formulaireDates
            print("FORMULAIRE DATE VALIDE")
            #a = formulaireDates.cleaned_data['dateDebut']
            #print(str(a))
            #AppelListe = Appel.objects.all()
            dateDeb = formulaireDates.cleaned_data['dateDebut'] #On récupère la dete de début entrée dans le formulaire
            dateF = formulaireDates.cleaned_data['dateFin'] #On récupère la dete de fin entrée dans le formulaire
            
            strHeureDebut = formulaireDates.cleaned_data['heureDebut'] #On récupère l'heure de début sous forme de chaine de caractère (pour le moment)
            strHeureFin = formulaireDates.cleaned_data['heureFin'] #On récupère l'heure de fin sous forme de chaine de caractère (pour le moment)
            
            print('/n/n****************************'+ strHeureDebut)
            
            #On crée ensuite les objets datetime de début et de fin
            date_time_deb = datetime( dateDeb.year, dateDeb.month, dateDeb.day, int(strHeureDebut[0:2]),int(strHeureDebut[3:5]), int(strHeureDebut[6:8])) #date naive
            date_time_fin = datetime( dateF.year, dateF.month, dateF.day, int(strHeureFin[0:2]), int(strHeureFin[3:5]), int(strHeureFin[6:8])) #date naive aussi
            
            timzeone = pytz.timezone('UTC') #Définition de la zone horaire pour rendre la date aware
            date_time_deb_aware = timzeone.localize(date_time_deb)
            date_time_fin_aware = timzeone.localize(date_time_fin)
            
            #On affecte les dates aux variables globales
            GLOB_DATE_INIT = date_time_deb_aware
            GLOB_DATE_END = date_time_fin_aware
            time1 = time.time()
            #------------------------------------------------------------------------------------------
                     #CREATION DE LA LISTE D'APPEL QUI CORRESPOND AUX DATES ENTREES DANS LE FORMULAIRE
            if(date_time_deb_aware.date() >  date_time_fin_aware.date()):
                
                return render(request, 'communication/index.html', context) #On recharge la page

            else :

                if (date_time_deb_aware.date() == date_time_fin_aware.date()) : # Si on regarde les appels que sur une seule journée
                    #On commence par regarder si la date entrée apparait dans notre bdd
                    listeDates = Date.objects.filter(date__exact = date_time_deb_aware.date())
                    if (listeDates.count() == 1) : #Si la date renseignée est dans la bdd
        
                        listeDates = Date.objects.filter(date__exact = date_time_deb_aware.date())[0].Appel.all() #Renvoie un queryset contenant tous les appels passés à la même date
                        listeDates = listeDates.filter(heure__lte = date_time_fin_aware.time(), heure__gte = date_time_deb_aware.time())
                        print("Selection des appels sur une seule journée")
                    else :
                        print("Date non existante dans la base de données")
                        listeDates = Date.objects.all()[0].Appel.all().filter(duree__gt=3000)
                        

                else : # Si on fait une recherche sur plusieurs jours
                    
                    #On répertorie toutes les dates entrées (>= 2 grace au if)
                    liste_de_dates = Date.objects.filter(date__gte = date_time_deb_aware.date(), date__lte = date_time_fin_aware.date()) #Est une liste de dates

                    listeDates = liste_de_dates[0].Appel.all().filter(heure__gte = date_time_deb_aware.time())
                    
                    for m in range(1, liste_de_dates.count()-1):
                        listeDates = listeDates | liste_de_dates[m].Appel.all()
                    
                    listeDates = listeDates | liste_de_dates[liste_de_dates.count()-1].Appel.all().filter(heure__lte = date_time_fin_aware.time())

                listeDates = listeDates.filter(duree__lt=1000)
                listeDates = listeDates.filter(duree__gt=0)

                #Pour le dernier jour, on ne prend que les appels passés avant l'heure de fin
                #QuerySetDateFinAppels =  liste_de_dates[liste_de_dates.count()-1].Appel.all()
                #QuerySetDateFinAppels.filter(heure__lte = date_time_fin_aware.time())
                #listeDates = listeDates|QuerySetDateFinAppels

                #time2 = time.time()
                #print(time2)
                #print("Durée initialisation appels :")
                #delta = time2 - time1
                #print(delta)
                
                #LISTEDATES contient tous les appels correspondants aux dates séléctionnées.
                #On affine cette liste en fonction du spinner de séléction de secteur
                
                #------------------------------------------------------------------------------------------
                        #RECUPERATION DU CHAMP DU MENU DEROULANT DE SELECTION DES SECTEURS

                strSecteur = formulaireDates.cleaned_data['positionSpinner']   
                choixSpinner = []
                for i in range(len(strSecteur)):
                    choixSpinner.append(formulaireDates.fields['positionSpinner'].choices[int(strSecteur[i])-1])

                #choixSpinner = formulaireDates.fields['positionSpinner'].choices[int(strSecteur[0])-1]

                print("strSecteur : "+strSecteur[0])
                print("choixSpinner : "+choixSpinner[0][1])
                
                #Il faut maintenant affiner la liste listeDates pour n'afficher que les appels faisant intervenit le secteur choisi
                #print(listeDates.count())
                secteurSelectionne = 0 #Vaut 0 si le menu déroulant de secteur est poisitionné sur "Tous Secteurs" et vaut 1 sinon
            
                    
                #------------------------------------------------------------------------------------------
                        #RECUPERATION DU CHAMP DU MENU DEROULANT DE SELECTION DES CORRESONDANTS ET AFFINAGE DE LA LISTE D'APPELS
                        
                strCorr = formulaireDates.cleaned_data['correspondantSpinner']
                choixSpinner_corr = [] #formulaireDates.fields['correspondantSpinner'].choices[int(strCorr)-1]
                for i in range(len(strCorr)):
                    choixSpinner_corr.append(formulaireDates.fields['correspondantSpinner'].choices[int(strCorr[i])-1])
                    
                #------------------------------------------------------------------------------------------
                        #POPULATION DU MENU DEROULANT DANS LEQUEL ON CHOISIT LE SECTEUR

                #Il faut maintenant construire le spinner du formulaire formulaireDates avec les secteur qui apparaissent dans les dates séléctionnées
                listeSecteursSpinner = [(1,"Tous secteurs")] #Contient tous les secteurs ayant été appelés / qui ont appelé sur la période séléctionnée FORMATE POUR LE SPINNER
                
                listeSect = [] #Contient tous les secteurs avec lesquels on va construire la suite du tuple précédent
            
                for appel in listeDates :
                    appelant = appel.nom_appelant
                    appele = appel.nom_appele
                    
                    if appelant not in listeSect :
                        for secteur in tabSecteurs :
                            if appelant == secteur.nom :
                                listeSect.append(appelant)
                                break
                                
                    if appele not in listeSect :
                        for secteur in tabSecteurs :
                            if appele == secteur.nom :
                                listeSect.append(appele)
                                break
                    
                            
                #Ici, listeSect contient le nom de tous les secteurs ayant intervenu sur la période séléctionnée.
                #On construit alors la liste de tuples à passer au Spinner
                
                for i in range(len(listeSect)):
                    p = (i+2, listeSect[i])
                    listeSecteursSpinner.append(p) #On a déjà le ((1,("Toute position"))). La suite continue à (2,...)

                    #On échange les deux éléments pour que le menu déroulant affiche le secteur choisi
                    #tamp = listeSecteursSpinner[0]
                    #listeSecteursSpinner[0] = listeSecteursSpinner[1]
                    #listeSecteursSpinner[1] = tamp

                
            
                #------------------------------------------------------------------------------------------
                        #POPULATION DU MENU DEROULANT DANS LEQUEL ON CHOISIT LE CORRESPONDANT

                #Il faut maintenant construire le spinner du formulaire formulaireDates avec les correspondants qui apparaissent dans les appels aux dates séléctionnées
                listeCorrespondantSpinner = [(1,"Tous les correspondants")] #Contient tous les correspondants ayant été appelés / qui ont appelé sur la période séléctionnée FORMATE POUR LE SPINNER
                listeCorresp = [] #Contient tous les correspondants avec lesquels on va construire la suite du tuple précédent
            
                for appel in listeDates :
                    appelant = appel.nom_appelant
                    appele = appel.nom_appele
                    
                    if appelant not in listeCorresp :
                        for corr in tabNumExterieur :
                            if appelant == corr.nom :
                                listeCorresp.append(appelant)
                                break
                                
                    if appele not in listeCorresp :
                        for corr in tabNumExterieur :
                            if appele == corr.nom :
                                listeCorresp.append(appele)
                                break
                    
                            
                #Ici, listeSect contient le nom de tous les secteurs ayant intervenu sur la période séléctionnée.
                #On construit alors la liste de tuples à passer au Spinner
                
                for i in range(len(listeCorresp)):
                    p = (i+2, listeCorresp[i])
                    listeCorrespondantSpinner.append(p) #On a déjà le ((1,("Toute position"))). La suite continue à (2,...)
                
                GLOB_TAB_SECT = listeSecteursSpinner
                GLOB_TAB_CORREXTE = listeCorrespondantSpinner
                
                #formulaireDates = NameForm(request.POST, choice_list_sect = listeSecteursSpinner, choice_list_corr = listeCorrespondantSpinner)

                #------------------------------------------------------------------------------------------
                        #AFFINAGE DE LA LISTE D'APPELS EN FONCTION DU -- SECTEUR -- ENREGISTRE

                #On cherche si dans la liste des secteurs choisis, on trouve "Tous secteurs" :
                toutSecteur = False
                for i in range(len(choixSpinner)):
                    if(choixSpinner[i][1] == "Tous secteurs") :
                        toutSecteur = True



                if not toutSecteur : #Si on a pas "Tous secteurs dans ce qu'a choisi l'utilisateur, on doit affiner, sinon, on en touche a rien"
                    print("AUTRE SECTEUR CHOISI")
                    listeDatesProvisoire = listeDates.filter((Q(nom_appelant=choixSpinner[0][1]) | Q(nom_appele=choixSpinner[0][1])))
                    if(len(choixSpinner) > 1):    
                        for i in range(1, len(choixSpinner)):
                            #print("SECTEUR CHOISI :"+choixSpinner[i])
                            listeDatesProvisoire = listeDatesProvisoire | listeDates.filter((Q(nom_appelant=choixSpinner[i][1]) | Q(nom_appele=choixSpinner[i][1]))) #On affine la liste d'appels
                            #secteurSelectionne = 1
                    listeDates = listeDatesProvisoire
                else :
                    print("TOUS SECTEURS")

                
                
                #------------------------------------------------------------------------------------------
                        #AFFINAGE DE LA LISTE D'APPELS EN FONCTION DU -- CORRESPONDANT -- ENREGISTRE
                toutCorres = False
                for i in range(len(choixSpinner_corr)):
                    if(choixSpinner_corr[i][1] == "Tous les correspondants") :
                        toutCorres = True

                if not toutCorres :
                    print("AUTRE CORRESPONDANT CHOISI")
                    listeDatesProvisoire = listeDates.filter(Q(nom_appelant=choixSpinner_corr[0][1]) | Q(nom_appele=choixSpinner_corr[0][1]))
                    if(len(choixSpinner_corr)>1):
                        for i in range(1, len(choixSpinner_corr)):
                            listeDatesProvisoire = listeDatesProvisoire | listeDates.filter((Q(nom_appelant=choixSpinner_corr[i][1]) | Q(nom_appele=choixSpinner_corr[i][1]))) #On affine la liste d'appels
                            
                    listeDates = listeDatesProvisoire

                #------------------------------------------------------------------------------------------
                        #CREATION DU TABLEAU DE STATISTIQUES
                #Par défaut, au premier affichage des statistique, le spinner est positionné sur "Indifférent"
                
                # listeStat = statistiquesIndifferent(listeDates)
                
                listeStat = []
                
                typeElement = formulaireDates.cleaned_data['selectionTypeSpinner']
                formulaireDates = NameForm(request.POST)
                
                if typeElement == '1' : #INDIFFERENT 
                    print("ENTREE DANS LE IF ELEMENT = 1")
                    listeStat = statistiquesIndifferent(listeDates)
                    
                if typeElement == '2' : #SECTEUR
                    print("ENTREE DANS LE IF ELEMENT = 2")
                #On récupère tous les secteurs qui sont intervenus dans les dates séléctionnées
                
                    listeSecteurs = [] #Contient tous les secteurs avec lesquels on va construire la suite du tuple précédent
                
                    for appel in listeDates :
                        appelant = appel.nom_appelant
                        appele = appel.nom_appele
                        
                        #On commence à regarder l'appelant
                        if appelant not in listeSecteurs : #Si l'appelant ne figure pas déjà dans la liste de secteurs déjà établie
                        
                            for secteur in tabSecteurs :   #On regarde si c'est un secteur 
                                if appelant == secteur.nom :    #Si c'est un secteur
                                    listeSecteurs.append(appelant)  #On l'ajoute à la liste de secteurs 
                                    listeStat.append([appelant])    #On l'ajoute à la liste de statistiques (On ajoute le tableau cotnenant le nom du secteur
                                    #Que ce soit un secteur qu'on avait pas encore rencontré ou pas on fait le traitement suivant :
                                    indice = listeSecteurs.index(appelant) #On récupère l'indice de listeSecteurs où on vient de l'ajouter. On trouve les statistiques de ce secteur dans listeStat au même indice
                                    for p in range(5): #On intiialise les statistiques à 0 pour ce secteru
                                        listeStat[indice].append(0)
                                    #listeStat[indice] est maintenant un tableau à 6 colonnes
                                    
                                    #On incrémente le nombre d'appels
                                    listeStat[indice][1] = listeStat[indice][1]+1
                                    listeStat[indice][2] = listeStat[indice][2] + appel.duree
                                    if appel.etat == 'SATURATION_DEP' or appel.etat == 'DEST N JOIGNABLE':
                                            listeStat[indice][3] = listeStat[indice][3] + 1
                                    else :
                                            if appel.etat == 'NON_REPONSE' or appel.etat == 'DEST_OCCUPEE':
                                                listeStat[indice][4] = listeStat[indice][4] + 1
                                    break #On sort de la boucle 
                        else :
                            indice = indice = listeSecteurs.index(appelant) #On récupère l'indice de listeSecteurs où on vient de l'ajouter. On trouve les statistiques de ce secteur dans listeStat au même indice
                            #On incrémente le nombre d'appels
                            listeStat[indice][1] = listeStat[indice][1]+1
                            listeStat[indice][2] = listeStat[indice][2] + appel.duree
                            if appel.etat == 'SATURATION_DEP' or appel.etat == 'DEST N JOIGNABLE':
                                    listeStat[indice][3] = listeStat[indice][3] + 1
                            else :
                                    if appel.etat == 'NON_REPONSE' or appel.etat == 'DEST_OCCUPEE':
                                        listeStat[indice][4] = listeStat[indice][4] + 1


                                        
                        #On commence à regarder l'appele
                        if appele not in listeSecteurs : #Si l'appelant ne figure pas déjà dans la liste de secteurs déjà établie
                            
                            for secteur in tabSecteurs :   #On regarde si c'est un secteur 
                                if appele == secteur.nom :    #Si c'est un secteur
                                    listeSecteurs.append(appele)  #On l'ajoute à la liste de secteurs 
                                    listeStat.append([appele])    #On l'ajoute à la liste de statistiques (On ajoute le tableau cotnenant le nom du secteur
                                    #Que ce soit un secteur qu'on avait pas encore rencontré ou pas on fait le traitement suivant :
                                    indice = listeSecteurs.index(appele) #On récupère l'indice de listeSecteurs où on vient de l'ajouter. On trouve les statistiques de ce secteur dans listeStat au même indice
                                    for p in range(5): #On intiialise les statistiques à 0 pour ce secteru
                                        listeStat[indice].append(0)
                                    #listeStat[indice] est maintenant un tableau à 6 colonnes
                                    
                                    #On incrémente le nombre d'appels
                                    listeStat[indice][1] = listeStat[indice][1]+1
                                    listeStat[indice][2] = listeStat[indice][2] + appel.duree
                                    if appel.etat == 'SATURATION_DEP' or appel.etat == 'DEST N JOIGNABLE':
                                            listeStat[indice][3] = listeStat[indice][3] + 1
                                    else :
                                            if appel.etat == 'NON_REPONSE' or appel.etat == 'DEST_OCCUPEE':
                                                listeStat[indice][4] = listeStat[indice][4] + 1        
                                    break
                        else :
                            indice = indice = listeSecteurs.index(appele) #On récupère l'indice de listeSecteurs où on vient de l'ajouter. On trouve les statistiques de ce secteur dans listeStat au même indice
                            #On incrémente le nombre d'appels
                            listeStat[indice][1] = listeStat[indice][1]+1
                            listeStat[indice][2] = listeStat[indice][2] + appel.duree
                            if appel.etat == 'SATURATION_DEP' or appel.etat == 'DEST N JOIGNABLE':
                                    listeStat[indice][3] = listeStat[indice][3] + 1
                            else :
                                    if appel.etat == 'NON_REPONSE' or appel.etat == 'DEST_OCCUPEE':
                                        listeStat[indice][4] = listeStat[indice][4] + 1
                        
                                
                
                if typeElement == '3' : #LIGNE 
                    #On construit le tableau à afficher dans le tableau stats
                    print("ENTREE DANS LE IF ELEMENT = 3")
                    
                    listeLignes = [] #Liste dans laquelle on répertorie toutes les lignes qui ont été sollicitées. C'est dans cette liste qu'on vérifie si on acroisé telle ligne
                    #ATTENTION : Les lignes de listeLignes et de listeStat sont EXACTEMENT dans le même ordre. Rechercher l'indice d'une ligne dans listeLignes revient donc à chercher
                    #l'indice de listeStats où on a stocké les stats de la dite ligne
                    
                
                    
                    for u in listeDates :
                        #u est un Appel
                    
                        if (u.type == 'ENTRANT') :
                            if(u.line_appelante not in listeLignes):
                                listeLignes.append(u.line_appelante)
                                listeStat.append([u.line_appelante])
                                
                            #On récupère l'indice de listeLignes (et donc de listeStat) auquel on trouve la LIF
                            indice = listeLignes.index(u.line_appelante)
                            #On remplit les stats de la ligne de 0
                            for p in range(5):
                                listeStat[indice].append(0)
                                    
                            #On incrémente le nombre d'appel sur la dite ligne
                            listeStat[indice][1] = listeStat[indice][1] + 1 
                            
                            #On ajoute la durée de l'appel
                            listeStat[indice][2] = listeStat[indice][2] + u.duree 
                            
                            if u.etat == 'SATURATION_DEP' or u.etat == 'DEST N JOIGNABLE':
                                listeStat[indice][3] = listeStat[indice][3] + 1
                            else :
                                if u.etat == 'NON_REPONSE' or u.etat == 'DEST_OCCUPEE':
                                    listeStat[indice][4] = listeStat[indice][4] + 1
                            
                            
                                
                        elif (u.type == 'SORTANT') :
                            if(u.line_appele not in listeLignes):
                                listeLignes.append(u.line_appele)
                                listeStat.append([u.line_appele])
                                
                            #On récupère l'indice de listeLignes (et donc de listeStat) auquel on trouve la LIF
                            indice = listeLignes.index(u.line_appele)
                                    
                            #On remplit les stats de la ligne de 0
                            for p in range(5):
                                listeStat[indice].append(0)
                                    
                            #On incrémente le nombre d'appel sur la dite ligne
                            listeStat[indice][1] = listeStat[indice][1] + 1 
                            
                            #On ajoute la durée de l'appel
                            listeStat[indice][2] = listeStat[indice][2] + u.duree 
                            
                            if u.etat == 'SATURATION_DEP' or u.etat == 'DEST N JOIGNABLE':
                                listeStat[indice][3] = listeStat[indice][3] + 1
                            else :
                                if u.etat == 'NON_REPONSE' or u.etat == 'DEST_OCCUPEE':
                                    listeStat[indice][4] = listeStat[indice][4] + 1
                                    
                                    
                            
                        elif (u.type == 'TRANSIT') :
                            if(u.line_appele not in listeLignes):
                                listeStat.append([u.line_appele])
                                listeLignes.append(u.line_appele)
                                
                            if(u.line_appelante not in listeLignes):
                                listeStat.append([u.line_appelante])
                                listeLignes.append(u.line_appelante)
                                
                            #On récupère l'indice de listeLignes (et donc de listeStat) auquel on trouve les LIFs
                            indice1 = listeLignes.index(u.line_appele)
                            indice2 = listeLignes.index(u.line_appelante)
                            
                                                
                            #On remplit les stats de la ligne de 0
                            for p in range(5):
                                listeStat[indice1].append(0)
                                listeStat[indice2].append(0)
                                    
                            #On incrémente le nombre d'appel sur la dite ligne
                            listeStat[indice1][1] = listeStat[indice1][1] + 1 
                            listeStat[indice2][1] = listeStat[indice2][1] + 1 
                            
                            #On ajoute la durée de l'appel
                            listeStat[indice1][2] = listeStat[indice1][2] + u.duree 
                            listeStat[indice2][2] = listeStat[indice2][2] + u.duree 
                            
                            #On incrémente le nombre d'échec si c'est un échec
                            if u.etat == 'SATURATION_DEP' or u.etat == 'DEST N JOIGNABLE':
                                listeStat[indice1][3] = listeStat[indice1][3] + 1
                                listeStat[indice2][3] = listeStat[indice2][3] + 1
                            
                            #On incrémente le nombre de refus si c'est un refus
                            else :
                                if u.etat == 'NON_REPONSE' or u.etat == 'DEST_OCCUPEE':
                                    listeStat[indice1][4] = listeStat[indice1][4] + 1
                                    listeStat[indice2][4] = listeStat[indice2][4] + 1
                                    
                                #fin if
                            #fin else 
                        #fin elif
                    #fin for
                        
                    
                
                if typeElement == '4' : #FAISCEAU 
                    print("ENTREE DANS LE IF ELEMENT = 4")
                    listeFaisceaux = [] #Liste dans laquelle on va répertorier tous les faisceaux rencontrés
                    indice_entrant = -1
                    indice_sortant = -1

                    listeMaxOccupation = []
                    
                    for appel in listeDates :
                        if appel.fx_entrant != 'fx_xxxx_e' : #On s'occupe de FX_ENTRANT
                            if appel.fx_entrant not in listeFaisceaux :
                                listeStat.append([appel.fx_entrant])
                                listeFaisceaux.append(appel.fx_entrant)
                                for o in range(5) :
                                    listeStat[-1].append(0)
                                indice_entrant = len(listeFaisceaux)-1
                            else :
                                #On récupère l'indice de listeFaisceaux auquel on a notre appel
                                indice_entrant = listeFaisceaux.index(appel.fx_entrant)
                                
                            listeStat[indice_entrant][1] = listeStat[indice_entrant][1] + 1 #NbAppel
                            listeStat[indice_entrant][2] = listeStat[indice_entrant][2] + appel.duree #DureeCumulée
                            if appel.etat == 'SATURATION_DEP' or appel.etat == 'DEST N JOIGNABLE':
                                listeStat[indice_entrant][3] = listeStat[indice_entrant][3] + 1 #ECHEC
                            else :
                                if appel.etat == 'NON_REPONSE' or appel.etat == 'DEST_OCCUPEE':
                                    listeStat[indice_entrant][4] = listeStat[indice_entrant][4] + 1 #REFUS
                                    
                        if appel.fx_sortant != 'fx_xxxx_a' :
                            #On s'occupe de FX_SORTANT
                            if appel.fx_sortant not in listeFaisceaux :
                                listeStat.append([appel.fx_sortant])
                                listeFaisceaux.append(appel.fx_sortant)
                                for o in range(5) :
                                    listeStat[-1].append(0)
                                indice_sortant = len(listeFaisceaux)-1
                            else :
                                #On récupère l'indice de listeFaisceaux auquel on a notre appel
                                indice_sortant = listeFaisceaux.index(appel.fx_sortant)
                            listeStat[indice_sortant][1] = listeStat[indice_sortant][1] + 1 #NbAppel
                            listeStat[indice_sortant][2] = listeStat[indice_sortant][2] + appel.duree #DureeCumulée
                            if appel.etat == 'SATURATION_DEP' or appel.etat == 'DEST N JOIGNABLE':
                                listeStat[indice_sortant][3] = listeStat[indice_sortant][3] + 1 #ECHEC
                            else :
                                if appel.etat == 'NON_REPONSE' or appel.etat == 'DEST_OCCUPEE':
                                    listeStat[indice_sortant][4] = listeStat[indice_sortant][4] + 1 #REFUS

                    #Ont trie les appels par date croissante par faisceaux :
                    listeAppelsParFaisceaux = [0]*len(listeFaisceaux)
                    for i in range(len(listeAppelsParFaisceaux)):
                        listeAppelsParFaisceaux[i] = []
                        
                    for appel in listeDates :
                        if appel.duree != 0 : #On enlève tous les appels de 0s pour l'occupation faisceaux
                            #On memorise les indice de listeFaisceaux correspondant aux faisceaux entrants et sortants de l'appel
                            ind_entrant = -1
                            ind_sortant = -1
                            if appel.fx_entrant in listeFaisceaux :
                                ind_entrant = listeFaisceaux.index(appel.fx_entrant)
                            if appel.fx_sortant in listeFaisceaux :
                                ind_sortant = listeFaisceaux.index(appel.fx_sortant)
                            #On ajoute maintenant l'appel à listeAppelsParFaisceaux au bon indice
                            if(ind_entrant != -1) :
                                listeAppelsParFaisceaux[ind_entrant].append(appel)
                            if(ind_sortant != -1) :
                                listeAppelsParFaisceaux[ind_sortant].append(appel)
                            
                    #------------------------------
                    

                    #print("Calcul de l'occupation Faisceau :")
                    #print("Remplissage du tableau de calcul")
                    for i in range(len(listeAppelsParFaisceaux)): #Pour chaque faisceau
                        tabJalons = [] #Une table pour un faisceau
                        for appel in listeAppelsParFaisceaux[i] :
                            dateDebAppel = appel.date
                            heureDebAppel = appel.heure
                            datetimeDebAppel = datetime(int(str(dateDebAppel)[0:4]),int(str(dateDebAppel)[5:7]),int(str(dateDebAppel)[8:10]),heureDebAppel.hour,heureDebAppel.minute, heureDebAppel.second)
                            datetimeFinAppel = datetimeDebAppel + timedelta(seconds=appel.duree)
                            ouverture=(datetimeDebAppel, 0)
                            fermeture = (datetimeFinAppel, 1)
                            tabJalons.append(ouverture)
                            tabJalons.append(fermeture)
                        
                        #print("Tri des jalons du faisceau en cours")
                        tabJalons.sort()
                        print("Tri de la table de jalons : ")
                        #for l in range(len(tabJalons)):
                        #    print("FLAG : FAISCEAU : "+listeFaisceaux[i]+" Debut Appel numero "+str(l)+" : "+str(tabJalons[0]))

                        #print("Calcul de l'occupation faisceau")
                        compteur_max = 0 #Compteur du nb de fois que l'occurrence max est atteinte
                        simultMax = 0
                        simult = 0
                        duree = 0 #Duree pendant laquelle le nb max d'appels simultanés sur la période est atteint
                        listeMaxOccupation = []
                        for j in range(len(tabJalons)) :
                            if(tabJalons[j][1] == 0): #Début d'appel
                                simult = simult + 1
                                if(simult > simultMax): #On reset les variables
                                    simultMax = simult
                                    listeMaxOccupation = []
                                    duree = 0
                                    compteur_max = 1
                                elif(simult == simultMax):
                                    compteur_max = compteur_max + 1
                            elif(tabJalons[j][1] == 1): #Fin d'appel
                                if(simult == simultMax) :
                                    #On calcule la durée qui s'est écoulée depuis le dernier jalon
                                    p = j
                                    while(p>0): #On recherche le précédent début d'appel
                                        if(tabJalons[p-1][1] == 0) :
                                            delta = (tabJalons[j][0] - tabJalons[p-1][0]).total_seconds()
                                            #if(delta != 0):
                                            duree += delta
                                            listeMaxOccupation.append((tabJalons[p-1][0], (tabJalons[j][0] - tabJalons[p-1][0]).total_seconds()))
                                            break
                                        p = p - 1
                                simult = simult - 1
                        if(len(listeMaxOccupation) <= 5):
                            for l in range(len(listeMaxOccupation)):
                                print("FLAG : FAISCEAU : "+listeFaisceaux[i]+" Debut occurrence "+str(l)+" : "+str(listeMaxOccupation[l][0])+" --> Duree : "+str(listeMaxOccupation[l][1]))
                                pass
                                
                        #print("Ecriture de l'occupation faisceau")
                        listeStat[i][5] = (simultMax, compteur_max, duree)
                        
                        
                            
                    #------------------------------


                if typeElement == '5' : #SU + TP 
                    print("ENTREE DANS LE IF ELEMENT = 5")
                    listeStat.append(["SU + TP"])#Alors on renseigne la première ligne de listeStat qui est la seule ligne dans laquelle on entre les stats de SU+TP
                    for o in range(5):
                        listeStat[0].append(0)
                                    
                    for appel in listeDates :
                        if appel.SUTP == True :                       
                            listeStat[0][1] = listeStat[0][1] + 1 #NbAppel
                            listeStat[0][2] = listeStat[0][2] = appel.duree #Durée cumulée
                            
                            if appel.etat == 'SATURATION_DEP' or appel.etat == 'DEST N JOIGNABLE':
                                listeStat[0][3] = listeStat[0][3] + 1 #ECHEC
                            else :
                                if appel.etat == 'NON_REPONSE' or appel.etat == 'DEST_OCCUPEE':
                                    listeStat[0][4] = listeStat[0][4] + 1 #REFUS
                
                if typeElement == '6' : #SECOURS SDA 
                    print("ENTREE DANS LE IF ELEMENT = 6")
                    listeStat.append(["Secours Numeris"])#Alors on renseigne la première ligne de listeStat qui est la seule ligne dans laquelle on entre les stats de SU+TP
                    for o in range(5):
                        listeStat[0].append(0)
                                    
                    for appel in listeDates :
                        if appel.SDA == True :                       
                            listeStat[0][1] = listeStat[0][1] + 1 #NbAppel
                            listeStat[0][2] = listeStat[0][2] + appel.duree #Durée cumulée
                            
                            if appel.etat == 'SATURATION_DEP' or appel.etat == 'DEST N JOIGNABLE':
                                listeStat[0][3] = listeStat[0][3] + 1 #ECHEC
                            else :
                                if appel.etat == 'NON_REPONSE' or appel.etat == 'DEST_OCCUPEE':
                                    listeStat[0][4] = listeStat[0][4] + 1 #REFUS
                                    
                if typeElement == '7' : #NUMERO INCONNU 
                    print("ENTREE DANS LE IF ELEMENT = 7")
                    listeStat.append(["Appels non libellés"])
                    for o in range(5):
                        listeStat[0].append(0)
                        
                    #APPELANT
                    for appel in listeDates :
                        if appel.appelant == appel.nom_appelant :
                            listeStat[0][1] = listeStat[0][1] + 1
                            listeStat[0][2] = listeStat[0][2] + appel.duree
                            
                            if appel.etat == 'SATURATION_DEP' or appel.etat == 'DEST N JOIGNABLE':
                                listeStat[0][3] = listeStat[0][3] + 1 #ECHEC
                            else :
                                if appel.etat == 'NON_REPONSE' or appel.etat == 'DEST_OCCUPEE':
                                    listeStat[0][4] = listeStat[0][4] + 1 #REFUS
                                    
                        else :
                            print("Numero :"+appel.appelant)
                            print("Nom :"+appel.nom_appelant)
                                
                        if appel.appele == appel.nom_appele :
                            listeStat[0][1] = listeStat[0][1] + 1
                            listeStat[0][2] = listeStat[0][2] + appel.duree
                            
                            if appel.etat == 'SATURATION_DEP' or appel.etat == 'DEST N JOIGNABLE':
                                listeStat[0][3] = listeStat[0][3] + 1 #ECHEC
                            else :
                                if appel.etat == 'NON_REPONSE' or appel.etat == 'DEST_OCCUPEE':
                                    listeStat[0][4] = listeStat[0][4] + 1 #REFUS
                
                        else :
                            print("Numero :"+appel.appele)
                            print("Nom :"+appel.nom_appele)
                
                
                #Calcul du taux d'occupation
                    #On récupère les dates sur lesquelles on a les statistiques. La durée de cette période entre en compte dans le calcul du taux d'occupation
                    
                    
                duréeTotale = (GLOB_DATE_END - GLOB_DATE_INIT).total_seconds()
                #for i in range(len(listeStat)):
                    #tauxTemporaire = (listeStat[i][2]/duréeTotale)
                    #if (tauxTemporaire < 0.0001) : # ATTENTION !!! Valeur arbitraire. Il faudra probablement la changer !!!
                        #tauxTemporaire = 0
                    #listeStat[i][5] = tauxTemporaire
                
                
                #print(len(listeStat))
                
                
                context = {'AppelListe':listeDates, 'form':formulaireDates, 'ListeStats':listeStat, 'valid_date':date__datePicker, 'datesNonEmpty' : tabDatesNonEmpty} #, 'ListeStats':listeStat
                

                # context = {'AppelListe':listeDates,'form':formulaireDates, 'statForm':formulaireStatistiques, 'ListeStats':listeStat} 
                
                
                #On sauvegarde le formulaire et les appels dans une variable globale
                GLOB_FORM_DATE = formulaireDates
                #a = formulaireDates.cleaned_data['dateDebut']
                #print("*****************"+str(a))

                # GLOB_FORM_STATISTIQUES = formulaireStatistiques
                
                # print("----------------------------")
                # print("Nombre d'appels après sauvegarde :")
                # print(len(GLOB_TAB_APPELS))
                # print("----------------------------")

                # redirect to a new URL:
                return render(request, 'communication/index.html', context) #On recharge la page

        

   #     if formulaireStatistiques.is_valid():

   #         print("FORMULAIRE STATISTIQUES VALIDE")
   #         GLOB_FORM_STATISTIQUES = formulaireStatistiques
   #         # typeElement = formulaireStatistiques.cleaned_data['selectionTypeSpinner']
            
  #          print("********************")
  #          print("STATS : Nombre d'appels :")
  #          print(len(GLOB_TAB_APPELS))
  #          print("********************")



 #           print("********************")
 #           print("STATS : Nombre d'appels - listeDates:")
 #           print(len(context['AppelListe']))
 #           print("********************")

           
             
            

#            return render(request, 'communication/index.html', context) #On recharge la page

            
            
        #else :
            #Dans le cas où le formulaire n'est pas correct
            
            #Il faudrait ajouter un champ dans contexte qui contient une chaine de caractère du genre "Il est nécessaire de remplir tous les champs" 
            #puis de faire un test dans le html juste en dessous du formulaire tel que "Si ce champ de contexte existe, alors l'afficher,
            #sinon, ne pas l'afficher"
            
            #A ce moment là on a plus besoin de contexte juste avant "if form.is_valid():"

            #render(request, 'incident/index.html') #provisoire
            
    #else : #Dans le cas où on a pas récupéré un POST 
       
        #context = {'AppelListe':listeDates, 'form':formulaireDates} #Je pense que cette ligne est inutile
    
    return render(request, 'communication/index.html', context)
    

def statistiquesIndifferent(tab):
    """Fonction qui prend en entrée la liste avec tous les appels sur la periode selectionnée et 
    retourne un tuple 
    (Nb appel, Durée cumulée, Nb Echecs, Nb refus, Taux occupation)
    """
    
    #Pour les stats
    dureeCumulee = 0
    nombreEchec = 0
    nombreRefus = 0
    tauxOccupation = 0
    
    
    
    #Statistiques sur TOUS les appels sans recoupe
    listeStat = []
    # listeStat.append("")
    nbAppels = len(tab)
    
    #On fait une liste qui parcours les appels :
    for u in tab :
        #On calcule la durée cumulée 
        dureeCumulee = dureeCumulee + u.duree 
        
        #On regarde si c'est un echec
        
        if u.etat == 'SATURATION_DEP' or u.etat == 'DEST N JOIGNABLE':
            nombreEchec = nombreEchec + 1
        else :
            if u.etat == 'NON_REPONSE' or u.etat == 'DEST_OCCUPEE':
                nombreRefus = nombreRefus + 1
            
    listeEphemere = []
    listeEphemere.append("Indifférent")    
    listeEphemere.append(nbAppels)
    listeEphemere.append(dureeCumulee)
    listeEphemere.append(nombreEchec)
    listeEphemere.append(nombreRefus)
    listeEphemere.append(tauxOccupation)
    listeStat.append(listeEphemere)
    
    return listeStat
