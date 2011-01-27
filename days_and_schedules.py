"""
Intuitive abstractions for day ranges and weekly schedules.

Examples (see the doctests below for more):
    Create a day range and iterate over it: 
        for d in day_range

    Slice it (zero-based):
        day_range[1:5]

    Test for containment: 
        date(2011, 1, 1) in work_schedule
        'Monday' in work_schedule 
        'Fri' in work_schedule
        'U' in work_schedule

    print day_range -> "<DayRange 09/01/2009 - 09/04/2009>"
    len(day_range) -> 4

Implements a byte serialization format as well as human-readable representations
for weekly schedules.  Also provides some basic integrity checking of dates and
schedules.  

Author:  Thomas Hamlin <thomas@metaphorlab.com>
URL:     https://github.com/thomashamlin/python-days-and-schedules
"""
from datetime import date, timedelta, datetime as dt

WEEKDAY_INTS = [0, 1, 2, 3, 4, 5, 6]
WEEKDAY_BITS = [1, 2, 4, 8, 16, 32, 64]
WEEKDAY_ABBR1 = ['M', 'T', 'W', 'R', 'F', 'S', 'U']
WEEKDAY_ABBR2 = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su']
WEEKDAY_ABBR3 = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
WEEKDAY_ABBR3_CAPS = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
WEEKDAY_NAMES = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

class DayRange(object):
    """Abstraction of a date range.

    >>> from datetime import date, timedelta
    >>> r = DayRange(date(2009, 6, 1), date(2009, 6, 4))
    >>> len(r)
    4

    >> r = DayRange(date(2009, 6, 1), date(1, 1, 1))
    ValueError
    """
    def __init__(self, start, end):
        """Create a new dayrange, start and end inclusive."""
        try:
            self.reset(start.date(), end.date())
        except AttributeError:
            self.reset(start, end)

    def reset(self, start, end):
        if end < start:
            raise ValueError
        self.start = start
        self.end = end
        self.dates = [d for d in self]

    def __len__(self):
        return (self.end - self.start).days + 1

    def __iter__(self):
        """Iterate over the dates in this dayrange.

        >>> r = DayRange(date(2009, 8, 1), date(2009, 8, 5))
        >>> [day.strftime('%m-%d') for day in r]
        ['08-01', '08-02', '08-03', '08-04', '08-05']

        >>> r = DayRange(date(2009, 8, 1), date(2009, 8, 1))
        >>> [day.strftime('%m-%d') for day in r]
        ['08-01']
        """
        return self.next()

    def next(self):
        d = self.start
        upperbound = self.end + timedelta(1)
        while d < upperbound:
            yield d
            d = d + timedelta(1)

    def __contains__(self, day):
        """
        >>> r = DayRange(date(2009, 8, 1), date(2009, 8, 5))
        >>> date(2009, 8, 4) in r
        True
        >>> dt(2009, 8, 4) in r
        True
        >>> date(2009, 8, 6) in r
        False

        >>> r = DayRange(dt(2009, 8, 1), dt(2009, 8, 5))
        >>> date(2009, 8, 4) in r
        True
        >>> dt(2009, 8, 4) in r
        True
        >>> date(2009, 8, 6) in r
        False
        """
        contained = day in self.dates
        if contained:
            return True
        try:
            return day.date() in self.dates
        except AttributeError:
            return False

    def __getslice__(self, i, j):
        """
        >>> r = DayRange(date(2009, 8, 1), date(2009, 8, 5))
        >>> print r[1:3] 
        <DayRange 08/02/2009 - 08/04/2009>
        """
        return DayRange(self.dates[max(0, i)], self.dates[max(0, j)])

    def __str__(self):
        """
        >>> print DayRange(date(2009, 9, 1), date(2009, 9, 17))
        <DayRange 09/01/2009 - 09/17/2009>
        """
        return "<DayRange %s - %s>" % (self.start.strftime("%m/%d/%Y"), self.end.strftime("%m/%d/%Y"))

    def dates_for_weeklyschedule(self, weekly_schedule):
        """Return list of dates within this dayrange that coincide with the days
        represented by the WeeklySchedule object.

        >>> r = DayRange(date(2009, 9, 1), date(2009, 9, 17))
        >>> fridays = WeeklySchedule(weekdays=['F'])
        >>> r.dates_for_weeklyschedule(fridays)
        [datetime.date(2009, 9, 4), datetime.date(2009, 9, 11)]
        >>> mon_to_fri = WeeklySchedule(weekdays=['M', 'T', 'W', 'R', 'F'])
        >>> r.dates_for_weeklyschedule(mon_to_fri)
        [datetime.date(2009, 9, 1), datetime.date(2009, 9, 2), datetime.date(2009, 9, 3), datetime.date(2009, 9, 4), datetime.date(2009, 9, 7), datetime.date(2009, 9, 8), datetime.date(2009, 9, 9), datetime.date(2009, 9, 10), datetime.date(2009, 9, 11), datetime.date(2009, 9, 14), datetime.date(2009, 9, 15), datetime.date(2009, 9, 16), datetime.date(2009, 9, 17)]
        """
        dates = []
        for d in self.dates:
            if d in weekly_schedule:
                dates.append(d)
        return dates


class WeeklySchedule(object):
    """Represents a calendar week schedule.

    This abstraction does not concern itself with what day the week
    starts.
    """
    def __init__(self, weekdays=None, byte=None):
        """'weekdays' is a sequence of 1-letter weekday abbreviations.

        >>> print WeeklySchedule(byte=127)
        ['M', 'T', 'W', 'R', 'F', 'S', 'U']
        >>> print WeeklySchedule(weekdays=['Mon', 'Tue', 'Wed'])
        ['M', 'T', 'W']
        >>> print WeeklySchedule(weekdays=['Monday', 'Th', 'F', 'Su'])
        ['M', 'R', 'F', 'U']
        >>> print WeeklySchedule(byte=3)
        ['M', 'T']
        >>> print WeeklySchedule(byte=8)
        ['R']
        """
        if weekdays is not None:
            self.from_names(weekdays)
        elif byte is not None:
            self.from_byte(byte)
        else:
            self.from_names([])

    def from_byte(self, byte):
        """Set schedule corresponding to byte representation given.
        """
        index = 0
        self._weekday_ints = []
        for daybit in WEEKDAY_BITS:
            if daybit & byte:
                self._weekday_ints.append(index)
            index += 1

    def from_names(self, weekdays):
        """Return list of integers corresponding to specified list of day names.
        'weekdays' may be list of 1, 2, or 3 letter day abbreviations, or full names.
        """
        ints = []
        for day in weekdays:
            if day in WEEKDAY_INTS:
                ints.append(WEEKDAY_INTS.index(day))
            elif day in WEEKDAY_NAMES:
                ints.append(WEEKDAY_NAMES.index(day))
            elif day in WEEKDAY_ABBR1:
                ints.append(WEEKDAY_ABBR1.index(day))
            elif day in WEEKDAY_ABBR2:
                ints.append(WEEKDAY_ABBR2.index(day))
            elif day in WEEKDAY_ABBR3:
                ints.append(WEEKDAY_ABBR3.index(day))
        self._weekday_ints = ints

    def to_byte(self):
        """Return single byte integer representing the schedule

        >>> WeeklySchedule(weekdays=['M']).to_byte()
        1
        >>> WeeklySchedule(weekdays=['T', 'W']).to_byte()
        6
        >>> WeeklySchedule(weekdays=['T', 'R']).to_byte()
        10
        >>> WeeklySchedule(weekdays=['M', 'F']).to_byte()
        17
        >>> WeeklySchedule(weekdays=['F', 'S']).to_byte()
        48
        >>> WeeklySchedule(weekdays=['U']).to_byte()
        64
        >>> WeeklySchedule(weekdays=['M','T','W','R','F','S','U']).to_byte()
        127
        """
        byte = 0
        for day in self._weekday_ints:
            byte |= WEEKDAY_BITS[day]
        return byte

    def __iter__(self):
        """Iterate over the weekdays in this schedule.

        >>> s = WeeklySchedule(weekdays=['M', 'T', 'W'])
        >>> [day for day in s]
        ['M', 'T', 'W']

        """
        return self.next()

    def next(self):
        for i in self._weekday_ints:
            yield WEEKDAY_ABBR1[i]

    def __contains__(self, day):
        """Return true if schedule contains date, weekday number, weekday name/abbr

        >>> s = WeeklySchedule(weekdays=['M', 'T', 'W'])
        >>> from datetime import date
        >>> some_thursday = date(2009, 7, 2)
        >>> some_thursday in s
        False
        >>> some_monday = date(2009, 8, 31)
        >>> some_monday in s
        True
        >>> 0 in s
        True
        >>> 1 in s
        True
        >>> 3 in s
        False
        >>> 'M' in s
        True
        >>> 'Monday' in s
        True
        >>> 'Saturday' in s
        False
        >>> 'Invalid string' in s
        False
        """
        try:
            return day.weekday() in self._weekday_ints
        except AttributeError:
            return day in self._weekday_ints \
                or (day in WEEKDAY_ABBR1 and WEEKDAY_ABBR1.index(day) in self._weekday_ints) \
                or (day in WEEKDAY_ABBR2 and WEEKDAY_ABBR2.index(day) in self._weekday_ints) \
                or (day in WEEKDAY_ABBR3 and WEEKDAY_ABBR3.index(day) in self._weekday_ints) \
                or (day in WEEKDAY_NAMES and WEEKDAY_NAMES.index(day) in self._weekday_ints)

    def __eq__(self, other):
        try:
            return self.to_byte() == other.to_byte()
        except AttributeError:
            # Other is not a WeeklySchedule, so may be a list of days.
            # If other is a dict, string, or incorrect list, will result in
            # an empty schedule.
            try:
                return self == WeeklySchedule(weekdays=other).to_byte()
            except TypeError:
                return False

    def __ne__(self, other):
        return not self == other

    def __str__(self, repr=None):
        if not repr:
            repr = WEEKDAY_ABBR1
        return "[%s]" % (", ".join([("'%s'" % repr[d]) for d in self._weekday_ints]))

if __name__ == '__main__':
    import doctest
    doctest.testmod()
