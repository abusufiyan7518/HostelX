from ComplainXHostel_app.models import Room

def generate_hostel_rooms():
    """
    Creates rooms like:
    Boys: 111-120, 211-220, 311-320, 411-420
    Girls: 101-110, 201-210, 301-310, 401-410
    """

    created = 0

    for floor in range(1, 5):

        # GIRLS (101-110)
        for num in range(1, 11):
            room_number = f"{floor}0{num}"   # 101, 102...

            obj, is_created = Room.objects.get_or_create(
                room_number=room_number,
                defaults={
                    "wing": "girls",
                    "floor": floor,
                    "capacity": 3
                }
            )

            if is_created:
                created += 1

        # BOYS (111-120)
        for num in range(11, 21):
            room_number = f"{floor}{num}"   # 111, 112...

            obj, is_created = Room.objects.get_or_create(
                room_number=room_number,
                defaults={
                    "wing": "boys",
                    "floor": floor,
                    "capacity": 3
                }
            )

            if is_created:
                created += 1

    return created