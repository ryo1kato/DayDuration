#!/usr/bin/python

from datetime import *
import calendar
import re


#
# A utility class to calculate and hold a specific duration of days:
#
class DayDuration():
    """
    Usage: DayDuration("Description like 3monthago", today=date(2000,3,2))
           DayDuration()
    >>> d = DayDuration("3monthago", today=date(2000,3,2))
    >>> d.is_valid()
    True
    >>> d.begin()
    datetime.date(1999, 12, 1)
    >>> d.end()
    datetime.date(1999, 12, 31)
    >>> d.days()
    31
    >>> d.months()
    1
    >>> d = DayDuration("3 years ago", today=date(2000,3,2))
    >>> d.begin()
    datetime.date(1997, 1, 1)
    >>> d.end()
    datetime.date(1997, 12, 31)
    >>> d.days()
    365
    >>> d.months()
    12
    >>> d.years()
    1
    >>> d = DayDuration('un-parsable string')
    >>> d.is_valid()
    False
    >>> d = DayDuration('today', -1, today=date(2000,3,1))
    >>> d.days()
    1
    >>> d.begin()
    datetime.date(2000, 3, 1)
    >>> d.end()
    datetime.date(2000, 3, 1)
    >>> d = DayDuration('today', 0, today=date(2000,3,1))
    >>> d.days()
    1
    >>> d.begin()
    datetime.date(2000, 3, 1)
    >>> d.end()
    datetime.date(2000, 3, 1)
    >>> d = DayDuration('today', -2, today=date(2000,3,1))
    >>> d.days()
    2
    >>> d.begin()
    datetime.date(2000, 2, 29)
    >>> d.end()
    datetime.date(2000, 3, 1)
    >>> d = DayDuration('today', 3, today=date(2000,2,28))
    >>> d.days()
    3
    >>> d.begin()
    datetime.date(2000, 2, 28)
    >>> d.end()
    datetime.date(2000, 3, 1)
    """
    def __init__(self, pivot=None, duration=None, today=None):
        if today:
            self._today = today
        else:
            self._today = date.today()
        if isinstance(pivot, (str, unicode)):
            self.__init_pretty(pivot, duration)
        elif isinstance(pivot, date) and isinstance(duration, int):
            self.__init_by_date_days(pivot, duration)
        else:
            self._invalidate()

    def __init_by_date_days(self, pivot, days):
        if days > 0:
            self._date_begin = pivot
            self._days       = days
            self._date_end   = pivot + timedelta(days=days-1)
        elif days < 0:
            self._date_begin = pivot - timedelta(days=-days-1)
            self._days       = -days
            self._date_end   = pivot
        else: # days == 0
            self._date_begin = pivot
            self._date_end   = pivot
            self._days       = 1

    def __init_pretty(self, description, days):
        import sys
        pivot, days_tmp = self._parse_date(description)
        if pivot is None or days_tmp is None:
            self._invalidate()
        else:
            if days is not None:
                if days > 0:
                    self._date_begin = pivot
                    self._days       = days
                    self._date_end   = pivot + timedelta(days=days-1)
                elif days < 0:
                    self._date_begin = pivot - timedelta(days=-days-1)
                    self._days       = -days
                    self._date_end   = pivot
                else: #days==0
                    self._date_begin = pivot
                    self._date_end   = pivot
                    self._days       = 1
            else:
                    self._date_begin = pivot
                    self._days       = days_tmp
                    self._date_end   = pivot + timedelta(days=days_tmp-1)

    def _invalidate(self):
        self._date_begin = None
        self._days       = None
        self._date_end   = None

    def is_valid(self):
        return not self._date_begin is None and \
               not self._days       is None and \
               not self._date_end   is None and \
               (self._days >= 1) and \
               (self._date_begin <= self._date_end)
    def get(self):    return (self._date_begin, self._days, self._date_end)
    def begin(self):  return self._date_begin
    def end(self):    return self._date_end
    def days(self):   return self._days
    def months(self): return self._days / 30
    def years(self):  return self._days / 356
    def datelist(self):
        """
        >>> DayDuration(date(2011,1,1), 3).datelist()
        [datetime.date(2011, 1, 1), datetime.date(2011, 1, 2), datetime.date(2011, 1, 3)]
        >>> DayDuration(date(2000,2,28), 2).datelist()
        [datetime.date(2000, 2, 28), datetime.date(2000, 2, 29)]
        >>> DayDuration(date(2011,12,31), 3).datelist()
        [datetime.date(2011, 12, 31), datetime.date(2012, 1, 1), datetime.date(2012, 1, 2)]
        >>> DayDuration(date(2000,3,1), -2).datelist()
        [datetime.date(2000, 2, 29), datetime.date(2000, 3, 1)]
        """
        if not self.is_valid():
            return None
        elif self._days >= 1:
            return [ self._date_begin + timedelta(days=d) for d in range(self._days) ]
        else:
            return None

    def _months_ago(self, thedate, ago):
        """
        >>> d = DayDuration("xxx")
        >>> d._months_ago( date(2000,9,9), 1)
        (datetime.date(2000, 8, 1), 31)
        >>> d._months_ago( date(2000,9,9), 13)
        (datetime.date(1999, 8, 1), 31)
        >>> d._months_ago( date(2000,9,9), 19)
        (datetime.date(1999, 2, 1), 28)
        >>> d._months_ago( date(2000,2,15), 3)
        (datetime.date(1999, 11, 1), 30)
        >>> d._months_ago( date(2000,9,9), 99999999999999)
        (datetime.date(1, 1, 1), 31)
        """
        # You have to wrap-around to December of previous year, if it's January.
        new_year  = thedate.year-(ago/12)
        month_ago = ago%12
        if month_ago >= thedate.month:
            new_year = new_year - 1
            new_month = 12 - (month_ago - thedate.month)
        else:
            new_month = thedate.month - month_ago
        if new_year < 0:
            new_year = 1
            new_month = 1
        newdate = thedate.replace(year=new_year,
                                  month=new_month, day = 1)
        return (newdate, calendar.monthrange(new_year, new_month)[1])

    def _years_ago(self, thedate, ago):
        """
        >>> d = DayDuration("xxx")
        >>> d._years_ago( date(2000,12,1), 10 )
        (datetime.date(1990, 1, 1), 365)
        >>> d._years_ago( date(2000,12,1), 0 )
        (datetime.date(2000, 1, 1), 366)
        >>> d._years_ago( date(2000,12,1), 100 )
        (datetime.date(1900, 1, 1), 365)
        >>> d._years_ago( date(2000,12,1), 99999999999999999999)
        (datetime.date(1, 1, 1), 365)
        """
        if thedate.year <= ago:
            newyear = 1
        else:
            newyear = thedate.year - ago
        # care for leap year (365 days a year)
        newdate = date(newyear, 1, 1)
        yearEnd = date(newyear, 12, 31)
        return (newdate, (yearEnd-newdate).days+1)

    def _parse_iso_date(self, datestr):
        """
        >>> d = DayDuration("xxx")
        >>> d._parse_iso_date('2000-12-12')
        datetime.date(2000, 12, 12)
        >>> d._parse_iso_date('not an ISO date string') is None
        True
        """
        if datestr:
            try:
                return datetime.strptime(datestr, "%Y-%m-%d").date()
            except ValueError:
                return None
        else:
            return None

    def _parse_date(self, datestr, pivot=None):
        """
        >>> d = DayDuration("xxx")
        >>> d._today = date(2000, 3, 2)
        >>> d._today
        datetime.date(2000, 3, 2)
        >>> d._parse_date('today')
        (datetime.date(2000, 3, 2), 1)
        >>> d._parse_date('yesterday')
        (datetime.date(2000, 3, 1), 1)
        >>> d._parse_date('2 days ago')
        (datetime.date(2000, 2, 29), 1)
        >>> d._parse_date('thismonth')
        (datetime.date(2000, 3, 1), 2)
        >>> d._parse_date('lastmonth')
        (datetime.date(2000, 2, 1), 29)
        >>> d._parse_date('3monthago')
        (datetime.date(1999, 12, 1), 31)
        >>> d._parse_date('3yearsago')
        (datetime.date(1997, 1, 1), 365)
        >>> d._parse_date('400-years-ago')
        (datetime.date(1600, 1, 1), 366)
        """
        if pivot is None:
            pivot = self._today

        if not datestr:
            return None, 0

        if datestr == "today":
            return pivot, 1
        elif datestr == "yesterday":
            return pivot - timedelta(days=1), 1
        elif datestr == "thisweek":
            dayOfWeek=pivot.weekday() # monday=0, watch out for OBOE
            return (pivot - timedelta(days=dayOfWeek), dayOfWeek+1)
        elif datestr == "thismonth":
            return (pivot.replace(day=1), pivot.day)
        elif datestr == "thisyear":
            yearstart = pivot.replace(month=1, day=1)
            return (yearstart, (pivot - yearstart).days + 1)
        elif datestr == "lastweek":
            dayOfWeek=pivot.weekday()
            return (pivot - timedelta(days=(dayOfWeek+7)), 7)
        elif datestr == "lastmonth":
            return self._months_ago(pivot, 1)
        elif datestr == "lastyear":
            return self._years_ago(pivot, 1)
        else:
            dm = re.match("([0-9]+)[ _-]?days?[ _-]?ago", datestr)
            wm = re.match("([0-9]+)[ _-]?weeks?[ _-]?ago", datestr)
            mm = re.match("([0-9]+)[ _-]?months?[ _-]?ago", datestr)
            ym = re.match("([0-9]+)[ _-]?years?[ _-]?ago", datestr)
            if dm:
                return (pivot - timedelta(days=int(dm.group(1)))), 1
            elif wm:
                return (pivot - timedelta(days=int(wm.group(1))*7)), 7
            elif mm:
                return self._months_ago(pivot, int(mm.group(1)))
            elif ym:
                return self._years_ago(pivot, int(ym.group(1)))
            else:
                return self._parse_iso_date( datestr ), 1


## END of class DayDuration()


if __name__ == "__main__":
    print('-------- running doctest --------')
    import doctest
    #globs = dir()
    #globs = {'today': date(2000, 3, 1), 'foobar':1234567890}
    today = date(2000, 3, 2) # FIXME, how can I override globals in docstring?
    opts  = doctest.REPORT_ONLY_FIRST_FAILURE
    opts |= doctest.NORMALIZE_WHITESPACE
    opts |= doctest.REPORT_UDIFF
    opts |= doctest.REPORT_CDIFF
    opts |= doctest.ELLIPSIS
    doctest.testmod(optionflags=opts,
                    #globs=globs,
                    #extraglobs=globs,
                    )

