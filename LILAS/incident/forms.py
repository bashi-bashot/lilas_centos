from django import forms
from django.contrib.admin import widgets

class DateForm(forms.Form):
    dateDebut = forms.DateField(label='Date de début : ', widget=widgets.AdminDateWidget())
    heureDebut  = forms.CharField(max_length=8, widget=forms.TextInput(attrs={'size':10, 'value':'00:00:00'}))
    dateFin = forms.DateField(label='Date de fin : ',  widget=widgets.AdminDateWidget())
    heureFin = forms.CharField(max_length=8, widget=forms.TextInput(attrs={'size':10, 'value':'23:59:59'}))
