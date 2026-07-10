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
    required_room_name = serializers.ReadOnlyField(source='required_room.name') # foreign key
    class Meta:
        model=Surgery
        fields=['id','required_room','required_room_name','priority','patient_name','operation_name','duration_slots']


class AnesthesiaTeamSerializer(serializers.ModelSerializer):
    class Meta:
        model=AnesthesiaTeam
        fields =['id','name']
        
class ConstraintsSerializer(serializers.ModelSerializer):
    class Meta:
        model=Constraints
        fields =['id','name','description','is_active','weight','rule_type']
        
class ScheduleSerializer(serializers.ModelSerializer):
    surgeon_name = serializers.ReadOnlyField(source='surgeon.name')
    room_name = serializers.ReadOnlyField(source='room.name')
    team_name = serializers.ReadOnlyField(source='team.name')
    surgery_name = serializers.ReadOnlyField(source ='surgery.operation_name')
    
    class Meta:
        model=Schedule
        fields = ['id','start_slot', 'end_slot','date',
                  'room', 'room_name',
                   'surgeon','surgeon_name',
                   'surgery','surgery_name',
                   'team','team_name'
                  ]
        
class ScheduleGenerationSerializer(serializers.Serializer):
    start_date = serializers.DateField(format="%d-%m-%Y", input_formats = ["%d-%m-%Y"])
    end_date = serializers.DateField(format="%d-%m-%Y", input_formats = ["%d-%m-%Y"])
    
    def validate(self,data):
        if data['start_date'] > data['end_date']:
         raise serializers.ValidationError("start date cannot be bigger than end date")
        return data
        