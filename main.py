import pandas
import numpy
from tvdatafeed.tvDatafeed.main import *

def return_time(time):
    try:
       if time == "1h":
           return Interval.in_1_hour
       elif time =="15m":
           return Interval.in_15_minute
       elif time == "30m":
           return Interval.in_30_minute
       elif time == "1m":
           return Interval.in_1_minute
       elif time == "5m":
           return Interval.in_5_minute
       elif time == "4h":
           return Interval.in_4_hour
       elif time == "2h":
           return Interval.in_2_hour
       elif time == "3h":
           return Interval.in_3_hour
       elif time == "3m":
           return Interval.in_3_minute
       elif time == "45m":
           return Interval.in_45_minute
       elif time == "1d":
           return Interval.in_daily
       elif time == "1w":
           return Interval.in_weekly
       elif time == "1M":
           return Interval.in_monthly

    except:
        return "Unknown time format"

        