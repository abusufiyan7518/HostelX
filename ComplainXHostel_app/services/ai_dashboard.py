def ai_dashboard(students):

    high_risk = []
    room_pressure = {}

    for s in students:

        # student reaching final year
        if s.course_duration == s.current_year:
            high_risk.append(s)

        if s.room_number:
            room_pressure[s.room_number] = room_pressure.get(s.room_number, 0) + 1

    return {
        "high_risk_students": high_risk,
        "room_pressure": room_pressure
    }