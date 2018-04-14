package com.finnzhanchen.iotsmartshoppingapp;

import com.google.android.gms.maps.model.Circle;
import com.google.android.gms.maps.model.LatLng;
import com.google.android.gms.maps.model.Marker;

/**
 * Created by Finn Zhan Chen on 14/04/2018.
 */

public class Beacon {
    public final String deviceMac;
    public final LatLng position;
    // Circle represents distance derived from RSSI signals
    // this map keeps track of the reference so the circles on map can be
    // removed and updated when new data is received from the cloud server
    public Circle circle;
    public Marker marker;

    public Beacon(String deviceMac, LatLng position){
        this.deviceMac = deviceMac;
        this.position = position;
    }
}
