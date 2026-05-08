from datetime import datetime

def fix_date(date: datetime):
    return date.strftime("%d/%m/%Y")