package com.finnzhanchen.iotsmartshoppingapp;

import android.graphics.Color;
import android.nfc.Tag;
import android.os.Handler;
import android.support.v4.app.FragmentActivity;
import android.os.Bundle;
import android.util.Log;

import com.android.volley.AuthFailureError;
import com.android.volley.Cache;
import com.android.volley.DefaultRetryPolicy;
import com.android.volley.Network;
import com.android.volley.Request;
import com.android.volley.RequestQueue;
import com.android.volley.Response;
import com.android.volley.VolleyError;
import com.android.volley.toolbox.BasicNetwork;
import com.android.volley.toolbox.DiskBasedCache;
import com.android.volley.toolbox.HurlStack;
import com.android.volley.toolbox.StringRequest;
import com.google.android.gms.maps.CameraUpdate;
import com.google.android.gms.maps.CameraUpdateFactory;
import com.google.android.gms.maps.GoogleMap;
import com.google.android.gms.maps.OnMapReadyCallback;
import com.google.android.gms.maps.SupportMapFragment;
import com.google.android.gms.maps.model.BitmapDescriptorFactory;
import com.google.android.gms.maps.model.Circle;
import com.google.android.gms.maps.model.CircleOptions;
import com.google.android.gms.maps.model.GroundOverlayOptions;
import com.google.android.gms.maps.model.LatLng;
import com.google.android.gms.maps.model.LatLngBounds;
import com.google.android.gms.maps.model.Marker;
import com.google.android.gms.maps.model.MarkerOptions;

import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.Map;

public class Activity_1_Maps extends FragmentActivity implements OnMapReadyCallback {

    private GoogleMap mMap;
    private final String AUTHORISATION_BEARER = "Bearer 57:3996aa851ea17f9dd462969c686314ed878c0cf7";
    private final String coordinateEndPointURL = "http://glenlivet.inf.ed.ac.uk:8080/api/v1/svc/ep/test_coordinate_endpoint";
    LatLng startPosition = new LatLng(55.944433, -3.186908);
    private LatLng currentPosition = new LatLng(55.944398, -3.186355);
    private Circle currentPositionCircle;
    private RequestQueue queue;
    // Initialise beacons on a map
    private static final HashMap<String, LatLng> beaconsMap;
    static {
        beaconsMap = new HashMap<>();
        beaconsMap.put("ed23c0d875cd", new LatLng(55.9444578385393,-3.1866151839494705));
        beaconsMap.put("e7311a8eb6d7", new LatLng(55.94444244275808,-3.18672649562358860));
        beaconsMap.put("c7bc919b2d17", new LatLng(55.94452336441765,-3.1866540759801865));
        beaconsMap.put("ec75a5ed8851", new LatLng(55.94452261340533,-3.1867526471614838));
        beaconsMap.put("fe12def2c943", new LatLng(55.94448393625199,-3.1868280842900276));
        beaconsMap.put("c03b5cfa00b8", new LatLng(55.94449050761571,-3.1866483762860294));
        beaconsMap.put("e0b83a2f802a", new LatLng(55.94443774892113,-3.1867992505431175));
        beaconsMap.put("f15576cb0cf8", new LatLng(55.944432116316044,-3.186904862523079));
        beaconsMap.put("f17fb178ea3d", new LatLng(55.94444938963575,-3.1869836524128914));
        beaconsMap.put("fd8185988862", new LatLng(55.94449107087541,-3.186941407620907));
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_1__maps);
        // Obtain the SupportMapFragment and get notified when the map is ready to be used.
        SupportMapFragment mapFragment = (SupportMapFragment) getSupportFragmentManager()
                .findFragmentById(R.id.map);
        mapFragment.getMapAsync(this);
        // For testing purposes
        testDistanceBetweenPoints();
    }

    public void onMapReady(GoogleMap googleMap) {
        mMap = googleMap;
        initialiseMap();
        // Initialise requestQueue for GET and POST
        // Instantiate the cache
        Cache cache = new DiskBasedCache(getCacheDir(), 1024 * 1024); // 1MB cap
        // Set up the network to use HttpURLConnection as the HTTP client.
        Network network = new BasicNetwork(new HurlStack());
        // Instantiate the RequestQueue with the cache and network.
        queue = new RequestQueue(cache, network);
        // When a request finishes, it updates the current location
        queue.addRequestFinishedListener(new RequestQueue.RequestFinishedListener<StringRequest>() {
            @Override
            public void onRequestFinished(Request<StringRequest> request) {
                updateCurrentLocation();
            }
        });
        queue.start();
        updateCurrentLocation();
    }

    public void initialiseMap(){
        setUpUI();
        // Initialise start position circle
        currentPositionCircle = mMap.addCircle(new CircleOptions()
                .center(currentPosition)
                .radius(0.5) // radius of 5 metres
                .strokeColor(Color.parseColor("#3170d6"))
                .fillColor(0x993170d6));
        currentPositionCircle.setZIndex(2);
        // Move camera to startPosition which is Appleton Tower
        CameraUpdate startLocationCameraUpdate = CameraUpdateFactory.newLatLngZoom(startPosition, 50);
        mMap.animateCamera(startLocationCameraUpdate);
        // Add floor map to the Google Map
        LatLngBounds atLvl5Bounds = new LatLngBounds(
                new LatLng(55.94426201125635, -3.1871650367975235),       // South west corner
                new LatLng(55.944596588047396, -3.186331540346145));      // North east corner
        GroundOverlayOptions atLvl5Map = new GroundOverlayOptions()
                .image(BitmapDescriptorFactory.fromResource(R.drawable.at_floor5_v4))
                .positionFromBounds(atLvl5Bounds);
        mMap.addGroundOverlay(atLvl5Map);
        // Plot Beacons on map
        plotBeaconsOnMap();
        // Plot Circles on map
        plotCirclesOnMap();
        // Update current location every 3 second
        final Handler handler = new Handler();
        final int delay = 3000; //milliseconds

        handler.postDelayed(new Runnable(){
            public void run(){
                // Update current location with a new circle
                updateCurrentLocation();
                handler.postDelayed(this, delay);
            }
        }, delay);

    }

    public void setUpUI(){
        // For testing purpose
        try {
            // Visualise current position with a small blue captureCircle
            mMap.setMyLocationEnabled(true);


        } catch (SecurityException se) {
            System.out.println("Security exception thrown [onMapReady]");
        }
        // Add "My location" and "Zoom" button to the user interface
        mMap.getUiSettings().setMyLocationButtonEnabled(true);
        mMap.getUiSettings().setZoomControlsEnabled(true);
    }

    public void plotBeaconsOnMap(){
        for(String macAddress : beaconsMap.keySet()){
            mMap.addMarker(new MarkerOptions()
                    .position(beaconsMap.get(macAddress))
                    .anchor(0.5f, 0.5f)
                    .title(macAddress)
                    .icon(BitmapDescriptorFactory.fromResource(R.drawable.bluetooth_beacons)));
        }
    }

    public void plotCirclesOnMap(){
        for(String macAddress : beaconsMap.keySet()){
            mMap.addCircle(new CircleOptions()
                    .center(beaconsMap.get(macAddress))
                    .radius(2) // radius of 5 metres
                    .strokeColor(Color.parseColor("#3170d6"))
                    .fillColor(0x552cdae0)).setZIndex(2);
        }
    }

    public void updateCurrentLocation(){
        //Log.e("updateCurrentLocation", getRequest(queue, coordinateEndPointURL));
        getRequest(queue, coordinateEndPointURL);

        currentPositionCircle.remove();
        currentPositionCircle = mMap.addCircle(new CircleOptions()
                .center(currentPosition)
                .radius(0.5) // radius of 5 metres
                .strokeColor(Color.parseColor("#3170d6"))
                .fillColor(0x993170d6));
        currentPositionCircle.setZIndex(2);
    }

    private void getRequest(RequestQueue queue, String url) {
        StringRequest stringRequest = new StringRequest(Request.Method.GET, url,
                new Response.Listener<String>() {
                    @Override
                    public void onResponse(String response) {
                        if (!response.equals(null)) {
                            // Display the first 500 characters of the response string.
                            String[] position = response.split(",");
                            currentPosition = new LatLng(Float.parseFloat(position[0]), Float.parseFloat(position[1]));
                            Log.e("getRequest", "Response is: " + response);
                        } else {
                            Log.e("getRequest", "Your Array Response Data Null");
                        }
                    }
                }, new Response.ErrorListener() {
            @Override
            public void onErrorResponse(VolleyError error) {
                Log.e("getRequest ", "" + error);
            }
        }) {
            // Authorisation
            @Override
            public Map<String, String> getHeaders() throws AuthFailureError {
                Map<String, String> params = new HashMap<>();
                params.put("Authorization", AUTHORISATION_BEARER);
                return params;
            }
        };

        stringRequest.setRetryPolicy(new DefaultRetryPolicy(
                10000,
                DefaultRetryPolicy.DEFAULT_MAX_RETRIES,
                DefaultRetryPolicy.DEFAULT_BACKOFF_MULT));
        queue.add(stringRequest);
    }

    private void postRequest(RequestQueue queue, String url, final String timestamp, final String deviceMac, final String rssi) {
        StringRequest stringRequest = new StringRequest(Request.Method.POST, url,
                new Response.Listener<String>() {
                    @Override
                    public void onResponse(String response) {
                        if (!response.equals(null)) {
                            Log.e("postRequest", "Post Successful");
                        } else {
                            Log.e("postRequest", "Your Array Response Data Null");
                        }
                    }

                }, new Response.ErrorListener() {
            @Override
            public void onErrorResponse(VolleyError error) {
                Log.e("postRequest ", "" + error);
            }
        }) {
            // Authorisation
            @Override
            public Map<String, String> getHeaders() throws AuthFailureError {
                Map<String, String> params = new HashMap<>();
                params.put("Authorization", AUTHORISATION_BEARER);
                return params;
            }
            //Pass Your Parameters here
            @Override
            protected Map<String, String> getParams() {
                Map<String, String> params = new LinkedHashMap<String, String>();
                params.put("timestamp", timestamp);
                params.put("device_mac", deviceMac);
                params.put("rssi", rssi);
                return params;
            }

        };
        stringRequest.setRetryPolicy(new DefaultRetryPolicy(
                5,
                DefaultRetryPolicy.DEFAULT_MAX_RETRIES,
                DefaultRetryPolicy.DEFAULT_BACKOFF_MULT));
        // Add the request to the RequestQueue.
        queue.add(stringRequest);
    }

    public double distanceBetweenTwoLatLng(LatLng p1, LatLng p2){
        final double R = 6381 * 1000; // Earth radius in metres
        double lat1 = p1.latitude;
        double lon1 = p1.longitude;
        double lat2 = p2.latitude;
        double lon2 = p2.longitude;

        double latDistance = Math.toRadians(lat2 - lat1);
        double lonDistance = Math.toRadians(lon2 - lon1);
        double a = Math.sin(latDistance / 2) * Math.sin(latDistance / 2)
                + Math.cos(Math.toRadians(lat1)) * Math.cos(Math.toRadians(lat2))
                * Math.sin(lonDistance / 2) * Math.sin(lonDistance / 2);
        double c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
        double distance = R * c;
        return distance;
    }

    public void testDistanceBetweenPoints(){
        for(String macAddress : beaconsMap.keySet()){
            for(String macAddress2 : beaconsMap.keySet()){
                double distance = distanceBetweenTwoLatLng(beaconsMap.get(macAddress), beaconsMap.get(macAddress2));
                Log.e("testDistanceBetweenPont", macAddress + " to " + macAddress2 + " is " + Double.toString(distance) + " metres");
            }
        }
    }
}
