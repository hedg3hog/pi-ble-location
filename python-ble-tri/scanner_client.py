import asyncio

from bleak import  BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData
from rich import print
import requests

from models import BLEcapture

PUSH_URL = "http://192.168.8.124:8000/push_data"


stop_event = asyncio.Event()
async def main(stop_event):
    

    print("Entering main function")

    async def callback(device: BLEDevice, advertising_data: AdvertisementData):
  
        #print("############### BLE DEVICE ############")
        #print("address:", device.address, ", name:", device.name, ", details: device.details", ", rssi:", advertising_data.rssi)
        #print("#######################################\n\n")
        try:
            if device.name is None:
                return
            elif "pibeacon" not in device.name:
                return
            elif "iphone" not in device.name.lower() and "schl" not in device.name.lower():
                print(device.name)
            print("address:", device.address, ", name:", device.name, ", details: device.details", ", rssi:", advertising_data.rssi, advertising_data)
            data = BLEcapture(device_name=device.name, device_address=device.address, rssi=advertising_data.rssi, tx_power=advertising_data.tx_power)
            
            requests.post(PUSH_URL, data=data.model_dump_json(), timeout=2)
        except requests.HTTPError:
            return
        except Exception as e:
            print(e)
            return
        
    run = True
    while run:
        print("entered main loop")
        async with BleakScanner(callback) as scanner:
            # Important! Wait for an event to trigger stop, otherwise scanner
            # will stop immediately.
            try:
                print("Starting to listen")
                await stop_event.wait()
            except KeyboardInterrupt:
                stop_event.set()
                run = False
                print("got keyboard interupt")
            except Exception as e:
                print(e)
                continue
    print("exiting main func")

try:    
    asyncio.run(main(stop_event=stop_event))
except KeyboardInterrupt:
    stop_event.set()
    print("Bye!")
    exit(0)

print("I should not be reached")