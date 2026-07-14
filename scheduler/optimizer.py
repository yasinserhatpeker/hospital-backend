from .models import AnesthesiaTeam, Surgery, Schedule, OperationRoom, Constraints
from datetime import timedelta
from collections import defaultdict
from django.db import transaction

WEEKDAYS = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar']

class SurgeryOptimizer:
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date

        self.active_constraints = self._load_constraints()
        self.total_daily_slots = 10

        self.schedule_grid = {}
        self.surgeon_tracker = {}
        self.team_tracker = {}
        self.surgeon_daily_count = {}
        self.surgeon_busy_ranges = {}

        self.rooms = list(OperationRoom.objects.all())
        self.teams = list(AnesthesiaTeam.objects.all())

        self.final_assignment = []
        self.best_assignment = None
        self.best_score = None
        self.solutions_explored = 0
        self.max_solutions_to_explore = 200

    def _load_constraints(self):
        constraints = Constraints.objects.filter(is_active=True)
        return {c.name: c for c in constraints}

    def _constraint(self, key):
        return self.active_constraints.get(key)

    def _initialize_grids(self):
        current_date = self.start_date

        while current_date <= self.end_date:
            
            date_str = current_date.strftime("%d-%m-%Y")
            self.schedule_grid[date_str] = {}
            self.surgeon_tracker[date_str] = {}
            self.team_tracker[date_str] = {}
            self.surgeon_daily_count[date_str] = defaultdict(int)
            self.surgeon_busy_ranges[date_str] = defaultdict(list)

            for slot in range(1, self.total_daily_slots + 1):
                self.surgeon_tracker[date_str][slot] = set()
                self.team_tracker[date_str][slot] = set()

            for room in self.rooms:
                self.schedule_grid[date_str][room.id] = {slot: None for slot in range(1, self.total_daily_slots + 1)}

            current_date += timedelta(days=1)


        self._load_existing_schedules()

    def _load_existing_schedules(self):
        
        existing = Schedule.objects.filter(date__gte=self.start_date, date__lte=self.end_date)
        for schedule in existing:
            date_str = schedule.date.strftime("%d-%m-%Y")
            if date_str not in self.schedule_grid:
                continue
              
            for slot in range(schedule.start_slot, schedule.end_slot + 1):
                if schedule.room_id in self.schedule_grid[date_str] and slot in self.schedule_grid[date_str][schedule.room_id]:
                    
                    self.schedule_grid[date_str][schedule.room_id][slot] = schedule.surgery_id
                if slot in self.surgeon_tracker[date_str]:
                    
                    self.surgeon_tracker[date_str][slot].add(schedule.surgeon_id)
                    self.team_tracker[date_str][slot].add(schedule.team_id)
                    
            self.surgeon_daily_count[date_str][schedule.surgeon_id] += 1
            self.surgeon_busy_ranges[date_str][schedule.surgeon_id].append((schedule.start_slot, schedule.end_slot))

    def _calculate_surgery_score(self, surgery):
        
        priority_constraint = self._constraint('priority_weight')
        duration_constraint = self._constraint('duration_weight')
        
        priority_weight = priority_constraint.weight if priority_constraint else 5
        duration_weight = duration_constraint.weight if duration_constraint else 2

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

    def _violates_off_day(self, current_date, surgeon):
        if not surgeon.off_day:
            return False
        return WEEKDAYS[current_date.weekday()] == surgeon.off_day

    def _exceeds_max_daily(self, date_str, surgeon_id, limit):
        
        return self.surgeon_daily_count[date_str][surgeon_id] >= limit

    def _violates_min_rest(self, date_str, surgeon_id, start_slot, end_slot, min_gap):
        
        for (busy_start, busy_end) in self.surgeon_busy_ranges[date_str][surgeon_id]:
            
            if start_slot > busy_end:
                gap = start_slot - busy_end - 1
                
            elif end_slot < busy_start:
                gap = busy_start - end_slot - 1
                
            else:
                gap = -1
            if gap < min_gap:
                return True
            
        return False

    def _get_available_resources(self, date_str, current_date, start_slot, surgeon, duration):
        surgeon_id = surgeon.id
        end_slot = start_slot + duration - 1

        for slot in range(start_slot, end_slot + 1):
            if surgeon_id in self.surgeon_tracker[date_str][slot]:
                return False, None, 0

        soft_penalty = 0

        off_day_rule = self._constraint('surgeon_off_day')
        
        if off_day_rule and self._violates_off_day(current_date, surgeon):
            if off_day_rule.rule_type == 'HARD':
                return False, None, 0
            
            soft_penalty += off_day_rule.weight

        max_daily_rule = self._constraint('max_daily_surgeries')
        
        if max_daily_rule and max_daily_rule.value and self._exceeds_max_daily(date_str, surgeon_id, max_daily_rule.value):
            if max_daily_rule.rule_type == 'HARD':
                return False, None, 0
            soft_penalty += max_daily_rule.weight

        rest_rule = self._constraint('min_rest_slots')
        
        if rest_rule and rest_rule.value and self._violates_min_rest(date_str, surgeon_id, start_slot, end_slot, rest_rule.value):
            if rest_rule.rule_type == 'HARD':
                return False, None, 0
            soft_penalty += rest_rule.weight

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
            return False, None, 0

        return True, available_team, soft_penalty

    def _place(self,date_str,room_id,start_slot,surgeon_id,team_id,surgery_id,duration):
        
        end_slot = start_slot + duration - 1
        
        for slot in range(start_slot, start_slot + duration):
            
            self.schedule_grid[date_str][room_id][slot] = surgery_id
            self.surgeon_tracker[date_str][slot].add(surgeon_id)
            self.team_tracker[date_str][slot].add(team_id)
            
        self.surgeon_daily_count[date_str][surgeon_id] += 1
        self.surgeon_busy_ranges[date_str][surgeon_id].append((start_slot, end_slot))

    def _remove(self,date_str,room_id,start_slot,surgeon_id,team_id,duration):
        
        end_slot = start_slot + duration - 1
        
        for slot in range(start_slot, start_slot + duration):
            
            self.schedule_grid[date_str][room_id][slot] = None
            self.surgeon_tracker[date_str][slot].remove(surgeon_id)
            self.team_tracker[date_str][slot].remove(team_id)
            
        self.surgeon_daily_count[date_str][surgeon_id] -= 1
        self.surgeon_busy_ranges[date_str][surgeon_id].remove((start_slot, end_slot))

    def _backtracking_algorithm(self,surgeries,index,current_penalty):
        
        if index == len(surgeries):
            self.solutions_explored += 1
            
            if self.best_score is None or current_penalty < self.best_score:
                self.best_score = current_penalty
                self.best_assignment = list(self.final_assignment)
                
            return self.best_score == 0 or self.solutions_explored >= self.max_solutions_to_explore

        current_surgery = surgeries[index]

        if not current_surgery.surgeon:
         raise ValueError(f"'{current_surgery.patient_name}'named patient has no surgeon.")

        duration = current_surgery.duration_slots

        surgeon = current_surgery.surgeon
        surgeon_id = surgeon.id
        required_room_id = current_surgery.required_room.id if current_surgery.required_room else None

        current_date = self.start_date
        while current_date <= self.end_date:
            date_str = current_date.strftime("%d-%m-%Y")

            for room in self.rooms:
                for start_slot in range(1, self.total_daily_slots + 1):

                    if self._is_valid_replacement(date_str, room.id, start_slot, duration, required_room_id):

                        resources_ok, available_team, soft_penalty = self._get_available_resources(
                            date_str, current_date, start_slot, surgeon, duration
                        )

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

                            should_stop = self._backtracking_algorithm(surgeries, index + 1, current_penalty + soft_penalty)

                            self.final_assignment.pop()
                            self._remove(date_str, room.id, start_slot, surgeon_id, available_team.id, duration)

                            if should_stop:
                                return True

            current_date += timedelta(days=1)

        return False

    def generate_schedule_plan(self):
        self._initialize_grids()
        surgeries_to_plan = self._get_sorted_surgeries()

        if not surgeries_to_plan:
            return {"status": "success", "message": "There's no surgery to plan.", "data": []}

        self._backtracking_algorithm(surgeries_to_plan, 0, 0)

        if self.best_assignment is not None:
            try:
                created_schedules = []
                with transaction.atomic():
                    for asg in self.best_assignment:
                        schedule = Schedule.objects.create(
                            date=asg['date'],
                            start_slot=asg['start_slot'],
                            end_slot=asg['end_slot'],
                            room_id=asg['room_id'],
                            surgeon_id=asg['surgeon_id'],
                            team_id=asg['team_id'],
                            surgery_id=asg['surgery_id']
                        )
                        created_schedules.append(schedule)

                return {
                    "status": "success",
                    "message": f"{len(created_schedules)} surgeries successfully planned.",
                    "planned_count": len(created_schedules),
                    "soft_penalty_score": self.best_score,
                    "data": created_schedules,
                }

            except Exception as e:
                return {"status": "error", "message": f"There's an error occured during query: {str(e)}"}

        else:
            return {"status": "error", "message": "There's an error occured during planning. Please configure the constraints or timezone."}
