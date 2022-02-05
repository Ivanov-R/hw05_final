from django.utils import timezone


def year(request):
    """Добавляет переменную с текущим годом."""
    now = timezone.now()
    current_year = now.year
    return {
        "year": current_year,
    }
