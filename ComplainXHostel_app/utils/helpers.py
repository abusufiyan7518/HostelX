from ComplainXHostel_app.models import Student

def get_student(user):
    try:
        return Student.objects.get(user=user)
    except Student.DoesNotExist:
        return None

def get_wing_from_warden(warden):
    return "boys" if warden.gender == "Male" else "girls"