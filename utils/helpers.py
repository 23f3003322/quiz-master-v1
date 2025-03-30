from datetime import datetime,timedelta, date
import pytz

from datetime import datetime, timedelta
IST = pytz.timezone('Asia/Kolkata')

def is_quiz_active(quiz):
    ist_now = datetime.now(IST)  # Get current IST time


    quiz_start_naive = datetime.combine(quiz.date_of_quiz, quiz.start_time)  
    quiz_start = IST.localize(quiz_start_naive) 

    quiz_end = quiz_start + timedelta(minutes=quiz.time_duration)  

    print(f"Debug: IST Now: {ist_now}, Quiz Start: {quiz_start}, Quiz End: {quiz_end}")

    if ist_now < quiz_start:
        return False, f"Quiz has not started yet. It starts on {quiz.date_of_quiz} at {quiz_start.strftime('%H:%M')} IST"
    elif ist_now > quiz_end:
        return False, f"Quiz time has ended. It ended on {quiz.date_of_quiz} at {quiz_end.strftime('%H:%M')} IST"

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
    


def validate_quiz_date(date_value, start_time):
    try:

        if isinstance(date_value, str):
            date_value = datetime.strptime(date_value, '%Y-%m-%d').date()


        if isinstance(start_time, str):
            start_time = datetime.strptime(start_time, '%H:%M').time()


        now_utc = datetime.utcnow()
        now_ist = now_utc.replace(tzinfo=pytz.utc).astimezone(IST)


        quiz_start_naive = datetime.combine(date_value, start_time)  
        quiz_start_datetime = IST.localize(quiz_start_naive)  


        if quiz_start_datetime < now_ist:
            return "Quiz start time cannot be in the past!"

        return None  

    except Exception as e:
        return str(e)