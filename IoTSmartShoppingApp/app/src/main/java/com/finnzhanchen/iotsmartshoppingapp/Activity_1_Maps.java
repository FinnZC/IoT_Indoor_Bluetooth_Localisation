package com.finnzhanchen.iotsmartshoppingapp;

import android.Manifest;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.location.Location;
import android.support.v4.app.ActivityCompat;
import android.os.Bundle;
import android.support.v4.content.ContextCompat;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;
import android.widget.Toast;

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
import com.google.android.gms.common.ConnectionResult;
import com.google.android.gms.common.api.GoogleApiClient;
import com.google.android.gms.location.LocationListener;
import com.google.android.gms.location.LocationRequest;
import com.google.android.gms.location.LocationServices;
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
// AUTHOR: FINN ZHAN CHEN
// EXTERNAL SOURCES HAVE BEEN CITED APPROPIATELY
public class Activity_1_Maps extends AppCompatActivity
        implements OnMapReadyCallback,
        GoogleApiClient.ConnectionCallbacks,
        GoogleApiClient.OnConnectionFailedListener,
        LocationListener {

    private GoogleMap mMap;
    private GoogleApiClient mGoogleApiClient;
    private final String AUTHORISATION_BEARER = "Bearer 57:3996aa851ea17f9dd462969c686314ed878c0cf7";
    private final String coordinateEndPointURL = "http://glenlivet.inf.ed.ac.uk:8080/api/v1/svc/ep/main";
    private LatLng startPosition = new LatLng(55.94448393625199,-3.1868280842900276);
    private LatLng estimatedCurrentLocation = new LatLng(0, 0);
    private Circle estimatedCurrentLocationCircle;
    private RequestQueue queue;

    // Initialise beacons on a map
    private static final HashMap<String, Beacon> beaconsMap;
    static {
        beaconsMap = new HashMap<>();
        // Last Known Position is acting as a beacon if there are not enough beacons to trilaterate
        // the position, so if there are 2 beacons nearby then the last known position will be used
        // to interpolate the new estimated position, this Beacon object is used to visualise the interpolation on the map
        beaconsMap.put("LastKnownPosition", new Beacon("LastKnownPosition", new LatLng(0,0)));
        beaconsMap.put("ED23C0D875CD", new Beacon("ED23C0D875CD", new LatLng(55.9444578385393,-3.1866151839494705)));
        beaconsMap.put("E7311A8EB6D7", new Beacon("E7311A8EB6D7", new LatLng(55.94444244275808,-3.18672649562358860)));
        beaconsMap.put("C7BC919B2D17", new Beacon("C7BC919B2D17", new LatLng(55.94452336441765,-3.1866540759801865)));
        beaconsMap.put("EC75A5ED8851", new Beacon("EC75A5ED8851", new LatLng(55.94452261340533,-3.1867526471614838)));
        beaconsMap.put("FE12DEF2C943", new Beacon("FE12DEF2C943", new LatLng(55.94448393625199,-3.1868280842900276)));
        beaconsMap.put("C03B5CFA00B8", new Beacon("C03B5CFA00B8", new LatLng(55.94449050761571,-3.1866483762860294)));
        beaconsMap.put("E0B83A2F802A", new Beacon("E0B83A2F802A", new LatLng(55.94443774892113,-3.1867992505431175)));
        beaconsMap.put("F15576CB0CF8", new Beacon("F15576CB0CF8", new LatLng(55.944432116316044,-3.186904862523079)));
        beaconsMap.put("F17FB178EA3D", new Beacon("F17FB178EA3D", new LatLng(55.94444938963575,-3.1869836524128914)));
        beaconsMap.put("FD8185988862", new Beacon("FD8185988862", new LatLng(55.94449107087541,-3.186941407620907)));
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_1__maps);
        // Obtain the SupportMapFragment and get notified when the map is ready to be used.
        SupportMapFragment mapFragment = (SupportMapFragment) getSupportFragmentManager()
                .findFragmentById(R.id.map);
        mapFragment.getMapAsync(this);
        // Create an instance of GoogleAPIClient.
        if (mGoogleApiClient == null) {
            mGoogleApiClient = new GoogleApiClient.Builder(this)
                    .addConnectionCallbacks(this)
                    .addOnConnectionFailedListener(this)
                    .addApi(LocationServices.API)
                    .build();
        }
        // For testing purposes
        testDistanceBetweenPoints();
    }

    public void onMapReady(GoogleMap googleMap) {
        mMap = googleMap;

    }

    protected void onStart(){
        super.onStart();
        mGoogleApiClient.connect();
    }

    @Override
    protected void onStop(){
        super.onStop();
        if(mGoogleApiClient.isConnected()){
            mGoogleApiClient.disconnect();
        }
    }

    protected void createLocationRequest() {
        // Set the parameters for the location request
        LocationRequest mLocationRequest = new LocationRequest();
        mLocationRequest.setInterval(5000); // preferably every 5 seconds
        mLocationRequest.setFastestInterval(1000); // at most every second
        mLocationRequest.setPriority(LocationRequest.PRIORITY_HIGH_ACCURACY);
        // Can we access the user’s current location?
        int permissionCheck = ContextCompat.checkSelfPermission(this, Manifest.permission.ACCESS_FINE_LOCATION);
        if (permissionCheck == PackageManager.PERMISSION_GRANTED) {
            LocationServices.FusedLocationApi.requestLocationUpdates( mGoogleApiClient, mLocationRequest, this);
        }
    }

    @Override
    public void onConnected(Bundle connectionHint) {
        try { createLocationRequest(); }
        catch (java.lang.IllegalStateException ise) {
            System.out.println("IllegalStateException thrown [onConnected]");
        }
        setUp();
    }

    @Override
    public void onLocationChanged(Location current) {
        System.out.println("[onLocationChanged] Lat/long now ("
                + String.valueOf(current.getLatitude())
                + ","
                + String.valueOf(current.getLongitude()));
    }

    @Override
    public void onConnectionSuspended(int flag) {
        System.out.println(" >>>> onConnectionSuspended");
    }

    @Override
    public void onConnectionFailed(ConnectionResult result) {
        // An unresolvable error has occurred and a connection to Google APIs
        // could not be established. Display an error message, or handle
        // the failure silently
        System.out.println(" >>>> onConnectionFailed");
    }

    public void setUp(){
        // Initialise requestQueue for GET and POST
        // Instantiate the cache
        Cache cache = new DiskBasedCache(getCacheDir(), 1024 * 1024); // 1MB cap
        // Set up the network to use HttpURLConnection as the HTTP client.
        Network network = new BasicNetwork(new HurlStack());
        // Instantiate the RequestQueue with the cache and network.
        queue = new RequestQueue(cache, network);
        // When a request finishes, it calls updateEstimatedCurrentLocation() repeatedly
        queue.addRequestFinishedListener(new RequestQueue.RequestFinishedListener<StringRequest>() {
            @Override
            public void onRequestFinished(Request<StringRequest> request) {
                updateEstimatedCurrentLocation();
            }
        });
        queue.start();
        initialiseMap();
    }

    public void initialiseMap(){
        // Enable current locations from Wifi and GPS so that I can compare the difference
        // between bluetooth estimated and Wifi & GPS estimated locations
        setUpGoogleMaps();
        // Initialise start position circle
        estimatedCurrentLocationCircle = mMap.addCircle(new CircleOptions()
                .center(estimatedCurrentLocation)
                .radius(0.5) // radius of 5 metres
                .strokeColor(Color.parseColor("#ff0000"))
                .fillColor(0x99ff0000));
        estimatedCurrentLocationCircle.setZIndex(2);
        // Move camera to startPosition which is Appleton Tower
        CameraUpdate startLocationCameraUpdate = CameraUpdateFactory.newLatLngZoom(startPosition, 20);
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
        initialiseCirclesOnMap();
        // Update current location every 3 second
        updateEstimatedCurrentLocation();
    }

    public void setUpGoogleMaps(){
        // Can we access the user’s current location?
        if (ContextCompat.checkSelfPermission(this,
                Manifest.permission.ACCESS_FINE_LOCATION) ==
                PackageManager.PERMISSION_GRANTED) {
            mMap.setMyLocationEnabled(true);
        } else {
            ActivityCompat.requestPermissions(this,
                    new String[]{android.Manifest.permission.ACCESS_FINE_LOCATION},
                    1);
        }
        // Add "My location" and "Zoom" button to the user interface
        mMap.getUiSettings().setMyLocationButtonEnabled(true);
        mMap.getUiSettings().setZoomControlsEnabled(true);
    }

    public void plotBeaconsOnMap(){
        for(String macAddress : beaconsMap.keySet()){
            // Save the reference of the marker on the Beacon object
            beaconsMap.get(macAddress).marker = mMap.addMarker(new MarkerOptions()
                    .position(beaconsMap.get(macAddress).position)
                    .anchor(0.5f, 0.5f)
                    .title(macAddress)
                    .icon(BitmapDescriptorFactory.fromResource(R.drawable.bluetooth_beacons)));
        }
    }

    public void initialiseCirclesOnMap(){
        // Test only
        for(String macAddress : beaconsMap.keySet()){
            // Save the reference of the circle on Beacon object
            beaconsMap.get(macAddress).circle = mMap.addCircle(new CircleOptions()
                    .center(beaconsMap.get(macAddress).position)
                    .radius(0.1) // radius of 5 metres
                    .strokeColor(Color.parseColor("#3170d6"))
                    .fillColor(0x302cdae0));
            // Set Z index so that it appears above the overlayed image of the floor map
            beaconsMap.get(macAddress).circle.setZIndex(2);
        }
/*
        /////// TEST ONLY REMOVE AFTER FINISH
        Circle circle = mMap.addCircle(new CircleOptions()
                .center(beaconsMap.get("F15576CB0CF8").position)
                .radius(1.7782794100389228) // radius of 5 metres
                .strokeColor(Color.parseColor("#3170d6"))
                .fillColor(0x302cdae0));
        circle.setZIndex(2);
        mMap.addCircle(new CircleOptions()
                .center(beaconsMap.get("F17FB178EA3D").position)
                .radius(4.27) // radius of 5 metres
                .strokeColor(Color.parseColor("#3170d6"))
                .fillColor(0x302cdae0)).setZIndex(2);
        mMap.addCircle(new CircleOptions()
                .center(beaconsMap.get("FD8185988862").position)
                .radius(5.60) // radius of 5 metres
                .strokeColor(Color.parseColor("#3170d6"))
                .fillColor(0x302cdae0)).setZIndex(2);
        mMap.addCircle(new CircleOptions()
                .center(beaconsMap.get("C03B5CFA00B8").position)
                .radius(20) // radius of 5 metres
                .strokeColor(Color.parseColor("#3170d6"))
                .fillColor(0x302cdae0)).setZIndex(2);
*/
        /*
        Imagine at EC 75
        Circle circle = mMap.addCircle(new CircleOptions()
                .center(beaconsMap.get("FE12DEF2C943").position)
                .radius(6.64) // radius of 5 metres
                .strokeColor(Color.parseColor("#3170d6"))
                .fillColor(0x302cdae0));
        circle.setZIndex(2);
        mMap.addCircle(new CircleOptions()
                .center(beaconsMap.get("C7BC919B2D17").position)
                .radius(5.76) // radius of 5 metres
                .strokeColor(Color.parseColor("#3170d6"))
                .fillColor(0x302cdae0)).setZIndex(2);
        mMap.addCircle(new CircleOptions()
                .center(beaconsMap.get("EC75A5ED8851").position)
                .radius(1.8) // radius of 5 metres
                .strokeColor(Color.parseColor("#3170d6"))
                .fillColor(0x302cdae0)).setZIndex(2);
        mMap.addCircle(new CircleOptions()
                .center(beaconsMap.get("C03B5CFA00B8").position)
                .radius(20) // radius of 5 metres
                .strokeColor(Color.parseColor("#3170d6"))
                .fillColor(0x302cdae0)).setZIndex(2);

         */

    }

    public void hideAllCircles(){
        for (String deviceMac : beaconsMap.keySet()){
            beaconsMap.get(deviceMac).circle.setVisible(false);
        }
    }
    public void updateCircleOnMap(String deviceMac, float distanceReached){
        beaconsMap.get(deviceMac).circle.setVisible(true);
        beaconsMap.get(deviceMac).circle.setRadius(distanceReached);
        // Update the market with a new title
        beaconsMap.get(deviceMac).marker.setTitle(deviceMac + " - Distance to Beacon: " + Float.toString(distanceReached));
    }

    public void updateEstimatedCurrentLocation(){
        getRequest(queue, coordinateEndPointURL);
        estimatedCurrentLocationCircle.setCenter(estimatedCurrentLocation);
    }

    private void getRequest(RequestQueue queue, String url) {
        StringRequest stringRequest = new StringRequest(Request.Method.GET, url,
                new Response.Listener<String>() {
                    @Override
                    public void onResponse(String response) {
                        if (!response.equals(null)) {
                            try { // Filters irrelevant responses
                                // response is formated into
                                // line 1 is estimated location
                                // the rest is mac_address and its distance reached
                                String[] lines = response.split("\\r?\\n");
                                Log.e("getRequest", "Response is: \n" + response);
                                if (lines[0].equals("null")){
                                    Toast.makeText( Activity_1_Maps.this,"Null response, could not estimate position", Toast.LENGTH_LONG).show();
                                    Log.e("getRequest", "Could not estimate position");
                                } else if (lines[0].equals("Not enough beacons")){
                                    Toast.makeText( Activity_1_Maps.this,"Not enough beacons nearby to estimate your location!", Toast.LENGTH_LONG).show();
                                    Log.e("getRequest", "Not enough beacons.");
                                } else if (lines[0].equals("Failed to find using 2 beacons")) {
                                    Toast.makeText(Activity_1_Maps.this, "There were 2 beacons nearby and failed to interpolate using last known position", Toast.LENGTH_LONG).show();
                                    Log.e("getRequest", "Failed to interpolate");
                                } else if (lines[0].contains(",")){
                                    Log.e("lines[0]", lines[0]);
                                    String[] estimatedLatLng = lines[0].split(",");
                                    Log.e("getRequest", "Estimated location is " + estimatedLatLng[0] + "," + estimatedLatLng[1]);
                                    try {
                                        estimatedCurrentLocation = new LatLng(Float.parseFloat(estimatedLatLng[0]), Float.parseFloat(estimatedLatLng[1]));
                                        Toast.makeText(Activity_1_Maps.this, "New location estimated!", Toast.LENGTH_LONG).show();
                                    } catch (Exception e){
                                        e.printStackTrace();
                                    }
                                }

                                // Update beacons distance reached
                                hideAllCircles();
                                Log.e("hideAllCircles", "Hide circles");
                                for (int i = 1; i < lines.length; i=i+1 ){
                                    Log.e("lines[" + i + "]", lines[i]);
                                    String deviceMac = lines[i].split(",")[0];
                                    float distanceReached = Float.parseFloat(lines[i].split(",")[1]);
                                    updateCircleOnMap(deviceMac, distanceReached);
                                    //Log.e(deviceMac, "distance reached: "+ Float.toString(distanceReached));
                                }
                            }catch (Exception e){
                                Log.e("getRequest", "Irrelevant response: " + response);
                            }
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

    // This is given in the IoTSSC coursework description
    // Source
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
                double distance = distanceBetweenTwoLatLng(beaconsMap.get(macAddress).position, beaconsMap.get(macAddress2).position);
                Log.e("testDistanceBetweenPont", macAddress + " to " + macAddress2 + " is " + Double.toString(distance) + " metres");
            }
        }
    }
}
