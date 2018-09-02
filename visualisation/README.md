# real-time-Android-visualisation
An Android app has been developed to visualise the results of the localisation algorithm in real time. The app calls an API end point in the Cloud which returns the geographic coordinates of the latest location alongside the MAC addresses and proximity of discovered beacons.

# cloud-visualisation-dashboard is ran on the Cloud and contains 4 visualisations:
* index.html: The homepage shows all estimations computed from the batch processing script on the Cloud as markers on the Google Map. Each marker has their title set to their time of computation. This page also has 3 buttons to navigate to the other 3 visualisations.

* path_trace_animated.html: Path trace plots the one estimation marker at a time. This repeats until no more estimations are left. The timestamp of the estimation is shown on the menu and speed can be adjusted from the menu. This helps the author to visualise inaccurate estimation and adjust parameters in the algorithm accordingly.

*  path_reconstruction.html: Like path trace, path reconstruction plots computed estimation as a marker sequentially for an adjustable time interval. Unlike path trace, the plotted markers will remain. This visualisation assists in evaluating the accuracy of non-moving and moving IoT device.

* heatmap.html: This plots a heatmap of the estimated locations. The denser an area is, the stronger the colour is. This visualisation helps the author in evaluating areas on the map that are rarely the result of the localisation algorithm.
