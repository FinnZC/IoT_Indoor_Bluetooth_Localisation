import requests
import math
import numpy as np
import json

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


###################### EXISTING SOLUTION FOR TRILATERATION ##############################
# Source from https://github.com/noomrevlis/trilateration
# http://en.wikipedia.org/wiki/Trilateration
# assuming elevation = 0
# length unit : km

earthR = 6371

class base_station(object):
    def __init__(self, lat, lon, dist):
        self.lat = lat
        self.lon = lon
        self.dist = dist

#using authalic sphere
#if using an ellipsoid this step is slightly different
#Convert geodetic Lat/Long to ECEF xyz
#   1. Convert Lat/Long to radians
#   2. Convert Lat/Long(radians) to ECEF  (Earth-Centered,Earth-Fixed)
def convert_geodetci_to_ecef(base_station):
    x = earthR *(math.cos(math.radians(base_station.lat)) * math.cos(math.radians(base_station.lon)))
    y = earthR *(math.cos(math.radians(base_station.lat)) * math.sin(math.radians(base_station.lon)))
    z = earthR *(math.sin(math.radians(base_station.lat)))
    #print(x, y, z)
    return np.array([x, y, z])

def calculate_trilateration_point_ecef(base_station_list):
    P1, P2, P3 = map(convert_geodetci_to_ecef, base_station_list)
    DistA, DistB, DistC = map(lambda x: x.dist, base_station_list)

    #vector transformation: circle 1 at origin, circle 2 on x axis
    ex = (P2 - P1)/(np.linalg.norm(P2 - P1))
    i = np.dot(ex, P3 - P1)
    ey = (P3 - P1 - i*ex)/(np.linalg.norm(P3 - P1 - i*ex))
    ez = np.cross(ex,ey)
    d = np.linalg.norm(P2 - P1)
    j = np.dot(ey, P3 - P1)

    #plug and chug using above values
    x = (pow(DistA,2) - pow(DistB,2) + pow(d,2))/(2*d)
    y = ((pow(DistA,2) - pow(DistC,2) + pow(i,2) + pow(j,2))/(2*j)) - ((i/j)*x)

    # only one case shown here
    z = np.sqrt(pow(DistA,2) - pow(x,2) - pow(y,2))

    #triPt is an array with ECEF x,y,z of trilateration point
    triPt = P1 + x*ex + y*ey + z*ez

    #convert back to lat/long from ECEF
    #convert to degrees
    lat = math.degrees(math.asin(triPt[2] / earthR))
    lon = math.degrees(math.atan2(triPt[1],triPt[0]))
    return lat, lon


######################## WRITTEN BY STUNDET FINN ZHAN CHEN ########################################

def getSecondsReference(lastTimestamp):
    # Timestamp is of this string format "yyyy-MM-dd HH:mm:ss.SSS"
    hourMinuteSecondMillisecondReference = lastTimestamp.split(" ")[1].split(":")
    totalSecondsReference = float(hourMinuteSecondMillisecondReference[2]) \
                            + float(hourMinuteSecondMillisecondReference[1]) * 60 \
                            + float(hourMinuteSecondMillisecondReference[0]) * 60 * 60
    return totalSecondsReference

class Beacon(object):
    def __init__(self, deviceMac, lat, lng, txPower):
        self.deviceMac = deviceMac
        self.lat = lat
        self.lng = lng
        self.txPower = txPower

if __name__ == "__main__":
    threeClosestBeacons= dict()

    beaconsLocation = {
        "ED23C0D875CD": (55.9444578385393, -3.1866151839494705),
        "E7311A8EB6D7": (55.94444244275808, -3.18672649562358860),
        "C7BC919B2D17": (55.94452336441765, -3.1866540759801865),
        "EC75A5AD8851": (55.94452261340533, -3.1867526471614838),
        "FE12DEF2C943": (55.94448393625199, -3.1868280842900276),
        "C03B5CFA00B8": (55.94449050761571, -3.1866483762860294),
        "E0B83A2F802A": (55.94443774892113, -3.1867992505431175),
        "F15576CB0CF8": (55.944432116316044, -3.186904862523079),
        "F17FB178EA3D": (55.94444938963575, -3.1869836524128914),
        "FD8185988862": (55.94449107087541, -3.186941407620907)
    }

    # Tx is the strength of the transmission signal measured at a distance of one meter from the transmitter.
    # The following tx power has been calculated by collecting more than 30 rssi of the beacon
    # around 1 metres from the beacon, outliers have been removed and the mean is calculated
    # data collected are saved on an excel file and input to this algorithm
    # https://www.kdnuggets.com/2017/02/removing-outliers-standard-deviation-python.html

    beaconsTxPower = {
        "ED23C0D875CD": 97.25,
        "E7311A8EB6D7": 95.97222222,
        "C7BC919B2D17": 66.78431373,
        "EC75A5AD8851": 90.24,
        "FE12DEF2C943": 89.55555556,
        "C03B5CFA00B8": 53.17647059,
        "E0B83A2F802A": 99.88888889,
        "F15576CB0CF8": 96.0,
        "F17FB178EA3D": 88.38888889,
        "FD8185988862": 95.02941176
    }

    # Calibration required, I found this via eye inspection via my custom Android Google Maps app
    latLngCalibration = (-0.000025, -0.0000025)

    # Authorisation header for GET and POST request
    myheaders = {"Authorization":"Bearer 57:3996aa851ea17f9dd462969c686314ed878c0cf7"}

    url = 'http://glenlivet.inf.ed.ac.uk:8080/api/v1/svc/apps/data/docs/everything'
    endpoint = "http://glenlivet.inf.ed.ac.uk:8080/api/v1/svc/ep/get"


    r = requests.get(url, headers=myheaders)
    #print(r.text)
    #print(r.json())

    # Reverse the json file and read the first 20 key value pairs of the reversed
    # list to get the latest discovery of beacons
    if len(r.json()) > 0:
        lastTimestamp = r.json()[len(r.json())-1]["timestamp"] # Get last timestamp
        # Timestamp is of this format "yyyy-MM-dd HH:mm:ss.SSS"
        timeReference = getSecondsReference(lastTimestamp)

        for item in r.json()[::-1]:
            try:
                timestamp = item["timestamp"]
                device_mac =  item["device_mac"]
                rssi = int(item["rssi"])
                # only considers values in the past 3 seconds
                if (abs(timeReference - getSecondsReference(timestamp)) <= 3):
                    #print(timestamp + " | " + device_mac + " | " + str(rssi))
                    if not device_mac in threeClosestBeacons:
                        # convert metres to kilometres for the trilateration algorithm later
                        threeClosestBeacons[device_mac] = getDistanceFromRSSI(rssi=rssi, txPower=beaconsTxPower.get(device_mac))/1000
                        #print(getDistanceFromRSSI(rssi=rssi, txPower=-65)/1000)
                        if len(threeClosestBeacons) == 3:
                            break
                else:
                    break
            except:
                #print("Not in format")
                pass

    if len(threeClosestBeacons) == 3:
        #print(threeClosestBeacons)
        base_station_list = list()
        # distance in km
        for device_mac in threeClosestBeacons:
            # beaconsLocation[device_mac][0] is latitude of the beacon
            # beaconsLocation[device_mac][1] is longitude of the beacon
            base_station_list.append(
                base_station(beaconsLocation[device_mac][0],
                             beaconsLocation[device_mac][1],
                             threeClosestBeacons.get(device_mac)))

        estimated_lat, estimated_lon = calculate_trilateration_point_ecef(base_station_list)

        if (repr(estimated_lat) == "nan" and repr(estimated_lon) == "nan"):
            # Cannot estimate because there is no overlapping areas between the base stations
            print("null")
        else:
            # Successful estimated the position
            print(repr(estimated_lat+latLngCalibration[0]) + "," + repr(estimated_lon+latLngCalibration[1]))
    else:
        # There are no 3 beacons so cannot estimate
        print("No 3 beacons")

    for device_mac in threeClosestBeacons:
        print(device_mac + "," + str(threeClosestBeacons.get(device_mac)*1000)) # convert km back to metres

