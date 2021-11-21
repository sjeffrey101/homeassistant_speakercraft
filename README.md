Home Assistant Speaker Craft

This project integrates a SpeakerCraft MZC66 to Home Assistant as a media player.

I created this as a personal project.  But someone may find it usefull.  Sorry instructions arent great, as i created it a while ago and just trying to remember what i did.

There are 2 parts to it, an ESP32 which has a RS232 adapter (i think this adjusts the voltages) and then links direct to the control port, using a serial cable to 3.5mm plug, which i got off ebay. 

The esp32 part is written in micropython.  You'll need to upload the main.py to the esp32 controller once micropythong is installed.

Copy the mqtt_media folder to the custom_components folder in Home assistant.

I then add my 8 zones to HA using the codein the configuration.yaml.  You'll see i have a default zone and volume, so when it turns on these are sent aswell.  I only use a single source, but multiple can be used
