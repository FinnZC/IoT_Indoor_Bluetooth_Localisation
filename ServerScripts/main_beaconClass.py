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
        self.txPower = txPower
        self.pastRssi = list()

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
            final_list = [x for x in self.pastRssi if (x > mean - 2 * sd)]
            final_list = [x for x in final_list if (x < mean + 2 * sd)]
            return np.mean(final_list)

def getThreeBeaconsForTrilateration(discoveredBeacons):
    # Return 3 closest beacons
    threeBeacons = list()
    distances = dict() # key is distance and value is Beacon object
    for beacon in discoveredBeacons:
        distances[beacon.getDistanceToBeacon()] = beacon

    # Return the 3 closest beacons
    for distance in sorted(distances)[:3]:
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
    return timeReference - time <= 3

if __name__ == "__main__":
    beaconsMap = {
        "ED23C0D875CD": Beacon("ED23C0D875CD", 55.9444578385393, -3.1866151839494705, 97.25),
        "E7311A8EB6D7": Beacon("E7311A8EB6D7", 55.94444244275808, -3.18672649562358860, 95.97222222),
        "C7BC919B2D17": Beacon("C7BC919B2D17", 55.94452336441765, -3.1866540759801865, 66.78431373),
        "EC75A5AD8851": Beacon("EC75A5AD8851", 55.94452261340533, -3.1867526471614838, 90.24),
        "FE12DEF2C943": Beacon("FE12DEF2C943", 55.94448393625199, -3.1868280842900276, 89.55555556),
        "C03B5CFA00B8": Beacon("C03B5CFA00B8", 55.94449050761571, -3.1866483762860294, 53.17647059),
        "E0B83A2F802A": Beacon("E0B83A2F802A", 55.94443774892113, -3.1867992505431175, 99.88888889),
        "F15576CB0CF8": Beacon("F15576CB0CF8", 55.944432116316044, -3.186904862523079, 96.0),
        "F17FB178EA3D": Beacon("F17FB178EA3D", 55.94444938963575, -3.1869836524128914, 88.38888889),
        "FD8185988862": Beacon("FD8185988862", 55.94449107087541, -3.186941407620907, 95.02941176)
    }
    # a list of discovered Beacon objects
    discoveredBeacons = list()
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
    # LINE 1 CONTAINS THE ESTIMATED POSITION
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
                device_mac =  item["device_mac"]
                rssi = int(item["rssi"])
                # only considers values in the past 3 seconds
                if timeDifference(timeReference, getSeconds(timestamp)) <= 3:
                    #print(timestamp + " | " + device_mac + " | " + str(rssi))
                    if not device_mac in discoveredBeacons:
                        # convert metres to kilometres for the trilateration algorithm later
                        discoveredBeacons.append(beaconsMap[device_mac])

                    # record seen rssi value in the past 3 seconds to beacons
                    beaconsMap[device_mac].pastRssi.append(rssi)
                else:
                    break
            except:
                #print("Not in format")
                pass

    # Base stations for trilateration
    baseStationsForTrilateration = list()
    if len(discoveredBeacons) >= 3:
        threeBeaconsForTrilateration = getThreeBeaconsForTrilateration(discoveredBeacons)

        # distance in km
        for beacon in threeBeaconsForTrilateration:
            baseStationsForTrilateration.append(
                base_station(beacon.lat, beacon.lng, beacon.getDistanceToBeacon()))

        estimated_lat, estimated_lon = calculate_trilateration_point_ecef(baseStationsForTrilateration)

        if (repr(estimated_lat) == "nan" and repr(estimated_lon) == "nan"):
            # Cannot estimate because there is no overlapping areas between the base stations
            print("null")
        else:
            # Successful estimated the position
            # post estimated position to the Cloud
            requests.post(estimatedPositionUrl, data={"timestamp": lastTimestamp,
                                                        "lat": repr(estimated_lat),
                                                        "lon": repr(estimated_lon)
                                                        }, headers = myheaders)

            print(repr(estimated_lat)  + "," + repr(estimated_lon)) # might need to calibrate the algorithm response
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
            if timeDif <= 5:
                for beacon in discoveredBeacons:
                    baseStationsForTrilateration.append(beacon)
                baseStationsForTrilateration.append(base_station(past_lat, past_lon, (1*timeDif)/1000))

                estimated_lat, estimated_lon = calculate_trilateration_point_ecef(baseStationsForTrilateration)

                if (repr(estimated_lat) == "nan" and repr(estimated_lon) == "nan"):
                    # Cannot estimate because there is no overlapping areas between the base stations
                    print("null")
                else:
                    # Successful estimated the position
                    # post estimated position to the Cloud
                    requests.post(estimatedPositionUrl, data={"timestamp": lastTimestamp,
                                                              "lat": repr(estimated_lat),
                                                              "lon": repr(estimated_lon)
                                                              }, headers=myheaders)

                    print(repr(estimated_lat) + "," + repr(estimated_lon))  # might need to calibrate the algorithm response

                # print the distance and
                print("LastKnownPosition," + str(1*timeDif))

        except:
            print("Failed to interpolate")

    else:
        # There are no 3 beacons so cannot estimate
        print("Not enough beacons")

    for beacon in discoveredBeacons:
        print(beacon.deviceMac + "," + str(beacon.getDistanceToBeacon()*1000)) # convert km back to metres
