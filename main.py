# main.py

from umqtt.robust import MQTTClient
import machine
import utime as time
import gc
import binascii
import ujson

# Wifi connect established in the boot.py file. Uncomment if needed
# import network
# sta_if = network.WLAN(network.STA_IF)
# sta_if.active(True)
# sta_if.connect("NCW", "malolos5459")
volumetodb = [80, 78, 78, 76, 74, 74, 72, 72, 70, 68, 68, 66, 64, 64, 62, 62, 60, 58, 58, 56, 54, 54, 52, 52, 50, 48, 48, 46, 46, 44, 43, 43, 42, 41, 41, 40, 40, 39, 38, 38, 37, 36, 36, 35, 35, 34, 33, 33, 32, 32, 31, 30, 30, 29, 28, 28, 27, 27, 26, 25, 25, 24, 23, 23, 22, 22, 21, 20, 19, 19, 18, 18, 17, 17, 16, 15, 15, 14, 14, 13, 12, 12, 11, 10, 10, 9, 9, 8, 7, 7, 6, 5, 5, 4, 4, 3, 2, 2, 1, 1, 0]
command = bytearray()

from machine import WDT
wdt = WDT(timeout=10000)  # enable it with a timeout of 2s

def sub_checksum(data):
    checksum = sum(data)
    while checksum > 256:
        checksum -= 256	
    return 0x100 - checksum

def sub_cb(topic, msg):
    global command, sub_checksum, volumetodb, client
    print("Command Recieved")
    print((topic, msg))
    
    command = bytearray()
	
    type=""

    if topic == b'speakercraft/command/zone1':
        zone = 0
        type = "zone"
    elif topic == b'speakercraft/command/zone2':
        zone = 1
        type = "zone"
    elif topic == b'speakercraft/command/zone3':
        zone = 2
        type = "zone"
    elif topic == b'speakercraft/command/zone4':
        zone = 3
        type = "zone"
    elif topic == b'speakercraft/command/zone5':
        zone = 4
        type = "zone"
    elif topic == b'speakercraft/command/zone6':
        zone = 5
        type = "zone"
    elif topic == b'speakercraft/command/zone7':
        zone = 6
        type = "zone"
    elif topic == b'speakercraft/command/zone8':
        zone = 7
        type = "zone"
    
    if type=="zone":
        if msg == b'Power On':
            print("Turn on zone " + str(zone))
            command = bytearray([0x55, 0x04, 0xA0, zone])
        elif msg == b'Power Off':
            print("Turn on zone " + str(zone))
            command = bytearray([0x55, 0x04, 0xA1, zone])
        elif msg == b'Mute':
            print("Mute zone " + str(zone))
            command = bytearray([0x55, 0x08, 0x57, 0x00, 0x00, 0x04, 0x00, zone])
        elif msg == b'Unmute':
            print("Unmute zone " + str(zone))
            command = bytearray([0x55, 0x08, 0x57, 0x00, 0x00, 0x03, 0x00, zone])
        elif msg == b'Volume Up':
            print("Volume up zone " + str(zone))
            command = bytearray([0x55, 0x08, 0x57, 0x00, 0x00, 0x01, 0x00, zone])
        elif msg == b'Volume Down':
            print("Volume down zone " + str(zone))
            command = bytearray([0x55, 0x08, 0x57, 0x00, 0x00, 0x00, 0x00, zone])
        elif msg[:12] == b'Volume Level':

            volume = int(msg[13:].decode('utf-8'))
            volumeDB = volumetodb[volume]

            print("Volume Level zone " + str(zone) + " " + str(volume) + " DB " + str(volumeDB))
            command = bytearray([0x55, 0x08, 0x57, 0x00, 0x00, 0x05,  volumeDB, zone])

        elif msg[:6] == b'Source':
            print("Source zone " + str(zone) + " " + str(msg[7:8]))
            source = int(msg[7:8])-1
            command = bytearray([0x55, 0x05, 0xA3, zone, source])


    if len(command) > 0:
        checksum = sub_checksum(command)
        command.append(checksum)
        client.publish(topic="speakercraft/status", msg='command queued')

def checkwifi():
    while not sta_if.isconnected():
        time.sleep_ms(500)
        print(".")
        sta_if.connect()
    

client = MQTTClient("speakercraft", "192.168.0.100", 1883)
client.set_callback(sub_cb)
client.connect()
client.subscribe("speakercraft/command/+")

uart = machine.UART(2, tx=17, rx=16, baudrate=57600)  

print("Starting Loop")
	
	
previous = {}
previous[1] = ""
previous[2] = ""
previous[3] = ""
previous[4] = ""
previous[5] = ""
previous[6] = ""
previous[7] = ""
previous[8] = ""

lastread = time.ticks_ms()

	
while True:
    wdt.feed()
    zonestatus = {}
    checkwifi()
    #check for messages if there isnt one already queued
    if len(command) == 0:
            client.check_msg()
            

    if uart.any() > 0:
        lastread = time.ticks_ms()
        byte = uart.read(1)
        if byte == b'\x11':
            #windows open
            if len(command) > 0:
                #print("Write " + str(command))
                uart.write(command)
                client.publish(topic="speakercraft/status", msg='command sent')
            
        elif byte == b'\x13':
            #windows closed
            pass
        elif byte == b'\x55':
            #incoming message
            #get the length
            byte = uart.read(1)
            length = int.from_bytes(byte, "big") - 1
            #read message
            bytes = uart.read(length)
            #get type of message
            if bytes[:1] == b'\x20':
               #zone update
               zone = int.from_bytes(bytes[1:2], "big")  + 1 
               zonestatus["Zone"] = zone
               print("Update Zone:" + str(zone))
               status = '{:08b}'.format(ord(bytes[3:4]))
               if status[6:7] == "1":
                   zonestatus["Power"] = "On"
               else:
                   zonestatus["Power"] = "Off"
               if status[7:8] == "1":
                   zonestatus["Mute"] = "Muted"
               else:
                   zonestatus["Mute"] = "Unmuted"

               zonestatus["Source"] = int.from_bytes(bytes[4:5], "big")+1
               zonestatus["Volume"] = int.from_bytes(bytes[5:6], "big")
               zonestatus["Bass"] = int.from_bytes(bytes[6:7], "big")
               zonestatus["Trebble"] = int.from_bytes(bytes[7:8], "big")
               zonestatus["VolumeDB"] = int.from_bytes(bytes[8:9], "big")
               json = ujson.dumps(zonestatus)
               if previous[zone] != json:
                   client.publish(topic="speakercraft/zone" + str(zone), msg=json, retain=True)
                   previous[zone] = json

			   
               print(zonestatus)
            elif bytes[:1] == b'\x29':
                #tuner update
               print("Update Tuner")
            elif bytes[:1] == b'\x95':
               #response to command
               #clear the command
               command = bytearray()
               print("Responce Recieved")
               client.publish(topic="speakercraft/status", msg='command recieved')
            else:
               #unknown message
               print("Update Unknown")
        else:
            #completely unknown
            print("Unknown")

    delta = time.ticks_diff(time.ticks_ms(), lastread)
    if delta > 1000:
        time.sleep_ms(100)
    else:
        time.sleep_ms(2)
