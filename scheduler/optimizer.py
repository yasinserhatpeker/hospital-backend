from .models import AnesthesiaTeam,Surgeon,Surgery,Schedule,OperationRoom,Constraints
from datetime import datetime,timedelta
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
         return {c.name : c.weigth for c in constraints}  
     
     
    def _initiliaze_grids(self):
         current_date = self.start_date
         
         while current_date <= self.end_date:
             date_str = current_date.strftime("%d-%m-%Y")
             self.schedule_grid[date_str] = {}
             self.surgeon_tracker[date_str] = {}
             self.team_tracker[date_str] = {}
            
             for slot in range(1,self.total_daily_slots + 1):
                
        
            
             
        