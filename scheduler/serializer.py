from rest_framework import serializers
from datetime import datetime,timedelta
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
    surgeon_name = serializers.ReadOnlyField(source='surgeon.name')
    class Meta:
        model=Surgery
        fields=['id','required_room','required_room_name','surgeon','surgeon_name','priority','patient_name','operation_name','duration_slots']


class AnesthesiaTeamSerializer(serializers.ModelSerializer):
    class Meta:
        model=AnesthesiaTeam
        fields =['id','name']
        
class ConstraintsSerializer(serializers.ModelSerializer):
    class Meta:
        model=Constraints
        fields =['id','name','description','is_active','weight','value','rule_type']
        
class ScheduleSerializer(serializers.ModelSerializer):
    start_time = serializers.SerializerMethodField()
    end_time = serializers.SerializerMethodField()
    
    surgeon_name = serializers.ReadOnlyField(source='surgeon.name')
    room_name = serializers.ReadOnlyField(source='room.name')
    team_name = serializers.ReadOnlyField(source='team.name')
    surgery_name = serializers.ReadOnlyField(source ='surgery.operation_name')
    
    class Meta:
        model=Schedule
        fields = ['id','start_slot', 'end_slot',
                  'start_time',
                  'end_time',
                  'date',
                  'room', 'room_name',
                   'surgeon','surgeon_name',
                   'surgery','surgery_name',
                   'team','team_name'
                  ]
    def get_start_time(self,obj):
        base_time = datetime.strptime("08:00","%H:%M")
        start = base_time + timedelta(hours=obj.start_slot - 1 )
        return start.strftime("%H:%M")
    
    def get_end_time(self,obj):
        base_time = datetime.strptime("08:00","%H:%M")
        end = base_time + timedelta(hours=obj.end_slot)
        return end.strftime("%H:%M")
        
        
        
class ScheduleGenerationSerializer(serializers.Serializer):
    start_date = serializers.DateField(format="%d-%m-%Y", input_formats = ["%d-%m-%Y"])
    end_date = serializers.DateField(format="%d-%m-%Y", input_formats = ["%d-%m-%Y"])
    
    def validate(self,data):
        if data['start_date'] > data['end_date']:
         raise serializers.ValidationError("start date cannot be bigger than end date")
        return data
        