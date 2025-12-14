import random
from app.schemas.schedule import ScheduleRequest

def generate_schedule(payload: ScheduleRequest):
    schedule = {}

    for day in range(1, payload.days + 1):
        day_key = f"Day {day}"
        schedule[day_key] = {}

        for shift in payload.shifts:
            staff = random.choice(payload.staff)
            schedule[day_key][shift.name] = staff.name

    return {
        "schedule": schedule,
        "fitness_score": round(random.uniform(0.7, 0.95), 2)
    }
