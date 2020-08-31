#Script qui a pour but de pallier le problème des 0 en début de numéro de tel à 10 chiffres qui n'apparait pas suite à un pb dans excel
from communication.models import *

listeCorres = NumExterieur.objects.all()

for i in range(len(listeCorres)):
    correspondant = listeCorres[i]
    if(len(correspondant.numero) == 9):
        numero = "0"+numero
        correspondant.save()