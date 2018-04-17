import requests
import math
import numpy as np
import json

# EXTERNAL SOURCES HAVE BEEN CITED APPROPIATELY AND LOOK AT MAIN FUNCTION FOR STUDENT'S WORK (FINN ZHAN CHEN)

##################### EXISING SOLUTION FOR CALCULATING DISTANCE FROM RSSI ################
# Source from http://developer.radiusnetworks.com/2014/12/04/fundamentals-of-beacon-ranging.html

def getDistanceFromRSSI(rssi, txPower): # in metres
    #tx values usually ranges from -59 to -65
    #print("RSSI: " + str(rssi) + " txPower:" + str(txPower))
    return math.pow(10, (txPower - rssi) / (10 * 2))


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
if __name__ == "__main__":
    threeClosestBeacons= dict()

    beaconsLocation = {
        "ED23C0D875CD": (55.9444578385393, -3.1866151839494705),
        "E7311A8EB6D7": (55.94444244275808, -3.18672649562358860),
        "C7BC919B2D17": (55.94452336441765, -3.1866540759801865),
        "EC75A5ED8851": (55.94452261340533, -3.1867526471614838),
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
        "ED23C0D875CD": -97.25 + 5,
        "E7311A8EB6D7": -95.97222222 + 5,
        "C7BC919B2D17": -66.78431373 + 9, # right
        "EC75A5ED8851": -90.24 + 5, # right
        "FE12DEF2C943": -89.55555556 + 6, # right
        "C03B5CFA00B8": -53.17647059 + 5,
        "E0B83A2F802A": -99.88888889 + 5,
        "F15576CB0CF8": -96.0 + 5,
        "F17FB178EA3D": -88.38888889 + 5,
        "FD8185988862": -95.02941176 + 10 # right
    }
    # Calibration required, I found this via eye inspection via my custom Android Google Maps app
    latLngCalibration = (0.00002, 0.0000025)
    oldlatLngCalibration = (0.000025, 0.0000025)
     # Imagine at F155
    a = "F15576CB0CF8"
    rssi_a = -96
    b = "F17FB178EA3D"
    rssi_b = -96
    c = "FD8185988862"
    rssi_c = -100

    """
    # Imagine at EC75
    a = "EC75A5ED8851"
    rssi_a = -90.24
    b = "FE12DEF2C943"
    rssi_b = -100
    c = "C7BC919B2D17"
    rssi_c = -73
    """
    baseA = base_station(beaconsLocation[a][0], beaconsLocation[a][1], getDistanceFromRSSI(rssi=rssi_a, txPower=beaconsTxPower[a])/1000) #in km
    print(a+ " " + str(getDistanceFromRSSI(rssi=rssi_a, txPower=beaconsTxPower[a])))
    baseB = base_station(beaconsLocation[b][0], beaconsLocation[b][1],  getDistanceFromRSSI(rssi=rssi_b, txPower=beaconsTxPower[b])/1000) #c0
    print(b + " " + str(getDistanceFromRSSI(rssi=rssi_b, txPower=beaconsTxPower[b])))
    baseC = base_station(beaconsLocation[c][0], beaconsLocation[c][1], getDistanceFromRSSI(rssi=rssi_c, txPower=beaconsTxPower[c])/1000) #c0
    print(c + " " + str(getDistanceFromRSSI(rssi=rssi_c, txPower=beaconsTxPower[c])))

    base_station_list = [baseA, baseB, baseC]
    lat, lon = calculate_trilateration_point_ecef(base_station_list)
    print(repr(lat) + ", " +repr(lon))
    print(repr(lat+latLngCalibration[0])  + ", " + repr(lon+latLngCalibration[1]))