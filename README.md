# homeassistant_mqtt_media_player
Media player custom component which works with MQTT.  I designed this to specifically work with a ESP32 which i used to control a speakercraft amp.

Copy the mqtt_media folder to the custom_components folder in Home assistant.

I then add my 8 zones to HA using this yaml.  You'll see i have a default zone and volume, so when it turns on these are sent aswell.  I only use a single source, but multiple can be used

media_player:
  - platform: mqtt_media
    name: "Lounge Speakers"
    entity_id: lounge_speakers
    command_topic: "speakercraft/command/zone1"
    state_topic: "speakercraft/zone1"
    sources:
      5: "Alexa"
    default_source: 5
    default_volume: 75

  - platform: mqtt_media
    name: "Kitchen Speakers"
    entity_id: kitchen_speakers
    command_topic: "speakercraft/command/zone2"
    state_topic: "speakercraft/zone2"
    sources:
      5: "Alexa"
    default_source: 5
    default_volume: 50
  - platform: mqtt_media
    name: "Den Speakers"
    entity_id: den_speakers
    command_topic: "speakercraft/command/zone3"
    state_topic: "speakercraft/zone3"
    sources:
      5: "Alexa"
    default_source: 5
    default_volume: 75

  - platform: mqtt_media
    name: "Outside Speakers"
    entity_id: outside_speakers
    command_topic: "speakercraft/command/zone4"
    state_topic: "speakercraft/zone4"
    sources:
      5: "Alexa"
    default_source: 5
    default_volume: 75

  - platform: mqtt_media
    name: "Master Speakers"
    entity_id: master_speakers
    command_topic: "speakercraft/command/zone5"
    state_topic: "speakercraft/zone5"
    sources:
      5: "Alexa"
    default_source: 5
    default_volume: 75
  
  - platform: mqtt_media
    name: "Bathroom Speakers"
    entity_id: bathroom_speakers
    command_topic: "speakercraft/command/zone6"
    state_topic: "speakercraft/zone6"
    sources:
      5: "Alexa"
    default_source: 5
    default_volume: 75

  - platform: mqtt_media
    name: "Kid1 Speakers"
    entity_id: kid1_speakers
    command_topic: "speakercraft/command/zone7"
    state_topic: "speakercraft/zone7"
    sources:
      5: "Alexa"
    default_source: 5
    default_volume: 75

  - platform: mqtt_media
    name: "Kid2 Speakers"
    entity_id: kid2_speakers
    command_topic: "speakercraft/command/zone8"
    state_topic: "speakercraft/zone8"
    sources:
      5: "Alexa"
    default_source: 5
    default_volume: 75
