from django import forms
from django.contrib.admin import widgets
from .exception import *
# from django.core import validators
# from django.core.validators import FileExtensionValidator


class UploadFileForm(forms.Form):
    fileConf = forms.FileField(required=False)

    fileSyst = forms.FileField(required=False)

    fileOpe = forms.FileField(required=False)
    # fileOpe = forms.FileField(required=False, validators=[FileExtensionValidator(allowed_extensions=('csv',))])
    
    fileCom = forms.FileField(required=False)

    fileInc = forms.FileField(required=False)

    class Meta:
        fields = ('fileConf', 'fileSyst', 'fileOpe', 'fileCom', 'fileInc')

    def clean(self):
        data = self.cleaned_data
        if (not data.get('fileConf', None) and data.get('fileSyst', None)) or (data.get('fileConf', None) and not data.get('fileSyst', None)):
            raise forms.ValidationError('Veuillez renseigner les 2 fichiers de configuration')
        else:
            return data

    # def clean_fileOpe(self):
    #     fileOpe = self.cleaned_data['fileOpe']
    #     if fileOpe != None:
    #         print(fileOpe)
    #         if not '.csv' in fileOpe:
    #             print(fileOpe)
    #             raise forms.ValidationError('Veuillez utiliser un fichier .CSV')
            
    
    # def clean(self):
    #     cleaned_data = super().clean()
    #     fileOpe = cleaned_data.get("fileOpe")
    #     print(fileOpe)
    #     if not '.csv' in fileOpe:
    #         print(fileOpe)
    #         raise forms.ValidationError({'fileOpe':['Veuillez utiliser un fichier .CSV']})