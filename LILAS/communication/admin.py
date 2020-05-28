from django.contrib import admin
from .models import Appel, NumExterieur, NumSecteur, Faisceau, LIF, Date

# Register your models here.

admin.site.register(Appel)
admin.site.register(NumExterieur)
admin.site.register(NumSecteur)
admin.site.register(Faisceau)
admin.site.register(LIF)
admin.site.register(Date)
