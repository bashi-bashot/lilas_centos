from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from configSalle.models import Uce, ConfigurationSalle
from .forms import DateForm

from datetime import datetime
import pytz

def index(request):

    #LISTE DE VARIABLES GLOBALES
    formulaireDates = DateForm(request.POST)
    #---------------------------
    
    
    #Creation de la liste qui contient les dates selectionnables dans le datepicker
    tabDatesNonEmpty = []
    bdd_datePicker = ConfigurationSalle.objects.all()
    date__datePicker = []
    for i in range(len(bdd_datePicker)): #Cette boucle risque de prendre du temps si énormément de conf de salles sont entrées. Pour l'optimiser, il faudrait faire comme commmunciation : faire une table Date dans laquelle on entre toutes les dates à laquelle est rattachée une conf artemis
        #date__datePicker.append(strDate)
        if(bdd_datePicker[i].date.strftime("%d/%m/%Y") not in tabDatesNonEmpty): 
            tabDatesNonEmpty.append(bdd_datePicker[i].date.strftime("%d/%m/%Y"))
    
    
    
    context = {'form':formulaireDates, 'datesNonEmpty' : tabDatesNonEmpty}

    if request.method == 'POST': #Si on a rempli un formulaire /!\ Chercher comment différencier les différents formulaire d'une même page /!\
            
            if formulaireDates.is_valid(): #Si on a rempli le formulaire de choix de date / secteur / correspondant pour afficher les appels
                # process the data in form.cleaned_data as required
                print("FORMULAIRE DATE VALIDE")
                
                date = formulaireDates.cleaned_data['date'] #On récupère la dete de début entrée dans le formulaire
                
                #On crée ensuite les objets datetime de début et de fin
                date_time_deb = datetime( date.year, date.month, date.day, 00, 00, 00) #date naive
                date_time_fin = datetime( date.year, date.month, date.day, 23, 59, 00) #date naive aussi
                
                timzeone = pytz.timezone('UTC') #Définition de la zone horaire pour rendre la date aware
                date_time_deb_aware = timzeone.localize(date_time_deb) #Pour faire le test suivant, le fuseau horaire de la date associée doit être renseigné 'aware'
                date_time_fin_aware = timzeone.localize(date_time_fin)
                
                #On crée la liste de confSalle à afficher
                confs = ConfigurationSalle.objects.filter(date__gte = date_time_deb_aware, date__lte = date_time_fin_aware)
                
                #On crée la liste d'uces à afficher et on l'initialise
                uces=[]
                if len(confs) !=0:
                    uces = confs[0].confUce.all()
                    for i in range(confs.count()) :
                        uces = uces | confs[i].confUce.all()  #cet opérateur combine les querysets entre eux
                
                #On change la variable contexte à envoyer au html
                context = { 'uceListe':uces, 'confListe':confs, 'date':date, 'form':formulaireDates, 'datesNonEmpty' : tabDatesNonEmpty}                
                # redirect to a new URL:
                return render(request, 'configSalle/index.html', context) #On recharge la pagee                
                
    
    else :                  #Dans le cas où on a pas récupéré un POST 
        form = DateForm()   #On crée le formulaire à afficher
        bool = True         #Permet de différencier le cas où le 'form' n'a pas été renseigné et/ou n'ets pas valide
        context = {'bool':bool, 'form':form, 'datesNonEmpty' : tabDatesNonEmpty}
        
    return render(request, 'configSalle/index.html', context)