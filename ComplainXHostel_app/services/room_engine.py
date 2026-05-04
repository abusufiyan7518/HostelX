from django.db.models import F
from ComplainXHostel_app.models import Room, Student, RoomWaitingList


def assign_student_to_room(student):

    rooms = Room.objects.filter(wing=student.wing)

    if not rooms.exists():
        return add_to_waiting(student)

    best_room = None
    best_score = -1

    for room in rooms:

        occupants = Student.objects.filter(room=room, is_active=True)
        count = occupants.count()

        if count >= room.capacity:
            continue

        score = 0

        same_course = occupants.filter(course=student.course).count()
        same_year = occupants.filter(current_year=student.current_year).count()

        # 🎯 grouping priority
        if count > 0 and same_course == count and same_year == count:
            score += 100
        elif same_course > 0:
            score += 70
        elif count > 0:
            score += 40
        else:
            score += 20

        # 🎯 fill rooms first
        score += count * 15

        # 🎯 AC strict preference
        if room.is_ac == student.prefers_ac:
            score += 50
        else:
            score -= 20   # penalize mismatch

        if score > best_score:
            best_score = score
            best_room = room

    if best_room:
        student.room = best_room
        student.is_active = True
        student.save()

        return {
            "status": "assigned",
            "room": best_room.room_number
        }

    return add_to_waiting(student)


def add_to_waiting(student):
    RoomWaitingList.objects.get_or_create(
        user=student.user,
        defaults={"wing": student.wing}
    )

    return {"status": "waiting"}
# ================= GRADUATION =================
# def graduate_and_release_rooms():

#     graduated_students = Student.objects.filter(
#         current_year__gte=F("course_duration"),
#         is_active=True
#     )

#     for student in graduated_students:

#         freed_room = student.room

#         student.is_active = False
#         student.room = None
#         student.save()

#         if freed_room:

#             waiting = RoomWaitingList.objects.filter(
#                 wing=student.wing
#             ).order_by("created_at").first()

#             if waiting:

#                 next_student = Student.objects.get(user=waiting.user)

#                 next_student.room = freed_room
#                 next_student.save()

#                 waiting.delete()


# ================= ROOM GENERATION =================
def generate_rooms_bulk():

    for floor in range(1, 5):

        # GIRLS NON-AC
        for i in range(1, 11):
            Room.objects.get_or_create(
                room_number=f"{floor}0{i}",
                defaults={
                    "floor": floor,
                    "wing": "girls",
                    "capacity": 3,
                    "is_ac": False
                }
            )

        # BOYS AC
        for i in range(11, 16):
            Room.objects.get_or_create(
                room_number=f"{floor}{i}",
                defaults={
                    "floor": floor,
                    "wing": "boys",
                    "capacity": 3,
                    "is_ac": True
                }
            )

        # BOYS NON-AC
        for i in range(16, 21):
            Room.objects.get_or_create(
                room_number=f"{floor}{i}",
                defaults={
                    "floor": floor,
                    "wing": "boys",
                    "capacity": 3,
                    "is_ac": False
                }
            )