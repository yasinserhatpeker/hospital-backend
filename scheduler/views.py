from rest_framework import viewsets
from .models import Schedule,Surgeon,Surgery,AnesthesiaTeam,Constraints,OperationRoom
from .serializer import ScheduleSerializer,SurgeonSerializer,SurgerySerializer,AnesthasiaTeamSerializer,ConstraintsSerializer,OperationRoomSerializer

class OperationRoomViewSet(viewsets.ModelViewSet):
    queryset = OperationRoom.objects.all()
    serializer_class = OperationRoomSerializer

