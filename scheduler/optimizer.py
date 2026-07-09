from .models import AnesthesiaTeam,Surgeon,Surgery,Schedule,OperationRoom,Constraints
from datetime import timedelta
from django.db import transaction

class SurgeryOptimizer:
    def __init__(self,start_date,end_date):
        self.start_date = start_date
        self.end_date = end_date
        
        self.active_constraints = self._load_constraints()
        self.total_daily_slots = 10
        
        self.schedule_grid= {}
        self.surgeon_tracker = {}
        self.team_tracker = {}
        
        self.rooms = list(OperationRoom.objects.all())
        self.teams = list(AnesthesiaTeam.objects.all())
        
        self.final_assignment = []
        
    
    def _load_constraints(self):
         constraints = Constraints.objects.filter(is_active = True)
         return {c.name : c.weight for c in constraints}  
     
     
    def _initialize_grids(self):
         current_date = self.start_date
         
         while current_date <= self.end_date:
             date_str = current_date.strftime("%d-%m-%Y")
             self.schedule_grid[date_str] = {}
             self.surgeon_tracker[date_str] = {}
             self.team_tracker[date_str] = {}
            
             for slot in range(1,self.total_daily_slots + 1):
                  self.surgeon_tracker[date_str][slot] = set()
                  self.team_tracker[date_str][slot] = set()
            
             
             for room in self.rooms:
                 self.schedule_grid[date_str][room.id] ={slot:None for slot in range(1,self.total_daily_slots+1)}  
        
             current_date += timedelta(days=1)
        
    
    def _calculate_surgery_score(self,surgery):
         priority_weight = self.active_constraints.get('priority_weight',5)
         duration_weight = self.active_constraints.get('duration_weight',2)
         
         priority_map = {
             'kritik':4,
             'yüksek':3,
             'orta':2,
             'düşük':1
         } 
         
         safe_priority_str = surgery.priority.strip().lower()
         urgency_multiplier = priority_map.get(safe_priority_str,1)
         
         score = (urgency_multiplier * priority_weight) +(surgery.duration_slots * duration_weight)
         return score
     
     
    def _get_sorted_surgeries(self):
        pending_surgeries = list(Surgery.objects.filter(schedule__isnull=True))
        pending_surgeries.sort(key=self._calculate_surgery_score, reverse=True)
        
        return pending_surgeries

    
    def _is_valid_replacement(self,date_str,room_id,duration,required_room_id,start_slot):
        
        if required_room_id and required_room_id != room_id:
            return False
        
        
        
    
    
     
     
     