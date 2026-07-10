from .models import AnesthesiaTeam,Surgery,Surgeon, Schedule, OperationRoom, Constraints
from datetime import timedelta
from django.db import transaction

class SurgeryOptimizer:
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        
        self.active_constraints = self._load_constraints()
        self.total_daily_slots = 10
        
        self.schedule_grid = {}
        self.surgeon_tracker = {}
        self.team_tracker = {}
        
        self.rooms = list(OperationRoom.objects.all())
        self.teams = list(AnesthesiaTeam.objects.all())
        
        self.final_assignment = []
      
    def _load_constraints(self):
        constraints = Constraints.objects.filter(is_active=True)
        return {c.name: c.weight for c in constraints}  
     
    def _initialize_grids(self):
        current_date = self.start_date
        
        while current_date <= self.end_date:
            date_str = current_date.strftime("%d-%m-%Y")
            self.schedule_grid[date_str] = {}
            self.surgeon_tracker[date_str] = {}
            self.team_tracker[date_str] = {}
            
            for slot in range(1, self.total_daily_slots + 1):
                self.surgeon_tracker[date_str][slot] = set()
                self.team_tracker[date_str][slot] = set()
            
            for room in self.rooms:
                self.schedule_grid[date_str][room.id] = {slot: None for slot in range(1, self.total_daily_slots + 1)}  
        
            current_date += timedelta(days=1)
        
    def _calculate_surgery_score(self, surgery):
        priority_weight = self.active_constraints.get('priority_weight', 5)
        duration_weight = self.active_constraints.get('duration_weight', 2)
        
        priority_map = {
            'kritik': 4,
            'yüksek': 3,
            'orta': 2,
            'düşük': 1
        } 
        
        safe_priority_str = surgery.priority.strip().lower()
        urgency_multiplier = priority_map.get(safe_priority_str, 1)
        
        score = (urgency_multiplier * priority_weight) + (surgery.duration_slots * duration_weight)
        return score
     
    def _get_sorted_surgeries(self):
        pending_surgeries = list(Surgery.objects.filter(schedule__isnull=True))
        pending_surgeries.sort(key=self._calculate_surgery_score, reverse=True)
        return pending_surgeries
    
   
    def _is_valid_replacement(self, date_str, room_id, start_slot, duration, required_room_id):
        if required_room_id and required_room_id != room_id:
            return False
        
        end_slot = start_slot + duration - 1
        
        if end_slot > self.total_daily_slots:
            return False
        
        for slot in range(start_slot, end_slot + 1):
            if self.schedule_grid[date_str][room_id][slot] is not None:
                return False
          
        return True
        
    def _get_available_resources(self, date_str, start_slot, surgeon_id, duration):
        end_slot = start_slot + duration - 1
        
        for slot in range(start_slot, end_slot + 1):
            if surgeon_id in self.surgeon_tracker[date_str][slot]:
                return False, None
            
        available_team = None
        
        for team in self.teams:
            team_is_free = True
            for slot in range(start_slot, end_slot + 1):
                if team.id in self.team_tracker[date_str][slot]:
                    team_is_free = False 
                    break
                
            if team_is_free:
                available_team = team
                break
            
        
        if not available_team:
            return False, None
            
        return True, available_team
        
    def _place(self, date_str, room_id, start_slot, surgeon_id, team_id, surgery_id, duration):
        
        for slot in range(start_slot, start_slot + duration):
            self.schedule_grid[date_str][room_id][slot] = surgery_id
            self.surgeon_tracker[date_str][slot].add(surgeon_id)
            self.team_tracker[date_str][slot].add(team_id)
            
    def _remove(self, date_str, room_id, start_slot, surgeon_id, team_id, duration):
        
        for slot in range(start_slot, start_slot + duration):
            self.schedule_grid[date_str][room_id][slot] = None
            self.surgeon_tracker[date_str][slot].remove(surgeon_id)
            self.team_tracker[date_str][slot].remove(team_id)
             
    def _backtracking_algorithm(self, surgeries, index):
        if index == len(surgeries):
            return True   
        
        current_surgery = surgeries[index]
        
        if not current_surgery.surgeon:
         raise ValueError(f"'{current_surgery.patient_name}'named patient has no surgeon.")
     
        duration = current_surgery.duration_slots
        
        surgeon_id = current_surgery.surgeon.id
        required_room_id = current_surgery.required_room.id if current_surgery.required_room else None
        
        current_date = self.start_date
        while current_date <= self.end_date:
            date_str = current_date.strftime("%d-%m-%Y") 
            
            for room in self.rooms:
                for start_slot in range(1, self.total_daily_slots + 1):
                    
                    if self._is_valid_replacement(date_str, room.id, start_slot, duration, required_room_id):
                        
                        resources_ok, available_team = self._get_available_resources(date_str, start_slot, surgeon_id, duration)
                        
                        if resources_ok:
                            
                            self._place(date_str, room.id, start_slot, surgeon_id, available_team.id, current_surgery.id, duration)
                            
                            assignment = {
                                'date': current_date,
                                'start_slot': start_slot,
                                'end_slot': start_slot + duration - 1,
                                'room_id': room.id,
                                'surgeon_id': surgeon_id,
                                'team_id': available_team.id,
                                'surgery_id': current_surgery.id
                            }
                            self.final_assignment.append(assignment)
                            
                            
                            if self._backtracking_algorithm(surgeries, index + 1):
                                return True
                            
                            self.final_assignment.pop()
                            
                            
                            self._remove(date_str, room.id, start_slot, surgeon_id, available_team.id, duration)
                            
            current_date += timedelta(days=1)
            
        return False
    
    def generate_schedule_plan(self):
        self._initialize_grids()
        surgeries_to_plan = self._get_sorted_surgeries()
        
        if not surgeries_to_plan:
            return {"status": "success", "message": "There's no surgery to plan.", "data": []}
        
        success = self._backtracking_algorithm(surgeries_to_plan, 0)
        
        if success:
            try:
                with transaction.atomic():
                    for asg in self.final_assignment:
                        Schedule.objects.create(
                            date=asg['date'],
                            start_slot=asg['start_slot'],
                            end_slot=asg['end_slot'],
                            room_id=asg['room_id'],
                            surgeon_id=asg['surgeon_id'],
                            team_id=asg['team_id'],
                            surgery_id=asg['surgery_id']
                        )
                        
               
                return {
                    "status": "success",
                    "message": f"{len(surgeries_to_plan)} surgeries successfully planned.",
                    "planned_count": len(surgeries_to_plan)
                }
                    
            except Exception as e:
                return {"status": "error", "message": f"There's an error occured during query: {str(e)}"}
                
        else:
            return {"status": "error", "message": "There's an error occured during planning. Please configure the constraints or timezone."}