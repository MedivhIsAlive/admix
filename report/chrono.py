from datetime import datetime
from dateutil.relativedelta import relativedelta

from django.utils import timezone

from typing import Iterator, Optional

from report.period import Period


def iter_period_starts(
    start_date: Optional[datetime],
    end_date: Optional[datetime] = None,
    period: Period = Period.WEEKLY,
) -> Iterator[datetime]:
    """
    Yields dates between start and end.
    param start: required, cannot be None
    param end: if None, end = now()
    param period: default 'weekly'
    """

    if start_date is None:
        raise ValueError("start date is required")

    if end_date is None:
        end_date = timezone.now()

    if period == Period.DAILY:
        step = relativedelta(days=1)
    elif period == Period.WEEKLY:
        step = relativedelta(weeks=1)
    elif period == Period.MONTHLY:
        step = relativedelta(months=1)
    else:
        raise ValueError(f"unknown period: {period}")

    current_date = start_date
    while current_date <= end_date:
        if current_date + step > end_date:
            yield current_date, end_date
        else:
            yield current_date, current_date + step
        current_date += step
