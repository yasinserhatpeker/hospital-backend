from rest_framework import viewsets,status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Schedule,Surgeon,Surgery,AnesthesiaTeam,Constraints,OperationRoom
from .serializer import ScheduleSerializer,SurgeonSerializer,SurgerySerializer,AnesthesiaTeamSerializer,ConstraintsSerializer,OperationRoomSerializer,ScheduleGenerationSerializer

from .optimizer import SurgeryOptimizer

class BaseProjectViewSet(viewsets.ModelViewSet):
    # pagitation,authentication ...
    pass

class OperationRoomViewSet(BaseProjectViewSet):
    queryset = OperationRoom.objects.all()
    serializer_class = OperationRoomSerializer

class SurgeonViewSet(BaseProjectViewSet):
   queryset = Surgeon.objects.all()
   serializer_class = SurgeonSerializer
   
class SurgeryViewSet(BaseProjectViewSet):
    queryset = Surgery.objects.all()
    serializer_class = SurgerySerializer
    
class ScheduleViewSet(BaseProjectViewSet):
    queryset=Schedule.objects.select_related('room', 'surgeon', 'surgery','team').all()
    serializer_class = ScheduleSerializer

class AnesthesiaTeamViewSet(BaseProjectViewSet):
    queryset = AnesthesiaTeam.objects.all()
    serializer_class = AnesthesiaTeamSerializer
    
class ConstraintsViewSet(BaseProjectViewSet):
    queryset = Constraints.objects.all()
    serializer_class = ConstraintsSerializer
    
    
class GenerateScheduleAPIView(APIView):
    
   def post(self,request):
       serializer = ScheduleGenerationSerializer(data=request.data)
       
       serializer.is_valid(raise_exception = True)
       
       start_date = serializer.validated_data['start_date']
       end_date = serializer.validated_data['end_date']
       
       try:
           optimizer = SurgeryOptimizer(start_date,end_date)
           result = optimizer.generate_schedule_plan()

           if result['status'] == 'success':
               
               if result.get('data') and hasattr(result['data'][0], 'pk'):
                   result = {**result, 'data': ScheduleSerializer(result['data'], many=True).data}
                   
               return Response(result, status=status.HTTP_201_CREATED)
           else:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
        
       except Exception as e:
           
           return Response({"error":f"There's an error occured in server-side. {str(e)}"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
           