from django.contrib import admin
from .models import Surgeon,Schedule,Surgery,AnesthesiaTeam,OperationRoom,Constraints

admin.site.register(Surgeon)
admin.site.register(Surgery)
admin.site.register(Schedule)
admin.site.register(AnesthesiaTeam)
admin.site.register(OperationRoom)
admin.site.register(Constraints)
