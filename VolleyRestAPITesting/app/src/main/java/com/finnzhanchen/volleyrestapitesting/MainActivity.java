package com.finnzhanchen.volleyrestapitesting;

import android.os.Handler;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.widget.TextView;

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
import com.android.volley.toolbox.Volley;

import org.w3c.dom.Text;

import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Timer;
import java.util.TimerTask;

public class MainActivity extends AppCompatActivity {
    private String AUTHORISATION_BEARER = "Bearer 57:3996aa851ea17f9dd462969c686314ed878c0cf7";
    String url = "http://glenlivet.inf.ed.ac.uk:8080/api/v1/svc/ep/test_coordinate_endpoint";
    String url2 = "http://glenlivet.inf.ed.ac.uk:8080/api/v1/svc/apps/data/docs/test";
    RequestQueue queue;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        /*
        // Instantiate the cache
        Cache cache = new DiskBasedCache(getCacheDir(), 1024 * 1024); // 1MB cap
        // Set up the network to use HttpURLConnection as the HTTP client.
        Network network = new BasicNetwork(new HurlStack());
        // Instantiate the RequestQueue with the cache and network.
        RequestQueue queue = new RequestQueue(cache, network);
        */
        // Instantiate the RequestQueue.
        // Instantiate the cache
        Cache cache = new DiskBasedCache(getCacheDir(), 1024 * 1024); // 1MB cap
        // Set up the network to use HttpURLConnection as the HTTP client.
        Network network = new BasicNetwork(new HurlStack());
        // Instantiate the RequestQueue with the cache and network.
        queue = new RequestQueue(cache, network);
        queue.start();


        final Handler handler = new Handler();
        final int delay = 3000; //milliseconds

        handler.postDelayed(new Runnable(){
            public void run(){
                // Update current location with a new circle
                getRequest(queue, url);
                handler.postDelayed(this, delay);
            }
        }, delay);


        //getRequest(queue, url);

        //getRequest(queue, url);
        //postRequest(queue, url2, "2013", "mac_asd", "-83");


    }

    private void getRequest(RequestQueue queue, String url) {
        StringRequest stringRequest = new StringRequest(Request.Method.GET, url,
                new Response.Listener<String>() {
                    @Override
                    public void onResponse(String response) {
                        if (!response.equals(null)) {
                            final TextView mTextView = (TextView) findViewById(R.id.text);
                            mTextView.setText(response);
                            // Display the first 500 characters of the response string.
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

        // Add the request to the RequestQueue.
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
        // Add the request to the RequestQueue.
        queue.add(stringRequest);
    }
}
