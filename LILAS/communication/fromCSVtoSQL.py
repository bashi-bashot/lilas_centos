#Algorithme qui sert a trier les tickets de COMMUNICATION
#Extraire les champs importants
#Utiliser les fonctionnalites Django pour creer la base de donnees

from communication.models import *

from django.conf import settings
from datetime import datetime

import time



def main():
    #On ouvre le fichier contenant les tickets
    fic = open(settings.MEDIA_ROOT+"/tickets_comm.csv", 'r', encoding='latin1')
    t = fic.readlines() #on stock dans t toutes les lignes du fichier de tickets --> Chaque ligne EST un ticket
    fic.close() #On ferme le flux
    #print(t[0])
    u = [] #u est comme t, a la difference que chaque colonne est un champ du ticket
    
    for i in range(len(t)): #On parcourt tous les tickets ----- len(t)
        u.append(t[i].split(",")) #On separe les champs du ticket
    return u
    
    
def createAppel(t, listeLif):
    #Fonction qui cree un tableau a 8 cases 
    #t=[appelant, appele, date, type, duree, liberation, line_appelante, line_appelee, etat, fsx_entrant, fsx_sortant, Commentaire(Debord Num ou SU+TP]
    #t=[27,       28,     23,   25,   calcul,        30,               ,             ,   29,         xxx,         xxx,                              31]
    
    tabExterieurs = NumExterieur.objects.all() #On recupere tous les numeros exterieurs
    tabSecteurs = NumSecteur.objects.all() #On recupere tous les numeros de secteurs
    import pytz #import ici sinon, ca ne marche pas
    timzeone = pytz.timezone('UTC') #Definition de la zone horaire pour rendre la date aware
    
    
    
    for k in range(len(t)):
        print(k)
        
        #On recupere la date au champ 23
        texteDate = t[k][23].replace('"','')
        texteDateFin = t[k][24].replace('"','')

        #-------------------------------------------------------------------------------------------
        
        #On recupere le nom du joncteur et de l'appelant
        # str = t[k][27][1:-1].replace(" ","") # de la forme -->     Appelant : [PTEL] - EPOS_127              337070   Il faut doint enlever les espaces pour faire le traitement
        # applant = str[len(str)-6:len(str)] #ATTENTION Parfois, le numero appelant est simplement 0. Si on recupere les 6 derniers caracteres, on se retrouve avec un bout de joncteur. --> Si on trouve une lettre dans "appelant" alors il n'a a pas 6 numeros
        # fsx_e = str[9:len(str)-6] # Le faisceau est tout le reste

        #Pour eviter les problemes dans le cas d'un numero qui a moins de 6 chiffres, on peut faire le test suivant :
        #Si on rencontre plus de 5 espace a la fois --> Alors le premier caractere qui n'est pas un espace qui suit est le premier chiffre du numero de telephone

        
        str = t[k][27].replace('"','')
        compteur_espace = 0
        indice_separation = 0
        for l in range(len(str)):
            if(str[l] == ' '):
                compteur_espace = compteur_espace + 1

                if(compteur_espace >= 4 ):
                    #On est dans a l'indice d'un espace entre le joncteur et le numero
                    indice_separation = l+1
                    break

            else:
                compteur_espace = 0
            
            
        
        l = indice_separation
        while (str[l] == ' '): 
            l = l+1
            if(str[l] != ' '):
                #On a rencontre le numero
                applant = str[l:len(str)]
                fsx_e = str[11:indice_separation-4]
        
        #-------------------------------------------------------------------------------------------
        
        #On recupere le nom du joncteur et de l'appele
        # str2 = t[k][28][1:-1].replace(" ","")
        # apple = str2[len(str2)-6:len(str2)]
        # fsx_a = str2[7:len(str2)-6]
        
        str2 = t[k][28].replace('"','')
        
        compteur_espace = 0
        indice_separation = 0
        for l in range(len(str2)):
            if(str2[l] == ' '):
                compteur_espace = compteur_espace + 1

                if(compteur_espace >= 4 ):
                    #On est dans a l'indice d'un espace entre le joncteur et le numero
                    indice_separation = l+1
                    break

            else:
                compteur_espace = 0
            
            
        
        l = indice_separation
        while (str2[l] == ' '): 
            l = l+1
            if(str2[l] != ' '):
                #On a rencontre le numero
                apple = str2[l:len(str2)]
                fsx_a = str2[9:indice_separation-4]
        
        #On calcule maintenant la duree de l'appel
        
        
        d = datetime(int(texteDate[6:8])+2000,int(texteDate[3:5]),int(texteDate[0:2]),int(texteDate[9:11]),int(texteDate[12:14]),int(texteDate[15:17]))
        dfin = datetime(int(texteDateFin[6:8])+2000,int(texteDateFin[3:5]),int(texteDateFin[0:2]),int(texteDateFin[9:11]),int(texteDateFin[12:14]),int(texteDateFin[15:17]))
        
        d = timzeone.localize(d)
        dfin = timzeone.localize(dfin)

        #On crze la date de l'appel dans la table Date si elle n'existe pas
        date_a_sauvegarder = Date(date = d.date())
        print("DETAIL AVANT : "+date_a_sauvegarder)
        
        if Date.objects.all().filter(date__exact=d.date()).count() == 1 :
            date_a_sauvegarder = Date.objects.all().filter(date__exact=d.date())[0]
        else :
            date_a_sauvegarder.save()
            
            

        #if Appel.objects.filter(date__date__contains=d.date(), heure__contains=d.time(), appelant__contains=apple, line_appelante__contains=fsx_e, appele__contains=applant, line_appele__contains=fsx_a).count()==1:
        #if Appel.objects.filter(date__date__contains=d.date()).filter(heure__contains=d.time()).filter(appelant__contains=apple).filter(line_appelante__contains=fsx_e).filter(appele__contains=applant).filter(line_appele__contains=fsx_a).count()==1:
        #    print("Doublon :"+d.__str__()+" "+applant+" "+apple)
        #    pass

        #-------------------------------- RECHERCHE DE DOUBLON -------------------------------------------------------------

        #On sait que l'appelle a été passé à : date_a_sauvegarder
        #On ne regarde donc que les appels de date_a_sauvegarder

        print("DETAIL : "+date_a_sauvegarder)
        if date_a_sauvegarder.Appel.all().filter(heure__exact=d.time()).filter(appelant__exact=apple).filter(line_appelante__exact=fsx_e).filter(appele__exact=applant).filter(line_appele__exact=fsx_a).count()>0:
            print("Doublon :"+d.__str__()+" "+applant+" "+apple)
        else:

            print("Heure :"+d.time()+" "+applant+" "+apple)
            dur = dfin - d #dur n'est pas un objet datetime, mais un objet timedelta
            
            #Traitemeent sur le champ "ETAT" du ticket : On ne regarde pas ce qui suit 'en'
            
            chaineTemoin = 'en'
            chaineATraiter = t[k][29][17:-1]
            etatAppel = ''
            
            for i in range(len(chaineATraiter)-1):
                if (chaineATraiter[i:i+2] == chaineTemoin):
                    etatAppel = chaineATraiter[0:i-1]
                    break
                    
            #On cherche maintenant le nom associe aux numeros dans les annuaires
            
            
            num_appelant = applant
            num_appele = apple
            
            nomAppelant =""
            nomAppele=""
                    
                    
            #On regarde si ces deux numeros apparaissent dans la liste des numeros exterieurs ou des numeros de secteurs (tabSecteurs et tabExterieurs sont intialises en debut de fonction)
            for j in range(len(tabExterieurs)):
                if num_appelant == tabExterieurs[j].numero :
                    nomAppelant = tabExterieurs[j].nom
                    
                    
                if num_appele == tabExterieurs[j].numero :
                    nomAppele = tabExterieurs[j].nom
                    
                
            for j in range(len(tabSecteurs)):
                if num_appelant == tabSecteurs[j].numero :
                    nomAppelant = tabSecteurs[j].nom
                    
                    
                if num_appele == tabSecteurs[j].numero :
                    nomAppele = tabSecteurs[j].nom
                    
            #Si on a pas trouve de correspondance, on recopie le numero dans l'intitule 
            if nomAppelant == "" :
                nomAppelant = applant
                
            if nomAppele == "" :
                nomAppele = apple
                
            #On recupere maintenant "les faisceaux" a partir des lignes ATTENTION, il s'agiti ici de la LIF et non pas du faisceau
            #fsx_e est la ligne appelante de la forme "[VoIP] - 7H_3_VoIP"
            #fsx_a est la ligne appelee de la forme "[VoIP] - 7H_3_VoIP"
            
            
            
            ligne1 = fsx_e
            ligne2 = fsx_a
            faisceauAppelant = 'fx_xxxx_a'
            faisceauAppele = 'fx_xxxx_e'
            indiceTiret = -1
            indiceFin = -1
            
            #LIGNE - 1
            for i in range(len(ligne1)):
                if ligne1[i] == '-' :
                    indiceTiret = i
                    break
            #l'indice i est '-', l'indice i+1 est ' ' et l'indice i+2 est le debut de l'intitule de la ligne
            # print("indiceTiret :"+str(indiceTiret))

            if(indiceTiret != -1):
                ligne1 = ligne1[i+2:len(ligne1)] #linge1 vaut la chaine exacte de la carte LIF
                ligne1 = ligne1.replace(" ", "") #On enleve les espaces
                for p in listeLif : #On cherche maintenant une correspondance dans nos LIFs
                    if p.nom == ligne1 :
                        faisceauAppelant = p.faisceau.nom
                        break
            else :
                print("Erreur determination LIF")
                
                
            #LIGNE - 2
            indiceTiret = -1 #On reinitialise le marqueur
            for i in range(len(ligne2)):
                if ligne2[i] == '-' :
                    indiceTiret = i
                    break
            #l'indice i est '-', l'indice i+1 est ' ' et l'indice i+2 est le debut de l'intitule de la ligne
            
            if(indiceTiret != -1):
                ligne2 = ligne2[i+2:len(ligne2)]
                ligne2 = ligne2.replace(" ", "")
                for p in listeLif :
                    if p.nom == ligne2 :
                        faisceauAppele = p.faisceau.nom
                        break
            else :
                print("Erreur determination LIF")
                  
                  
            #On s'occupe maintenant de determiner s'il s'agit d'un appel passe en SU+TP ou d'un debordement Numeris
            sutp = False
            numeris = False
            temo = "SecoursUltime"
            temo2="Numeris"
            
            t[k][31] = t[k][31].replace(" ","")
            
            for l in range(len(t[k][31])-len(temo)):
                if t[k][31][l:l+len(temo)] == temo :
                    sutp = True
                    print("SU+TP")
                    break
            for l in range(len(t[k][31])-len(temo2)):        
                if t[k][31][l:l+len(temo2)] == temo2 :
                    numeris = True
                    print("SDA")
                    break
            
            
            a = Appel(appelant=apple, appele= applant, date = date_a_sauvegarder, heure = d.time(), type = t[k][25].replace('"',''),duree = int(dur.total_seconds()), liberation = t[k][30][14:-1].replace('"',''), line_appelante = fsx_a, line_appele = fsx_e, etat = etatAppel, nom_appele = nomAppelant , nom_appelant = nomAppele, fx_entrant = faisceauAppele, fx_sortant = faisceauAppelant, SUTP = sutp, SDA = numeris)
            a.save()
      
    return 0
    
    
    #CODE QUE REALISE LE SCRIPT

time1 = time.time()
t = main()
listeLif = LIF.objects.all() #Variable utilisee pour determiner et referencer le faisceau par lequel passe un appel
createAppel(t, listeLif)
time2 = time.time()

execution = time2 - time1
print("DUREE D'EXECUTION : ")
print(execution)


# Commande shell manage.py : exec(open('communication/fromCSVtoSQL.py').read())
