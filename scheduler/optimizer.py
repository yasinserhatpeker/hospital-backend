from .models import AnesthesiaTeam,Surgeon,Surgery,Schedule,OperationRoom,Constraints
from datetime import datetime,timedelta
from django.db import transaction

class SurgeryOptimizer:
    def __init__(self,start_date_str,end_date_str):
        self.start_date_str = datetime.strftime(start_date_str,"%d-%m-%Y").date()
        self.end_date_str = datetime.strftime(end_date_str,"%d-%m-%Y").date()
        
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
           