from rest_framework import viewsets
from .models import Schedule,Surgeon,Surgery,AnesthesiaTeam,Constraints,OperationRoom
from .serializer import ScheduleSerializer,SurgeonSerializer,SurgerySerializer,AnesthasiaTeamSerializer,ConstraintsSerializer,OperationRoomSerializer

class OperationRoomViewSet(viewsets.ModelViewSet):
    queryset = OperationRoom.objects.all()
    serializer_class = OperationRoomSerializer

class SurgeonViewSet(viewsets.ModelViewSet):
   queryset = Surgeon.objects.all()
   serializer_class = SurgeonSerializer
   
class SurgeryViewSet(viewsets.ModelViewSet):
    queryset = Surgery.objects.all()
    serializer_class = SurgerySerializer
    
class ScheduleViewSet(viewsets.ModelViewSet):
    queryset=Schedule.objects.select_related('room', 'surgeon', 'surgery','team').all()
    serializer_class = ScheduleSerializer

class AnesthesiaTeamViewSet(viewsets.ModelViewSet):
    queryset = AnesthesiaTeam.objects.all()
    serializer_class = AnesthasiaTeamSerializer
    
class ConstraintsViewSet(viewsets.ModelViewSet):
    queryset = Constraints.objects.all()
    serializer_class = ConstraintsSerializer