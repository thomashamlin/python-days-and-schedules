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
