from rest_framework import serializers
from .models import Surgeon,Surgery,AnesthesiaTeam,Constraints,Schedule,OperationRoom

class OperationRoomSerializer(serializers.ModelSerializer):
   class Meta:
       model = OperationRoom
       fields= ['id','name','room_type']
    
class SurgeonSerializer(serializers.ModelSerializer):
    class Meta:
        model=Surgeon
        fields=['id','name','specialty','off_day']
        
class SurgerySerializer(serializers.ModelSerializer):
    class Meta:
        model=Surgery
        fields='__all__'


class AnesthasiaTeamSerializer(serializers.ModelSerializer):
    class Meta:
        model=AnesthesiaTeam
        fields ='__all__'
        
class ConstraintsSerializer(serializers.ModelSerializer):
    class Meta:
        model=Constraints
        fields ='__all__'
        
class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model=Schedule
        fields = '__all__'