from datetime import timedelta
from django.utils import timezone

def calculate_sm2(quality: int, repetitions: int, easiness_factor: float, interval: int):
    """
    SM-2 Algorithm implementation for Spaced Repetition.
    quality: 0-5 scale indicating how well the user remembered the item.
             5 - perfect response
             4 - correct response after a hesitation
             3 - correct response recalled with serious difficulty
             2 - incorrect response; where the correct one seemed easy to recall
             1 - incorrect response; the correct one remembered
             0 - complete blackout
    """
    if quality >= 3:
        if repetitions == 0:
            interval = 1
        elif repetitions == 1:
            interval = 6
        else:
            interval = int(round(interval * easiness_factor))
        repetitions += 1
    else:
        repetitions = 0
        interval = 1

    easiness_factor = easiness_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    if easiness_factor < 1.3:
        easiness_factor = 1.3

    return easiness_factor, interval, repetitions

def get_next_review_date(interval: int):
    return timezone.now() + timedelta(days=interval)
