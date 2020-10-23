#Script qui charge les faisceaux et les lignes
#Charge aussi certaines LIF qui interviennent dans les appels
from communication.models import Faisceau, LIF
from django.conf import settings



def chargeFichier():
    #fic = open(settings.MEDIA_ROOT+"/ELTS.csv", 'r', encoding='latin1')
    fic = open(settings.MEDIA_ROOT+"/ELTS.csv", newline='', encoding='latin1')
    tab = fic.readlines()
    fic.close()
    return tab #Chaque element de tab est une ligne de ELTS
    
def chercheFX(t):
    temoin="FX"
    indexOfFX=[]
    for i in range(len(t)):
        u = t[i].split(';')
        #u = t[i]
        for j in range(len(u[1])-2):
            if(u[1][j:j+2] == temoin):
                indexOfFX.append(i)
    return indexOfFX
    
def chercheLif(t):
    temoin='LIF '
    indexOfLif=[]
    for i in range(len(t)):
        
        # print(u)
        for j in range(len(t[i])-8):
            if(t[i][j:j+len(temoin)] == temoin):
                indexOfLif.append(i)
    print("Nombre de LIFs trouvees :")
    print(len(indexOfLif))
    return indexOfLif
    
    
t = chargeFichier()
tabIndex = chercheFX(t)
tabIndexLif=chercheLif(t)

#On cree un faisceau fictif
nomFx = "Fx FICTIF"
faisc = Faisceau(nom = nomFx, id_elts="abcd", id_lilas='abcd')
if Faisceau.objects.filter(nom__contains=nomFx).count()==0:
    faisc.save()
else :
    print("Faisceau fictif deja existant")
#Pour chaque element de TabIndexLIF on cree une LIF. Au pire, elle existe deja

for i in tabIndex :
    t[i] = t[i].split(';')
    
# print(t[0])

for i in range(len(tabIndex)):
    id_floating = str(t[tabIndex[i]][0]) #id_elts (string) avec deux 0 apres la virgule (WIN)
    #id = id_floating[0:len(id_floating)-3] #virgule et chiffres apres la virgule enleves (WIN)
    id=id_floating
    #print(id_floating)
    #print(id)    


    if Faisceau.objects.filter(nom__contains=t[tabIndex[i]][5]).count()==0:
        fx = Faisceau(id_elts =id , id_lilas = str(i), nom = t[tabIndex[i]][5].replace('"',''))
        fx.save()
    else :
        print('fx deja present')
    

#On s'occupe maintenant des LIFs

print("indices des LIFS recuperees : "+str(len(tabIndexLif)))

f = open(settings.MEDIA_ROOT+"/CONF_SYSTEM.csv", 'r')
tabLien = f.readlines()
f.close()

tabFaisceaux = Faisceau.objects.all()
print("Chargement des faisceaux")

#On commence par mettre en forme le tableau de lien
for i in tabLien :
    i=i.split(';')
    i[1] = i[1][0:len(i[1])-3] #On enleve les la virgule et les chiffres apres la virgule
    i[2] = i[2][0:len(i[2])-4] #On enleve les la virgule et les chiffres apres la virgule et le \n

    #On cherche dans te tableau CONF_SYSTEM si on trouve une correspondance

#On s'assure qu'il n'y ait pas de doublons

newList=[]
for i in tabIndexLif :
    if i not in newList :
        newList.append(i)

tabIndexLif = newList

print("Nombre de LIF apres verification doublons :")
print(len(tabIndexLif))

for i in tabIndexLif :
    t[i] = t[i].split(';')
    #print(t[i][1])
    #print(i)

for i in range(len(tabIndexLif)):
    id_floating = str(t[tabIndexLif[i]][0]) #id_elts (string) avec deux 0 apres la virgule
    #id = id_floating[0:len(id_floating)-3] #virgule et chiffres apres la virgule enleves
    id = id_floating
    #print(id_floating)
    #print(id)
    id_fx = '-1'
    #On regarde si il existe un element de type_association : 24 qui lie le numero de LIF avec un numero de faisceau
    for k in tabLien :
        k = k.split(";")
        #print(k[0])
        if k[0] == '24' :
            print("Association LIF-FAISCEAU trouvee")
            print(str(id_floating))
            print(k[2][0:len(k[2])-3])
            if k[2][0:len(k[2])-3] == str(id_floating) : #Si on trouve l'id_elts d'une LIF dans le tableau d'association, alors il faut regarder l'id_elts du faisceau
                id_fx = k[1][0:len(k[1])-3]
                print("Faisceau trouve avec l'id : "+id_fx)
            #else :
                #print("Probleme :")
                #print(str(id_floating))
                #print(k[2][0:len(k[2])-4])
    
    fxLifCourrant = ""
    if id_fx == '-1' :
        #print("Faisceau non trouve FLAG2")
        #print(t[tabIndexLif[i]][5])
        # on la sauvegarde en utilisant le faisceau fictif car il s'agit d'une BCB
        fx_fictif = Faisceau.objects.filter(nom__contains="Fx FICTIF")[0]
        lif = LIF(id_elts =id , id_lilas = str(i), nom = t[tabIndexLif[i]][5], faisceau = fx_fictif)
        lif.save()
        pass
    else :
        #print("LIF : Faisceau trouve")
        #On recupere le faisceau correspondant dans la table Faisceau
        for faisceau in tabFaisceaux :
            if faisceau.id_elts == id_fx :
                fxLifCourrant = faisceau
                break;
        #print("Verif fxlifcourrant")
        #print(fxLifCourrant)
        if fxLifCourrant != "" :        
            #print(t[tabIndexLif[i]][5][1:-1])
            if LIF.objects.filter(nom__contains=t[tabIndexLif[i]][5]).count()==0:
                lif = LIF(id_elts =id , id_lilas = str(i), nom = t[tabIndexLif[i]][5].replace('"',''), faisceau = fxLifCourrant)
                lif.save()
                print("LIF sauvee en FLAG1, fichier loadFX.py")
            else:
                print('lif deja presente')
    
#On s'occupe maintenant des LIFs orphelines 


#On doit determiner le dernier id id_lilas attribue
listeLifExistantes = LIF.objects.all()
maxID = -1
for i in range(len(listeLifExistantes)):
    if int(listeLifExistantes[i].id_lilas) > maxID :
        maxID = int(listeLifExistantes[i].id_lilas)
    
    
for p in tabIndexLif :
    # print(t[p][1].replace('"','').replace(' ',''))
    # print(t[p][5].replace('"',''))
    maxID = maxID + 1
    l = LIF(nom = t[p][5].replace('"',''), faisceau = faisc, id_elts = t[p][0][0:len(t[p][0])-3], id_lilas = maxID)
    if LIF.objects.filter(nom__contains=t[p][5].replace('"','')).count() == 0 :
        l.save()
    else :
        print("LIF deja existante")
        print(t[p][5].replace('"',''))
    
    
    
    
    

# Commande shell manage.py : exec(open('communication/loadFX.py').read())
