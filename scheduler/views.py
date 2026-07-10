from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Schedule,Surgeon,Surgery,AnesthesiaTeam,Constraints,OperationRoom
from .serializer import ScheduleSerializer,SurgeonSerializer,SurgerySerializer,AnesthesiaTeamSerializer,ConstraintsSerializer,OperationRoomSerializer,ScheduleGenerationSerializer

from .optimizer import SurgeryOptimizer

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
    queryset=Schedule.objects.select_related('room', 'surgeon', 'surgery','team').all() # avoiding n+1 problem with select_related
    serializer_class = ScheduleSerializer

class AnesthesiaTeamViewSet(viewsets.ModelViewSet):
    queryset = AnesthesiaTeam.objects.all()
    serializer_class = AnesthesiaTeamSerializer
    
class ConstraintsViewSet(viewsets.ModelViewSet):
    queryset = Constraints.objects.all()
    serializer_class = ConstraintsSerializer
    
    
class GenerateScheduleAPIView(APIView):
    
   def post(self,request,*args, **kwargs):
       serializer = ScheduleGenerationSerializer(data=request.data)
       
       serializer.is_valid(raise_exception = True)
       
       start_date = serializer.validated_data['start_date']
       end_date = serializer.validated_data['end_date']
       
       
       