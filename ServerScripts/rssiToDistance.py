import math

def getDistance(rssi, txPower): # in metres
    #tx values usually ranges from -59 to -65
    if rssi == 0:
        return -1

    ratio = rssi*1.0/txPower;
    if ratio < 1.0:
        return math.pow(ratio, 10)
    else:
        accuracy = (0.89976) * math.pow(ratio, 7.7095) + 0.111
        return accuracy

def getDistancev2(rssi, txPower):
    """"
     * RSSI = TxPower - 10 * n * lg(d)
     * n = 2 (in free space)
     *
     * d = 10 ^ ((TxPower - RSSI) / (10 * n))
     */
    """
    #print("RSSI: " + str(rssi) + " txPower:" + str(txPower))
    return math.pow(10, (txPower - rssi) / (10 * 2))



print("%.2f" % getDistance(-85, -65.5))
print("%.2f" % getDistancev2(-85, -65.5))