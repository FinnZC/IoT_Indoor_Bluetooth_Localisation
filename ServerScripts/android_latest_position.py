import requests
import math
import numpy as np

# EXTERNAL SOURCES HAVE BEEN CITED APPROPIATELY AND LOOK AT MAIN FUNCTION FOR STUDENT'S WORK (FINN ZHAN CHEN)

##################### EXISING SOLUTION FOR CALCULATING DISTANCE FROM RSSI ################
# Source from https://stackoverflow.com/questions/22784516/estimating-beacon-proximity-distance-based-on-rssi-bluetooth-le

def getDistanceFromRSSI(rssi, txPower):  # in metres
    # tx values usually ranges from -59 to -65
    if rssi == 0:
        return -1
    return math.pow(10, (txPower - rssi) / (10 * 2))


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


######################## SCRIPTS FROM UTM PACKAGE  ###############################################
# THIS IS COPY PASTED HERE SO THAT THE MAIN PACKAGE DOESN'T HAVE TO BE INSTALLED ON THE SERVER
# SOURCE: https://pypi.org/project/utm/
K0 = 0.9996

E = 0.00669438
E2 = E * E
E3 = E2 * E
E_P2 = E / (1.0 - E)

SQRT_E = math.sqrt(1 - E)
_E = (1 - SQRT_E) / (1 + SQRT_E)
_E2 = _E * _E
_E3 = _E2 * _E
_E4 = _E3 * _E
_E5 = _E4 * _E

M1 = (1 - E / 4 - 3 * E2 / 64 - 5 * E3 / 256)
M2 = (3 * E / 8 + 3 * E2 / 32 + 45 * E3 / 1024)
M3 = (15 * E2 / 256 + 45 * E3 / 1024)
M4 = (35 * E3 / 3072)

P2 = (3. / 2 * _E - 27. / 32 * _E3 + 269. / 512 * _E5)
P3 = (21. / 16 * _E2 - 55. / 32 * _E4)
P4 = (151. / 96 * _E3 - 417. / 128 * _E5)
P5 = (1097. / 512 * _E4)

R = 6378137

ZONE_LETTERS = "CDEFGHJKLMNPQRSTUVWXX"


def to_latlon(easting, northing, zone_number, zone_letter=None, northern=None, strict=True):
    if not zone_letter and northern is None:
        raise ValueError('either zone_letter or northern needs to be set')

    elif zone_letter and northern is not None:
        raise ValueError('set either zone_letter or northern, but not both')

    if strict:
        if not 100000 <= easting < 1000000:
            raise IndexError('easting out of range (must be between 100.000 m and 999.999 m)')
        if not 0 <= northing <= 10000000:
            raise IndexError('northing out of range (must be between 0 m and 10.000.000 m)')
    if not 1 <= zone_number <= 60:
        raise IndexError('zone number out of range (must be between 1 and 60)')

    if zone_letter:
        zone_letter = zone_letter.upper()

        if not 'C' <= zone_letter <= 'X' or zone_letter in ['I', 'O']:
            raise IndexError('zone letter out of range (must be between C and X)')

        northern = (zone_letter >= 'N')

    x = easting - 500000
    y = northing

    if not northern:
        y -= 10000000

    m = y / K0
    mu = m / (R * M1)

    p_rad = (mu +
             P2 * math.sin(2 * mu) +
             P3 * math.sin(4 * mu) +
             P4 * math.sin(6 * mu) +
             P5 * math.sin(8 * mu))

    p_sin = math.sin(p_rad)
    p_sin2 = p_sin * p_sin

    p_cos = math.cos(p_rad)

    p_tan = p_sin / p_cos
    p_tan2 = p_tan * p_tan
    p_tan4 = p_tan2 * p_tan2

    ep_sin = 1 - E * p_sin2
    ep_sin_sqrt = math.sqrt(1 - E * p_sin2)

    n = R / ep_sin_sqrt
    r = (1 - E) / ep_sin

    c = _E * p_cos ** 2
    c2 = c * c

    d = x / (n * K0)
    d2 = d * d
    d3 = d2 * d
    d4 = d3 * d
    d5 = d4 * d
    d6 = d5 * d

    latitude = (p_rad - (p_tan / r) *
                (d2 / 2 -
                 d4 / 24 * (5 + 3 * p_tan2 + 10 * c - 4 * c2 - 9 * E_P2)) +
                d6 / 720 * (61 + 90 * p_tan2 + 298 * c + 45 * p_tan4 - 252 * E_P2 - 3 * c2))

    longitude = (d -
                 d3 / 6 * (1 + 2 * p_tan2 + c) +
                 d5 / 120 * (5 - 2 * c + 28 * p_tan2 - 3 * c2 + 8 * E_P2 + 24 * p_tan4)) / p_cos

    return (math.degrees(latitude),
            math.degrees(longitude) + zone_number_to_central_longitude(zone_number))


def from_latlon(latitude, longitude, force_zone_number=None):
    if not -80.0 <= latitude <= 84.0:
        raise IndexError('latitude out of range (must be between 80 deg S and 84 deg N)')
    if not -180.0 <= longitude <= 180.0:
        raise IndexError('longitude out of range (must be between 180 deg W and 180 deg E)')

    lat_rad = math.radians(latitude)
    lat_sin = math.sin(lat_rad)
    lat_cos = math.cos(lat_rad)

    lat_tan = lat_sin / lat_cos
    lat_tan2 = lat_tan * lat_tan
    lat_tan4 = lat_tan2 * lat_tan2

    if force_zone_number is None:
        zone_number = latlon_to_zone_number(latitude, longitude)
    else:
        zone_number = force_zone_number

    zone_letter = latitude_to_zone_letter(latitude)

    lon_rad = math.radians(longitude)
    central_lon = zone_number_to_central_longitude(zone_number)
    central_lon_rad = math.radians(central_lon)

    n = R / math.sqrt(1 - E * lat_sin ** 2)
    c = E_P2 * lat_cos ** 2

    a = lat_cos * (lon_rad - central_lon_rad)
    a2 = a * a
    a3 = a2 * a
    a4 = a3 * a
    a5 = a4 * a
    a6 = a5 * a

    m = R * (M1 * lat_rad -
             M2 * math.sin(2 * lat_rad) +
             M3 * math.sin(4 * lat_rad) -
             M4 * math.sin(6 * lat_rad))

    easting = K0 * n * (a +
                        a3 / 6 * (1 - lat_tan2 + c) +
                        a5 / 120 * (5 - 18 * lat_tan2 + lat_tan4 + 72 * c - 58 * E_P2)) + 500000

    northing = K0 * (m + n * lat_tan * (a2 / 2 +
                                        a4 / 24 * (5 - lat_tan2 + 9 * c + 4 * c ** 2) +
                                        a6 / 720 * (61 - 58 * lat_tan2 + lat_tan4 + 600 * c - 330 * E_P2)))

    if latitude < 0:
        northing += 10000000

    return easting, northing, zone_number, zone_letter


def latitude_to_zone_letter(latitude):
    if -80 <= latitude <= 84:
        return ZONE_LETTERS[int(latitude + 80) >> 3]
    else:
        return None


def latlon_to_zone_number(latitude, longitude):
    if 56 <= latitude < 64 and 3 <= longitude < 12:
        return 32

    if 72 <= latitude <= 84 and longitude >= 0:
        if longitude <= 9:
            return 31
        elif longitude <= 21:
            return 33
        elif longitude <= 33:
            return 35
        elif longitude <= 42:
            return 37

    return int((longitude + 180) / 6) + 1


def zone_number_to_central_longitude(zone_number):
    return (zone_number - 1) * 6 - 180 + 3



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
        (x, y, _, _) = from_latlon(lat, lng)
        return x, y

    def createUTMPoint(self, lat, lng):
        x, y = self.convertLatLngToUTM(lat, lng)
        # print(x, y)
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

    def resetPastRssi(self):
        self.pastRssi = list()

# Test function to check accuracy
def getThreeBeaconsForTrilateration(discoveredBeacons):
    # Return 3 closest beacons as a list
    threeBeacons = dict()
    distances = dict()  # key is distance and value is Beacon object
    for deviceMac in discoveredBeacons:
        distances[beaconsMap[deviceMac].getDistanceToBeacon()] = beaconsMap[deviceMac]

    # Return the 3 closest beacons by sorting the key which is the distance
    # print("Three closest beacon")
    for distance in sorted(distances)[:3]:
        # distances[distance].debug()
        # print(distances[distance].deviceMac + " " + str(distance))
        threeBeacons[distances[distance].deviceMac] = distances[distance]

    return threeBeacons


def getSeconds(lastTimestamp):
    # Timestamp is of this string format "yyyy-MM-dd HH:mm:ss.SSS"
    # Returns the total seconds passed since the start of the day
    hourMinuteSecondMillisecondReference = lastTimestamp.split(" ")[1].split(":")
    totalSecondsReference = float(hourMinuteSecondMillisecondReference[2]) \
                            + float(hourMinuteSecondMillisecondReference[1]) * 60 \
                            + float(hourMinuteSecondMillisecondReference[0]) * 60 * 60
    return totalSecondsReference


def timeDifference(oldtime, newtime):
    return newtime - oldtime


def setUpCircleRadius(beacons):
    for deviceMac in beacons:
        beacons[deviceMac].circle.radius = beacons[deviceMac].getDistanceToBeacon()


def getTrilaterationResult(beacons):
    circle_list = list()
    for deviceMac in beacons.keys():
        circle_list.append(beacons[deviceMac].circle)

    inner_points = []
    for p in get_all_intersecting_points(circle_list):
        inner_points.append(p)
        # print("x: " + str(p.x) + " y:" + str(p.y))
        # Gives more 3x more weight if all of circles intersects
        if is_contained_in_circles(p, circle_list):
            inner_points.append(p)
            inner_points.append(p)
            inner_points.append(p)

    if len(inner_points) > 0:
        center = get_polygon_center(inner_points)
        (lat, lng) = to_latlon(center.x, center.y, 30, 'U')
        return lat, lng
    else:
        return "nan", "nan"



def computeResult(discoveredBeacons):
    # filter all beacons that has distance to user bigger than 20 metres because in the prototype, it is impossible
    # in AT lvl 5 and the further the distance the more unreliable
    # skip the dictionary changed size error by using a list copy of the keys
    for deviceMac in list(discoveredBeacons.keys()):
        if discoveredBeacons[deviceMac].getDistanceToBeacon() > 15:
            del discoveredBeacons[deviceMac]

    setUpCircleRadius(discoveredBeacons)

    # Treats last known position as a beacon to help in interpolating the new position
    estimatedPositionResponse = requests.get(estimatedPositionUrl, headers=myheaders)
    if (len(estimatedPositionResponse.json()) > 0):
        lastEstimatedPositionItem = estimatedPositionResponse.json()[len(estimatedPositionResponse.json()) - 1]
        pastTimestamp = lastEstimatedPositionItem["timestamp"]
        past_lat = lastEstimatedPositionItem["lat"]
        past_lon = lastEstimatedPositionItem["lon"]
        # Only uses last estimated location which were in the past 10 seconds
        # time difference is also used to estimated how far the user has gone from the past position
        # using the assumption that the user moves at 0.5 metres per second
        # This could be improved using gyroscope and accelerometer
        # This is used to make the last known position as a beacon with the distance travelled by user as a
        # clue for interpolation
        timeDif = timeDifference(getSeconds(pastTimestamp), timeReference)
        if timeDif <= 5 and timeDif >= 0:
            setUpCircleRadius(discoveredBeacons)
            discoveredBeacons["LastKnownPosition"] = Beacon("LastKnownPosition", float(past_lat), float(past_lon),
                                                            txPower=None)
            discoveredBeacons["LastKnownPosition"].circle.radius = 0.5 * timeDif
            estimated_lat, estimated_lon = getTrilaterationResult(discoveredBeacons)

            if (str(estimated_lat) != "nan" or str(estimated_lon) != "nan"):
                # Successful estimated the position
                # post estimated position to the Cloud
                requests.post(estimatedPositionUrl, data={"timestamp": lastTimestamp, "lat": repr(estimated_lat),
                                                          "lon": repr(estimated_lon)}, headers=myheaders)
                # print("successfuly interpolated last position with 2 beacons")
                print(str(estimated_lat) + "," + str(estimated_lon))
                return
            else:
                # Cannot estimate because there is no overlapping areas between the base stations
                # print("Failed to interpolate")
                del discoveredBeacons["LastKnownPosition"]

    # Whether last known position exists or not, interpolate position with discovered beacon
    estimated_lat, estimated_lon = getTrilaterationResult(discoveredBeacons)

    if (str(estimated_lat) != "nan" or str(estimated_lon) != "nan"):
        # Successful estimated the position
        # post estimated position to the Cloud
        requests.post(estimatedPositionUrl, data={"timestamp": lastTimestamp, "lat": repr(estimated_lat),
                                                      "lon": repr(estimated_lon)}, headers=myheaders)
        # print("successfuly interpolated last position with 2 beacons")
        print(str(estimated_lat) + "," + str(estimated_lon))
        return
    else:
        print("null")



if __name__ == "__main__":
    txCalibration = 10
    beaconsMap = {
        "ED23C0D875CD": Beacon("ED23C0D875CD", 55.9444578385393, -3.1866151839494705, -97.25 + txCalibration),
        "E7311A8EB6D7": Beacon("E7311A8EB6D7", 55.94444244275808, -3.18672649562358860, -95.97222222+ txCalibration + 10),
        "C7BC919B2D17": Beacon("C7BC919B2D17", 55.94452336441765, -3.1866540759801865, -66.78431373+ txCalibration),
        "EC75A5ED8851": Beacon("EC75A5ED8851", 55.94452261340533, -3.1867526471614838, -90.24 + txCalibration - 3),
        "FE12DEF2C943": Beacon("FE12DEF2C943", 55.94448393625199, -3.1868280842900276, -89.55555556+ txCalibration -5),
        "C03B5CFA00B8": Beacon("C03B5CFA00B8", 55.94449050761571, -3.1866483762860294, -53.17647059 + txCalibration),
        "E0B83A2F802A": Beacon("E0B83A2F802A", 55.94443774892113, -3.1867992505431175, -99.88888889 + txCalibration + 5),
        "F15576CB0CF8": Beacon("F15576CB0CF8", 55.944432116316044, -3.186904862523079, -96.0 + txCalibration ),
        "F17FB178EA3D": Beacon("F17FB178EA3D", 55.94444938963575, -3.1869836524128914, -88.38888889 + txCalibration),
        "FD8185988862": Beacon("FD8185988862", 55.94449107087541, -3.186941407620907, -95.02941176 + txCalibration)
    }
    discoveredBeacons = dict()  # a map of discovered Beacon objects
    timeWindow = 8  # Only take into account the RSSI of the past x seconds

    # Authorisation header for GET and POST request
    myheaders = {"Authorization": "Bearer 57:3996aa851ea17f9dd462969c686314ed878c0cf7"}
    readingsUrl = 'http://glenlivet.inf.ed.ac.uk:8080/api/v1/svc/apps/data/docs/everything'
    estimatedPositionUrl = 'http://glenlivet.inf.ed.ac.uk:8080/api/v1/svc/apps/data/docs/androidlive'

    readingsResponse = requests.get(readingsUrl, headers=myheaders)

    # ALL CONTENT OF THE PRINT STATEMENT HAVE BEEN FORMATTED IN THE FOLLOWING WAY
    # LINE 1 CONTAINS THE ESTIMATED POSITION OR ERROR MESSAGES
    # ALL OTHER LIENS CONTAINS THE BEACON'S DEVICE_MAC AND THE DISTANCE TO BEACON
    # NOTE WHEN THERE ARE NO ENOUGH BEACONS FOR TRILATERATION, THE LAST KNOWN POSITION WILL BE USED
    # TO INTERPOLATE THE NEW POSITION. IN THIS CASE THE LAST KNOWN POSITION IS TREATED AS A BEACON
    # AND ITS DISTANCE TO LAST KNOWN POSITION IS ALSO PRINTED AS A BEACON
    # THE PURPOSE OF THIS IS SO THAT IT CAN BE VISUALISED ON THE ANDROID APP
    if len(readingsResponse.json()) > 0:
        json = readingsResponse.json()
        # This is used as a reference timestamp to get all RSSI readings in the past x seconds
        i = len(json) - 1
        lastTimestamp = json[i]["timestamp"]  # Get first timestamp
        timeReference = getSeconds(lastTimestamp)
        # Start iteration from the latest item (newest beacon info)
        # Read all readings from the past timeWindow seconds and compute estimated location

        while (i >= 0):
            item = json[i]
            timestamp = item["timestamp"]
            deviceMac = item["device_mac"]
            rssi = int(item["rssi"])
            # only considers values in the past 3 seconds
            timeDif = timeDifference(getSeconds(timestamp), timeReference)

            if timeDif <= timeWindow:
                #print("i: " + str(i) + " j:" + str(j) + " threeSecondReached: " + str(timeWindowForAlgorithmReached) + " timeDif: " + str(timeDif) + " | " + timestamp + " | " + deviceMac + " | " + str(rssi))
                if not deviceMac in discoveredBeacons:
                    # convert metres to kilometres for the trilateration algorithm later
                    discoveredBeacons[deviceMac] = beaconsMap[deviceMac]
                # record seen rssi value in the past timeWindow seconds to beacons
                beaconsMap[deviceMac].pastRssi.append(rssi)
                i = i - 1
            else:
                computeResult(discoveredBeacons)
                for deviceMac in discoveredBeacons:
                    # discoveredBeacons[deviceMac].debug()
                    print(beaconsMap[deviceMac].deviceMac + "," + str(beaconsMap[deviceMac].getDistanceToBeacon()))
                break


