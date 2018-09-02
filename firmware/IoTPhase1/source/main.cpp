// PLEASE NOTE THAT ALL PRINTF HAVE BEEN COMMENTED OUT 
// BECAUSE IT WILL BE STUCK AT PRINTF STATEMENT WHEN 
// IT IS NOT CONNECTED TO ANY TERMINAL TO VIEW THE OUTPUT
#include <events/mbed_events.h>
#include <mbed.h>
#include "ble/BLE.h"
#include "ble/DiscoveredCharacteristic.h"
#include "ble/DiscoveredService.h"
#include "NotifyArrayGattCharacteristic.h"

DigitalOut alivenessLED(LED1, 1);
uint16_t macRssiServiceUUID  = 0xA000; // Custom Service UUID
uint16_t macRssiCharUUID       = 0xA001; // Characteristics that contains MAC address and RSSI

static EventQueue eventQueue(/* event count */ 16 * EVENTS_EVENT_SIZE);
const static char     DEVICE_NAME[]        = "JoBy1NoBa"; // change this
static const uint16_t uuid16_list[]        = {0xFFFF}; //Custom UUID, FFFF is reserved for development

/* Set Up custom Characteristics */
static uint8_t macRssiValue[7] = {0};
// mac_address_and_rssi is 7 bytes of unsigned integer
// 0-6 is mac address and 7 is the rssi in uint8_t which will be 
// converted to int8_t in the gateway android app
// to get its decimal reprensetation (e.g. -90)

// Create custom characteristics of "Notify" property
NotifyArrayGattCharacteristic<uint8_t, sizeof(macRssiValue)> notifyChar(macRssiCharUUID, macRssiValue);

// Set up custom service
GattCharacteristic *characteristics[] = {&notifyChar};
GattService        customService(macRssiServiceUUID, characteristics, sizeof(characteristics) / sizeof(GattCharacteristic *));

void periodicCallback(void) {
    //printf("blinky\r\n");
    alivenessLED = !alivenessLED; /* Do blinky on LED1 while we're waiting for BLE events */
}


int isLabBeaconWithinRange(int8_t rssi){
    // Return 1 if the detected lab beacon is within range (>105-dDm)
    if (rssi > -105){
        return 1;
    } else {
        return 0;
    }
}

int isLabBeacon(unsigned char *mac_address){
    // Compares the first 2 hex of the received mac address
    // with the first 2 hex of the lab beacon addresses in the lab
    // although not perfect, it would achieve the purposes for the prototype
    const unsigned char first_hex_lab_addresses[] = {0xED, 0xE7, 0xC7, 0xEC,
                                                     0xFE, 0xC0, 0xE0, 0xF1,
                                                     0xF1, 0xFD};
    const unsigned char second_hex_lab_addresses[] = {0x23, 0x31, 0xBC, 0x75,
                                                      0x12, 0x3B, 0xB8, 0x55,
                                                      0x7F, 0x81};
                                                      
    // each i represents a different lab beacon mac address
    for (int i = 0; i < sizeof(first_hex_lab_addresses); i++){
        if (mac_address[0] == first_hex_lab_addresses[i] 
            && mac_address[1] == second_hex_lab_addresses[i]){
            return 1;
        }
    }
    return 0;
}

void advertisementCallback(const Gap::AdvertisementCallbackParams_t *params) {
    unsigned char mac_address[] = {
        params->peerAddr[5], params->peerAddr[4],
        params->peerAddr[3], params->peerAddr[2],
        params->peerAddr[1], params->peerAddr[0]};

    if (isLabBeacon(mac_address) /*&& isLabBeaconWithinRange(params->rssi)*/){
        // The following printf is for debugging purposes
        /*printf("MAC Address [%02x %02x %02x %02x %02x %02x] rssi %d\r\n",
            params->peerAddr[5], params->peerAddr[4], params->peerAddr[3],
            params->peerAddr[2], params->peerAddr[1], params->peerAddr[0],
            params->rssi);
        */
            
        unsigned char mac_address_and_rssi[] = {
            params->peerAddr[5], params->peerAddr[4],
            params->peerAddr[3], params->peerAddr[2],
            params->peerAddr[1], params->peerAddr[0], 
            (uint8_t) params->rssi}; 
        // Note rssi is converteed from int8_t to uint8_t. This will be converted back to int8_t when received by the gateway
        
        // Update characteristic macRssiValue with notify properties with the new values
        BLE::Instance(BLE::DEFAULT_INSTANCE).gattServer().write(notifyChar.getValueHandle(), mac_address_and_rssi, sizeof(mac_address_and_rssi));
        
    }
}


void disconnectionCallback(const Gap::DisconnectionCallbackParams_t *) {
    //printf("disconnected\r\n");
    /* Start scanning and try to connect again */
    BLE::Instance().gap().startScan(advertisementCallback);
    BLE::Instance().gap().startAdvertising();
}

void onBleInitError(BLE &ble, ble_error_t error)
{
   //printf("onBleInitError\r\n");/* Initialization error handling should go here */
}

void printMacAddress()
{
    /* Print out device MAC address to the console*/
    Gap::AddressType_t addr_type;
    Gap::Address_t address;
    BLE::Instance().gap().getAddress(&addr_type, address);
    printf("DEVICE MAC ADDRESS: ");
    for (int i = 5; i >= 1; i--){
        printf("%02x:", address[i]);
    }
    printf("%02x\r\n", address[0]);
}

void bleInitComplete(BLE::InitializationCompleteCallbackContext *params)
{
    BLE&        ble   = params->ble;
    ble_error_t error = params->error;

    if (error != BLE_ERROR_NONE) {
        /* In case of error, forward the error handling to onBleInitError */
        onBleInitError(ble, error);
        return;
    }

    /* Ensure that it is the default instance of BLE */
    if (ble.getInstanceID() != BLE::DEFAULT_INSTANCE) {
        return;
    }

    ble.gap().onDisconnection(disconnectionCallback);

    // scan interval: 10ms and scan window: 10ms.
    // Every 10ms the device will scan for 10ms
    // This means that the device will scan continuously.
    ble.gap().setScanParams(10, 10);
    ble.gap().startScan(advertisementCallback);

    /* Setup advertising */
    ble.gap().accumulateAdvertisingPayload(GapAdvertisingData::BREDR_NOT_SUPPORTED | GapAdvertisingData::LE_GENERAL_DISCOVERABLE); // BLE only, no classic BT
    ble.gap().setAdvertisingType(GapAdvertisingParams::ADV_CONNECTABLE_UNDIRECTED); // advertising type
    ble.gap().accumulateAdvertisingPayload(GapAdvertisingData::COMPLETE_LOCAL_NAME, (uint8_t *)DEVICE_NAME, sizeof(DEVICE_NAME)); // add name
    ble.gap().accumulateAdvertisingPayload(GapAdvertisingData::COMPLETE_LIST_16BIT_SERVICE_IDS, (uint8_t *)uuid16_list, sizeof(uuid16_list)); // UUID's broadcast in advertising packet
    ble.gap().setAdvertisingInterval(50); // 50ms.

    /* Add our custom service */
    ble.addService(customService);

    /* Start advertising */
    ble.gap().startAdvertising();
    
    //printMacAddress();
}

void scheduleBleEventsProcessing(BLE::OnEventsToProcessCallbackContext* context) {
    //printf("scheduleBleEventsProcessing\r\n");
    BLE &ble = BLE::Instance();
    eventQueue.call(Callback<void()>(&ble, &BLE::processEvents));
}

int main()
{

    BLE &ble = BLE::Instance();
    ble.onEventsToProcess(scheduleBleEventsProcessing);
    ble.init(bleInitComplete);
    eventQueue.call_every(500, periodicCallback);
    eventQueue.dispatch_forever();
    /* SpinWait for initialization to complete. This is necessary because the
     * BLE object is used in the main loop below. */
    while (ble.hasInitialized()  == false) { /* spin loop */ }
        /* Infinite loop waiting for BLE interrupt events */
    while (true) {
        ble.waitForEvent(); /* Save power */
    }
}
