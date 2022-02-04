import datetime


def year(request):
    now = datetime.datetime.now()
    """Добавляет переменную с текущим годом."""
    return {
        'year': now.year
    }
