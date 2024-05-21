from datetime import datetime

def parse_date(date_str):
    date_formats = [
        '%a, %d %b %Y %H:%M:%S %z',  # Format with timezone
        '%a, %d %b %Y %H:%M:%S GMT',  # Format without timezone
        '%d %b %Y',  # Day month year format
    ]
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Не удалось распарсить дату: {date_str}")

def display_date(date_str):
    try:
        date = parse_date(date_str)
        return date.strftime('%d %b %Y')
    except ValueError:
        return 'Без даты'
