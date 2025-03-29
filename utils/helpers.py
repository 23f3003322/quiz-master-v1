from datetime import datetime,timedelta, date


def is_quiz_active(quiz):
    """Check if the quiz is currently active based on time."""
    now = datetime.now()
    quiz_start = datetime.combine(quiz.date_of_quiz, quiz.start_time)
    quiz_end = quiz_start + timedelta(minutes=quiz.time_duration)

    return quiz_start <= now <= quiz_end


def convert_time_to_db_time(time_str):
    """Convert 'HH:MM' string to a valid db.Time format."""
    try:
        time_obj = datetime.strptime(time_str, "%H:%M").time()  # Convert string to time object
        return time_obj 
    except ValueError:
        raise ValueError("Invalid time format. Expected HH:MM")
    


def validate_quiz_date(date_value):
    """Check if the quiz date is valid (not in the past)."""
    if isinstance(date_value, str):  # If it's a string, convert it to a date
        date_value = datetime.strptime(date_value, '%Y-%m-%d').date()

    if date_value < date.today():
        raise ValueError("Quiz date cannot be in the past!")

    return date_value

    


def convert_to_time(time_value):
    """Convert a string like '18:10' to a Python time object"""
    if isinstance(time_value, str):  # Ensure it's a string before parsing
        return datetime.strptime(time_value, '%H:%M').time()
    elif isinstance(time_value, datetime.time):  # If it's already time, return it
        return time_value
    else:
        raise ValueError("Invalid time format. Expected 'HH:MM' string or time object.")