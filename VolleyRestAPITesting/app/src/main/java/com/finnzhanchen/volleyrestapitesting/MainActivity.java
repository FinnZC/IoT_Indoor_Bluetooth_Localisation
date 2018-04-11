package com.finnzhanchen.volleyrestapitesting;

import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.widget.TextView;

import com.android.volley.AuthFailureError;
import com.android.volley.Cache;
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

public class MainActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        final TextView mTextView = (TextView) findViewById(R.id.text);
        // Instantiate the RequestQueue.
        //RequestQueue queue = Volley.newRequestQueue(this);

        // Instantiate the cache
        Cache cache = new DiskBasedCache(getCacheDir(), 1024 * 1024); // 1MB cap
        // Set up the network to use HttpURLConnection as the HTTP client.
        Network network = new BasicNetwork(new HurlStack());
        // Instantiate the RequestQueue with the cache and network.
        RequestQueue queue = new RequestQueue(cache, network);
        queue.start();
        String url = "http://glenlivet.inf.ed.ac.uk:8080/api/v1/svc/apps/data/docs/everything";
        getRequest(queue, url);
        postRequest(queue, url, "2013", "mac_asd", "-83");

    }

    private void getRequest(RequestQueue queue, String url) {
        StringRequest stringRequest = new StringRequest(Request.Method.GET, url,
                new Response.Listener<String>() {
                    @Override
                    public void onResponse(String response) {
                        if (!response.equals(null)) {
                            // Display the first 500 characters of the response string.
                            Log.e("getRequest", "Response is: " + response);
                        } else {
                            Log.e("getRequest", "Your Array Response Data Null");
                        }
                    }
                }, new Response.ErrorListener() {
            @Override
            public void onErrorResponse(VolleyError error) {
                Log.e("error is ", "" + error);
            }
        }) {
            // Authorisation
            @Override
            public Map<String, String> getHeaders() throws AuthFailureError {
                Map<String, String> params = new HashMap<>();
                params.put("Authorization", "Bearer 57:3996aa851ea17f9dd462969c686314ed878c0cf7");
                return params;
            }
        };
        // Add the request to the RequestQueue.
        queue.add(stringRequest);
    }

    private void postRequest(RequestQueue queue, String url, final String timestamp, final String deviceMac, final String rssi) {
        StringRequest stringRequest = new StringRequest(Request.Method.POST, url,
                new Response.Listener<String>() {
                    @Override
                    public void onResponse(String response) {
                        if (!response.equals(null)) {
                            // Display the first 500 characters of the response string.
                            Log.e("getRequest", "Response is: " + response);
                        } else {
                            Log.e("getRequest", "Your Array Response Data Null");
                        }
                    }

                }, new Response.ErrorListener() {
            @Override
            public void onErrorResponse(VolleyError error) {
                Log.e("error is ", "" + error);
            }
        }) {
            // Authorisation
            @Override
            public Map<String, String> getHeaders() throws AuthFailureError {
                Map<String, String> params = new HashMap<>();
                params.put("Authorization", "Bearer 57:3996aa851ea17f9dd462969c686314ed878c0cf7");
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
