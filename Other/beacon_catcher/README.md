# Phase 1 - Bluetooth scanning and communication with the cloud

At the end of the first phase you should be familiar with the embedded device, which you will be using extensively in the next phase.
This involves:

1. Developing an embedded application that can run on the IoT device, and discover the Bluetooth Beacons deployed in the lab (that are within range). This will be achieved by continuously scanning the wireless environment, and recording the Beacons’ identifier, the time of encounter, and the Received Signal Strength (RSS). 
1. Uploading the beacon scan information collected to the cloud for storage. Communication with the cloud must be performed through a Bluetooth gateway, as the IoT boards only have a Bluetooth transceiver. You can develop your own gateway, using the mobile phone you are provided. Alternatively you can use the gateway we set up for this purposes (documentation available on the cloud configuration website).

**Note** that you must only record Bluetooth MAC addresses that really correspond to the Beacons deployed in the lab, i.e. do not record arbitrary Bluetooth device MACs that could correspond to other devices and which you may overhear! To verify whether a broadcasting device is indeed an Beacon, you can interrogate it and obtain an appropriate confirmation. The list of beacons is also available through the Cloud API, therefore you can query the cloud to retrieve this. The list is also visible in the Cloud Configuration Tool. The list is not going to change.

See the documentation on the cloud configuration website for how to upload data to the cloud, and how to push beacon data (see Resources section for details).
