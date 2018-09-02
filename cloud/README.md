# android_latest_position.py
Computes the latest location given the RSSIs in the past y seconds where y is the data time window. All beacons in the data time window are considered "discovered beacons" and their proximities are output. The script is called by a real-time visualisation Android app, and Android app visualise the latest estimated location and the discovered beacons' proximity.

# batch_process_all.py
Run the localisation algorithm for every x seconds for the RSSIs collected in the past y seconds at the time of the localisation algorithm where x is the algorithm time interval and y is the data time window. Results are saved in the collection of estimated locations. When the Cloud visualisation dashboard is opened, the script is called. Then, the Cloud dashboard retrieves the collection of estimated locations and visualise them.

# batch_process_all_experiments.py
Note that this script is identical as batch_process_all.py but has additional features. This script is not uploaded to the cloud for the following reasons:
* contains the optimisation algorithm for the result of the localisation algorithm but the sever did not have the necessary packages installed.
* used for evaluating accuracy of tests points outlined in the report
* get the CSV file for the prototype demo
* for experimenting different parameters for the algorithm
