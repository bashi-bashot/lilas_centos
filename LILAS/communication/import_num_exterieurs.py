#-*- coding: utf-8 -*-

#Algorithme qui charge en base de donnee les numeros exterieurs au CRNA.
from communication.models import NumExterieur
from django.conf import settings


def chargeFichier():
    fic = open(settings.MEDIA_ROOT+"/ELTS.csv", newline='', encoding='latin1')   
    tab = fic.readlines() 
    fic.close()
    return tab


def chercheATC(t):
    temoin="CATC"
    indexOfATC=[]
    for i in range(len(t)):
        for j in range(len(t[i])-4):
            if(t[i][j:j+4] == temoin):
                indexOfATC.append(i)
                
    return indexOfATC
    
def chercheCNUM(t):
    temoin="CNUM"
    indexOfATC=[]
    for i in range(len(t)):
        for j in range(len(t[i])-4):
            if(t[i][j:j+4] == temoin):
                indexOfATC.append(i)
                
    return indexOfATC
    
def chercheGRP(t):
    temoin=';"GRP "'
    indexOfGRP=[]
    for i in range(len(t)):
        for j in range(len(t[i])-len(temoin)):
            if(t[i][j:j+len(temoin)] == temoin):
                indexOfGRP.append(i)
                  
    return indexOfGRP
    
t = chargeFichier()
tabIndex = chercheATC(t)
tabIndexCNUM = chercheCNUM(t)
tabIndexGRP = chercheGRP(t)

# print(len(tabIndexGRP))




for i in tabIndex : #i est deja un indice de CATC, pas besoin de mettre tabIndex[i]
    t[i] = t[i].split(';')
    
for i in tabIndexCNUM : #i est deja un indice de CNUM, pas besoin de mettre tabIndex[i]
    t[i] = t[i].split(';')

for i in tabIndexGRP : #i est deja un indice de GRP, pas besoin de mettre tabIndex[i]
    t[i] = t[i].split(';')
    
    

for i in range(len(tabIndex)):
    id_floating = str(t[tabIndex[i]][0]) #id_elts (string) avec deux 0 apres la virgule
    id = id_floating[0:len(id_floating)-3] #virgule et chiffres apres la virgule enleves
    
    if NumExterieur.objects.filter(numero__contains=str(t[tabIndex[i]][32])).filter(nom__contains=t[tabIndex[i]][5][1:-1]).count()==0:
        corr = NumExterieur(id_elts =id , id_lilas = str(i), numero = str(t[tabIndex[i]][32]), nom = t[tabIndex[i]][5][1:-1])
        corr.save()
    else :
        print("Correspondant deja existant")
    
for i in range(len(tabIndexCNUM)):
    id_floating = str(t[tabIndexCNUM[i]][0]) #id_elts (string) avec deux 0 apres la virgule
    id = id_floating[0:len(id_floating)-3] #virgule et chiffres apres la virgule enleves

    if NumExterieur.objects.filter(numero__contains=str(t[tabIndexCNUM[i]][26])).filter(nom__contains=t[tabIndexCNUM[i]][5][1:-1]).count()==0:
        corr = NumExterieur(id_elts =id , id_lilas = str(i), numero = str(t[tabIndexCNUM[i]][26]), nom = t[tabIndexCNUM[i]][5][1:-1])
        corr.save()
    else :
        print("Correspondant deja existant")
    
for i in range(len(tabIndexGRP)):
    id_floating = str(t[tabIndexGRP[i]][0]) #id_elts (string) avec deux 0 apres la virgule
    id = id_floating[0:len(id_floating)-3] #virgule et chiffres apres la virgule enleves
    
    if NumExterieur.objects.filter(numero__contains=str(t[tabIndexGRP[i]][32])).filter(nom__contains=t[tabIndexGRP[i]][5][1:-1]).count()==0:
        corr = NumExterieur(id_elts =id , id_lilas = str(i), numero = str(t[tabIndexGRP[i]][32]), nom = t[tabIndexGRP[i]][5][1:-1])
        corr.save()
    else :
        print("Correspondant deja existant")

# Commande shell manage.py : exec(open('communication/import_num_exterieurs.py').read())

#exec(open('communication/script_change_numéro.py').read())
