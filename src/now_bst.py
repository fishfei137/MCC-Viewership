from datetime import datetime, timedelta

def now():
    now_dt = datetime.utcnow() #+ timedelta(hours=1)  #bst
    now = now_dt.strftime('%H:%M')
    return now

