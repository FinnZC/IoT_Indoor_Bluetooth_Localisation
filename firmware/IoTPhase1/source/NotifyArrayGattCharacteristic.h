// Custom Gatt Characteristics by Finn Zhan Chen derived from GattCharacteristics.h
template <typename T, unsigned NUM_ELEMENTS>
class NotifyArrayGattCharacteristic : public GattCharacteristic {
public:

    NotifyArrayGattCharacteristic<T, NUM_ELEMENTS>(const UUID    &uuid,
                                                      T              valuePtr[NUM_ELEMENTS],
                                                      uint8_t        additionalProperties = BLE_GATT_CHAR_PROPERTIES_NONE,
                                                      GattAttribute *descriptors[]        = NULL,
                                                      unsigned       numDescriptors       = 0) :
        GattCharacteristic(uuid, reinterpret_cast<uint8_t *>(valuePtr), sizeof(T) * NUM_ELEMENTS, sizeof(T) * NUM_ELEMENTS,
                           BLE_GATT_CHAR_PROPERTIES_NOTIFY | additionalProperties, descriptors, numDescriptors) {
        /* empty */
    }
};