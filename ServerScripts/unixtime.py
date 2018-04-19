from datetime import date
from time import mktime
#2018-04-17 19:59:51.940
def getSeconds(lastTimestamp):
    # Timestamp is of this string format "yyyy-MM-dd HH:mm:ss.SSS"
    hourMinuteSecondMillisecondReference = lastTimestamp.split(" ")[1].split(":")
    totalSecondsReference = float(hourMinuteSecondMillisecondReference[2]) \
                            + float(hourMinuteSecondMillisecondReference[1]) * 60 \
                            + float(hourMinuteSecondMillisecondReference[0]) * 60 * 60
    return totalSecondsReference

timestamp = "2018-04-17 19:59:51.940"
dateFormat = timestamp.split(" ")[0].split("-")
print(dateFormat)

start = date(int(dateFormat[0]), int(dateFormat[1]), int(dateFormat[2]))
unixTime = int(mktime(start.timetuple())*1000 + getSeconds(timestamp)*1000)
print(unixTime)