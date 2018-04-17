import requests
import math
import numpy as np
import utm
# EXTERNAL SOURCES HAVE BEEN CITED APPROPIATELY AND LOOK AT MAIN FUNCTION FOR STUDENT'S WORK (FINN ZHAN CHEN)

##################### EXISING SOLUTION FOR CALCULATING DISTANCE FROM RSSI ################
# Source from http://developer.radiusnetworks.com/2014/12/04/fundamentals-of-beacon-ranging.html

def getDistanceFromRSSI(rssi, txPower): # in metres
    #tx values usually ranges from -59 to -65
    if rssi == 0:
        return -1

    ratio = rssi*1.0/txPower;
    if ratio < 1.0:
        return math.pow(ratio, 10)
    else:
        accuracy = (0.89976) * math.pow(ratio, 7.7095) + 0.111
        return accuracy


###################### EXISTING SOLUTION FOR TRILATERATION IN 2D ##############################
# Source from https://github.com/noomrevlis/trilateration
# http://en.wikipedia.org/wiki/Trilateration

class point(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y


class circle(object):
    def __init__(self, point, radius):
        self.center = point
        self.radius = radius

def get_two_points_distance(p1, p2):
    return math.sqrt(pow((p1.x - p2.x), 2) + pow((p1.y - p2.y), 2))


def get_two_circles_intersecting_points(c1, c2):
    p1 = c1.center
    p2 = c2.center
    r1 = c1.radius
    r2 = c2.radius

    d = get_two_points_distance(p1, p2)
    # if to far away, or self contained - can't be done
    if d >= (r1 + r2) or d <= math.fabs(r1 - r2):
        return None

    a = (pow(r1, 2) - pow(r2, 2) + pow(d, 2)) / (2 * d)
    h = math.sqrt(pow(r1, 2) - pow(a, 2))
    x0 = p1.x + a * (p2.x - p1.x) / d
    y0 = p1.y + a * (p2.y - p1.y) / d
    rx = -(p2.y - p1.y) * (h / d)
    ry = -(p2.x - p1.x) * (h / d)
    return [point(x0 + rx, y0 - ry), point(x0 - rx, y0 + ry)]


def get_all_intersecting_points(circles):
    points = []
    num = len(circles)
    for i in range(num):
        j = i + 1
        for k in range(j, num):
            res = get_two_circles_intersecting_points(circles[i], circles[k])
            if res:
                points.extend(res)
    return points

def is_contained_in_circles(point, circles):
    for i in range(len(circles)):
        if (get_two_points_distance(point, circles[i].center) >= (circles[i].radius)):
            return False
    return True


def get_polygon_center(points):
    center = point(0, 0)
    num = len(points)
    for i in range(num):
        center.x += points[i].x
        center.y += points[i].y
    center.x /= num
    center.y /= num
    return center

######################## WRITTEN BY STUNDET FINN ZHAN CHEN ########################################

class Beacon(object):
    def __init__(self, deviceMac, lat, lng, txPower):
        self.deviceMac = deviceMac
        self.lat = lat
        self.lng = lng
        # Tx is the strength of the transmission signal measured at a distance of one meter from the transmitter.
        # The following tx power has been calculated by collecting more than 30 rssi of the beacon
        # around 1 metres from the beacon, outliers have been removed and the mean is calculated
        # data collected are saved on an excel file and input to this algorithm
        # https://www.kdnuggets.com/2017/02/removing-outliers-standard-deviation-python.html
        self.umtPoint = self.createUTMPoint(lat, lng)
        # Do not know the radius at this point
        self.circle = circle(self.umtPoint, 0)
        self.txPower = txPower
        self.pastRssi = list()

    def convertLatLngToUTM(self, lat, lng):
        (x, y, _, _) = utm.from_latlon(lat, lng)
        return x, y

    def createUTMPoint(self, lat, lng):
        x, y = self.convertLatLngToUTM(lat, lng)
        #print(x, y)
        return point(x, y)

    def getDistanceToBeacon(self):
        return getDistanceFromRSSI(rssi=self.getPastRssiAverage(), txPower=self.txPower)

    def getPastRssiAverage(self):
        if len(self.pastRssi) == 0:
            return 0
        else:
            ##################### EXISING SOLUTION FOR REMOVING OUTLIERS ###########################
            # Source from https://www.kdnuggets.com/2017/02/removing-outliers-standard-deviation-python.html
            elements = np.array(self.pastRssi)
            mean = np.mean(elements, axis=0)
            sd = np.std(elements, axis=0)
            # Removes outliers and return filtered mean past RSSIs
            final_list = [x for x in self.pastRssi if (x >= mean - 2 * sd)]
            final_list = [x for x in final_list if (x <= mean + 2 * sd)]
            return np.mean(final_list)
    def debug(self):
        print(self.deviceMac + " " + str(self.pastRssi) + " " + str(self.getPastRssiAverage()))

def getThreeBeaconsForTrilateration(discoveredBeacons):
    # Return 3 closest beacons as a list
    threeBeacons = list()
    distances = dict() # key is distance and value is Beacon object
    for deviceMac in discoveredBeacons:
        distances[beaconsMap[deviceMac].getDistanceToBeacon()] = beaconsMap[deviceMac]

    # Return the 3 closest beacons by sorting the key which is the distance
    #print("Three closest beacon")
    for distance in sorted(distances)[:3]:
        #distances[distance].debug()
        #print(distances[distance].deviceMac + " " + str(distance))
        threeBeacons.append(distances[distance])

    return threeBeacons

def getSeconds(lastTimestamp):
    # Timestamp is of this string format "yyyy-MM-dd HH:mm:ss.SSS"
    hourMinuteSecondMillisecondReference = lastTimestamp.split(" ")[1].split(":")
    totalSecondsReference = float(hourMinuteSecondMillisecondReference[2]) \
                            + float(hourMinuteSecondMillisecondReference[1]) * 60 \
                            + float(hourMinuteSecondMillisecondReference[0]) * 60 * 60
    return totalSecondsReference

def timeDifference(timeReference, time):
    return timeReference - time


def getTrilaterationResult(beacons):
    circle_list = list()
    for deviceMac in beacons:
        beacons[deviceMac].circle.radius = beacons[deviceMac].getDistanceToBeacon()
        circle_list.append(beacons[deviceMac].circle)

    inner_points = []
    for p in get_all_intersecting_points(circle_list):
        if is_contained_in_circles(p, circle_list):
            inner_points.append(p)

    if len(inner_points) > 0:
        center = get_polygon_center(inner_points)
        (lat, lng) = utm.to_latlon(center.x, center.y, 30, 'U')
        return lat, lng
    else:

        return "nan", "nan"

if __name__ == "__main__":
    beaconsMap = {
        "ED23C0D875CD": Beacon("ED23C0D875CD", 55.9444578385393, -3.1866151839494705, -97.25),
        "E7311A8EB6D7": Beacon("E7311A8EB6D7", 55.94444244275808, -3.18672649562358860, -95.97222222),
        "C7BC919B2D17": Beacon("C7BC919B2D17", 55.94452336441765, -3.1866540759801865, -66.78431373),
        "EC75A5ED8851": Beacon("EC75A5ED8851", 55.94452261340533, -3.1867526471614838, -90.24),
        "FE12DEF2C943": Beacon("FE12DEF2C943", 55.94448393625199, -3.1868280842900276, -89.55555556),
        "C03B5CFA00B8": Beacon("C03B5CFA00B8", 55.94449050761571, -3.1866483762860294, -53.17647059),
        "E0B83A2F802A": Beacon("E0B83A2F802A", 55.94443774892113, -3.1867992505431175, -99.88888889),
        "F15576CB0CF8": Beacon("F15576CB0CF8", 55.944432116316044, -3.186904862523079, -90.0),
        "F17FB178EA3D": Beacon("F17FB178EA3D", 55.94444938963575, -3.1869836524128914, -85.38888889),
        "FD8185988862": Beacon("FD8185988862", 55.94449107087541, -3.186941407620907, -90.02941176)
    }
    # a map of discovered Beacon objects
    discoveredBeacons = dict()
    # Calibration required, I found this via eye inspection via my custom Android Google Maps app
    latLngCalibration = (-0.000025, -0.0000025)

    # Authorisation header for GET and POST request
    myheaders = {"Authorization":"Bearer 57:3996aa851ea17f9dd462969c686314ed878c0cf7"}
    readingsUrl = 'http://glenlivet.inf.ed.ac.uk:8080/api/v1/svc/apps/data/docs/everything'
    estimatedPositionUrl = 'http://glenlivet.inf.ed.ac.uk:8080/api/v1/svc/apps/data/docs/estimatedposition'

    readingsResponse = requests.get(readingsUrl, headers=myheaders)
    #print(r.text)
    #print(r.json())

    # ALL CONTENT OF THE PRINT STATEMENT HAVE BEEN FORMATTED IN THE FOLLOWING WAY
    # LINE 1 CONTAINS THE ESTIMATED POSITION OR ERROR MESSAGES
    # ALL OTHER LIENS CONTAINS THE BEACON'S DEVICE_MAC AND THE DISTANCE TO BEACON
    # NOTE WHEN THERE ARE NO ENOUGH BEACONS FOR TRILATERATION, THE LAST KNOWN POSITION WILL BE USED
    # TO INTERPOLATE THE NEW POSITION. IN THIS CASE THE LAST KNOWN POSITION IS TREATED AS A BEACON
    # AND ITS DISTANCE TO LAST KNOWN POSITION IS ALSO PRINTED AS A BEACON
    # THE PURPOSE OF THIS IS SO THAT IT CAN BE VISUALISED ON THE ANDROID APP
    if len(readingsResponse.json()) > 0:
        # This is used as a reference timestamp to get all readings in the past x seconds
        lastTimestamp = readingsResponse.json()[len(readingsResponse.json()) - 1]["timestamp"] # Get last timestamp
        timeReference = getSeconds(lastTimestamp)

        # Start iteration from the last item (newest beacon info)
        # Reverse the json file and read all readings from the past 3 seconds
        for item in readingsResponse.json()[::-1]:
            try:
                timestamp = item["timestamp"]
                deviceMac =  item["device_mac"]
                rssi = int(item["rssi"])
                # only considers values in the past 3 seconds
                timeDif =timeDifference(timeReference, getSeconds(timestamp))
                #print(timeDif)
                if  timeDif <= 8:
                    #print(timestamp + " | " + device_mac + " | " + str(rssi))
                    if not deviceMac in discoveredBeacons:
                        # convert metres to kilometres for the trilateration algorithm later
                        discoveredBeacons[deviceMac] = beaconsMap[deviceMac]

                    # record seen rssi value in the past 3 seconds to beacons
                    beaconsMap[deviceMac].pastRssi.append(rssi)
                else:
                    break
            except:
                #print("Not in format")
                pass

    #for device_mac in discoveredBeacons:
        #print(beaconsMap[device_mac].deviceMac)

    if len(discoveredBeacons) >= 3:
        # returns a
        #threeBeaconsForTrilateration = getThreeBeaconsForTrilateration(discoveredBeacons)
        estimated_lat, estimated_lon = getTrilaterationResult(discoveredBeacons)

        if (estimated_lat == "nan" or estimated_lon == "nan"):
            # Cannot estimate because there is no overlapping areas between the base stations
            print("null")
        else:
            # Successful estimated the position
            # post estimated position to the Cloud
            requests.post(estimatedPositionUrl, data={"timestamp": lastTimestamp,
                                                        "lat": repr(estimated_lat),
                                                        "lon": repr(estimated_lon)
                                                        }, headers = myheaders)

            print(str(estimated_lat)  + "," + str(estimated_lon)) # might need to calibrate the algorithm response
    elif len(discoveredBeacons) == 2:
        # Interpolating 2 beacons with the last estimated position
        estimatedPositionResponse = requests.get(estimatedPositionUrl, headers=myheaders)
        # Get last item which is the latest estimated position
        try:
            lastEstimatedPositionItem = estimatedPositionResponse.json()[::-1][0]
            timestamp = lastEstimatedPositionItem["timestamp"]
            past_lat = lastEstimatedPositionItem["lat"]
            past_lon = lastEstimatedPositionItem["lon"]
            # Only uses estimated location which were in the past 3 seconds
            # time difference is also used to estimated how far the user has gone from the past position
            # using the assumption that the user moves at 1 metres per second
            # This is used to make the last known position as a beacon with the distance travelled by user as a
            # clue for interpolation
            timeDif = timeDifference(timeReference, getSeconds(timestamp))
            if timeDif <= 8:

                estimated_lat, estimated_lon = getTrilaterationResult(discoveredBeacons)

                if (str(estimated_lat) == "nan" or str(estimated_lon) == "nan"):
                    # Cannot estimate because there is no overlapping areas between the base stations
                    print("null")
                else:
                    # Successful estimated the position
                    # post estimated position to the Cloud
                    requests.post(estimatedPositionUrl, data={"timestamp": lastTimestamp,
                                                              "lat": repr(estimated_lat),
                                                              "lon": repr(estimated_lon)
                                                              }, headers=myheaders)

                    print(str(estimated_lat) + "," + str(estimated_lon))  # might need to calibrate the algorithm response

                print("LastKnownPosition," + str(1*timeDif))

        except:
            print("Failed to interpolate")

    else:
        # There are no 3 beacons so cannot estimate
        print("Not enough beacons")

    for deviceMac in discoveredBeacons:
        #discoveredBeacons[deviceMac].debug()
        print(beaconsMap[deviceMac].deviceMac + "," + str(beaconsMap[deviceMac].getDistanceToBeacon()))
