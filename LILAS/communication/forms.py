from django import forms
from django.contrib.admin import widgets
from communication.models import *


#Liste à modifier dynamiquement




listeTypeStats = [
    (1, ("Indifférent")),
    (2, ("Secteur")),
    (3, ("Ligne")),
    (4, ("Faisceau")),
    (5, ("SU + TP")),
    (6, ("Secours SDA")),
    (7, ("Numéro Inconnu"))
]

bddSecteur = NumSecteur.objects.all()
bddExterieur = NumExterieur.objects.all()

choicesSecteurs = [(1,"Tous secteurs"), (i+1, bddSecteur[i].nom) for i in range(bddSecteur.count())]
choiceExterieur = [(1,"Tous les correspondants"), (i+1, bddExterieur[i].nom) for i in range(bddExterieur.count())]

       
class NameForm(forms.Form):
    dateDebut = forms.DateField(widget=widgets.AdminDateWidget(attrs={'size':10}))
    heureDebut  = forms.CharField(max_length=8, widget=forms.TextInput(attrs={'size':10, 'placeholder': 'hh:mm:ss'}))
    dateFin = forms.DateField(widget=widgets.AdminDateWidget(attrs={'size':10}))
    heureFin  = forms.CharField(max_length=8, widget=forms.TextInput(attrs={'size':10, 'placeholder': 'hh:mm:ss'}))

    positionSpinner = forms.CharField(widget=forms.Select(choices = choicesSecteurs))
    correspondantSpinner = forms.CharField(widget=forms.Select(choices = choiceExterieur))

    selectionTypeSpinner = forms.ChoiceField(label='',choices = listeTypeStats)
    
    #def __init__(self, *args, **kwargs): #Fonction appelée a chaque appel du formulaire dans le code python
        #C'est une fonction nécessaire au remplissage dynamique du choiceField positionSpinner
        #l'appel est de cette forme là : formulaire=NameField(request.POST, my_choices = DICTIONNAIRE)
        
        #choices=[(1,("Tous secteurs"))] #On initialise une variable par défaut pour le spinenr de secteur
        #choices_corr = [(1, ("Tous les correspondants"))] #On initialise une variable par défaut pour le spinneur de correspondant

        #try:
        #    choices = kwargs.pop('choice_list_sect') #Si dans les kwargs (arguments donnés à l'appel de la classe) on a un élément de nom 'choice_list' alors on remplace la variable choices
        #except KeyError:
        #    print("Liste de secteurs non initialisée [DateForm]")
        
        #try:
        #    choices_corr = kwargs.pop('choice_list_corr') #Si dans les kwargs (arguments donnés à l'appel de la classe) on a un élément de nom 'choice_list' alors on remplace la variable choices
        #except KeyError:
        #    print("Liste de correspondants non initialisée [DateForm]")
       
        #super(NameForm, self).__init__(*args, **kwargs)
        
        #self.fields['correspondantSpinner'] = forms.ChoiceField(choices = choices_corr)
        #self.fields['positionSpinner'] = forms.ChoiceField(choices = choices)

    def clean_heureDebut(self):
        strHeure = self.cleaned_data['heureDebut']
        if (strHeure[2] != ':' or strHeure[5] != ':'):
            raise forms.ValidationError("Format : hh:mm:ss.", code="invalid format")
        return strHeure
        
        
        
 
    
    
# class StatSelectForm(forms.Form):
    # selectionTypeSpinner = forms.ChoiceField(label='',choices =listeTypeStats)

    
