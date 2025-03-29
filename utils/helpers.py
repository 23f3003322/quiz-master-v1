from datetime import datetime,timedelta, date


from datetime import datetime, timedelta

def is_quiz_active(quiz):
    now = datetime.now()
    quiz_start = datetime.combine(quiz.date_of_quiz, quiz.start_time)
    quiz_end = quiz_start + timedelta(minutes=quiz.time_duration)

    if now < quiz_start:
        return False, f"Quiz has not started yet. It starts on {quiz.date_of_quiz} at  {quiz_start.strftime('%H:%M')}"
    elif now > quiz_end:
        return False, f"Quiz time has ended. It ended on {quiz.date_of_quiz}  at {quiz_end.strftime('%H:%M')}"

    return True, None  



def convert_time_to_db_time(time_str):
    
    time_str = time_str.strip()  

    time_parts = time_str.split(":")
    if len(time_parts) == 3:  
        time_str = f"{time_parts[0]}:{time_parts[1]}"
    
    try:
        time_obj = datetime.strptime(time_str, "%H:%M").time()  
        return time_obj
    except ValueError:
        raise ValueError("Invalid time format. Expected 'HH:MM' or 'HH:MM:SS'.")
    


def validate_quiz_date(date_value):
    if isinstance(date_value, str):  
        date_value = datetime.strptime(date_value, '%Y-%m-%d').date()

    if date_value < date.today():
        raise ValueError("Quiz date cannot be in the past!")

    return date_value

    


def convert_to_time(time_value):

    if isinstance(time_value, str): 
        print("call is here1") 
        return datetime.strptime(time_value, '%H:%M').time()
    elif isinstance(time_value, datetime.time):  
        print("call is here2") 
        return time_value
    else:
        raise ValueError("Invalid time format. Expected 'HH:MM' string or time object.")