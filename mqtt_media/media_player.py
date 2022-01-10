"""Support for MQTT Media player."""
import logging
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
import json
import homeassistant.components.mqtt as mqtt

from homeassistant.components.media_player import PLATFORM_SCHEMA, MediaPlayerEntity
from homeassistant.components.media_player.const import (
    SUPPORT_SELECT_SOURCE,
    SUPPORT_TURN_OFF,
    SUPPORT_TURN_ON,
    SUPPORT_VOLUME_MUTE,
    SUPPORT_VOLUME_SET,
    SUPPORT_VOLUME_STEP,
)
from homeassistant.const import (
    ATTR_ID,
    STATE_OFF,
    STATE_ON,
)


_LOGGER = logging.getLogger(__name__)

CONF_SOURCES = "sources"
CONF_NAME = "name"
CONF_STATE_TOPIC = "state_topic"
CONF_COMMAND_TOPIC = "command_topic"
CONF_ENTITY_ID = "entity_id"
CONF_DEFAULT_SOURCE = "default_source"
CONF_DEFAULT_VOLUME = "default_volume"

DEFAULT_SOURCES = {
    1: "Source 1",
    2: "Source 2",
    3: "Source 3",
    4: "Source 4",
    5: "Source 5",
    6: "Source 6",
    7: "Source 7",
    8: "Source 8",

}


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_ENTITY_ID): cv.string,
        vol.Required(CONF_STATE_TOPIC): mqtt.valid_subscribe_topic,
        vol.Required(CONF_COMMAND_TOPIC): mqtt.valid_subscribe_topic,
        vol.Optional(CONF_SOURCES, default=DEFAULT_SOURCES): {cv.positive_int : cv.string},
        vol.Optional(CONF_DEFAULT_SOURCE, default=0): cv.positive_int,
        vol.Optional(CONF_DEFAULT_VOLUME, default=0): cv.positive_int,
    }
)

ZONE_JSON_PAYLOAD_SCHEMA = vol.Schema(
    {
        vol.Required("Power"): cv.string,
        vol.Required("Volume"): vol.Coerce(int),
        vol.Optional("Mute"): cv.string,
        vol.Optional("Source"): vol.Coerce(int),
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):


    devices = []
    
 
                
    dev = MQTTMediaPlayer(hass, config.get(CONF_NAME), config.get(CONF_ENTITY_ID), config.get(CONF_STATE_TOPIC), config.get(CONF_COMMAND_TOPIC),  config.get(CONF_SOURCES), config.get(CONF_DEFAULT_SOURCE), config.get(CONF_DEFAULT_VOLUME))
    
    devices.append(dev)

    async_add_entities(devices)


class MQTTMediaPlayer(MediaPlayerEntity):
    """Representation of a Russound Zone."""

    def __init__(self, hass, name, entity_id, state, command , sources, default_source, default_volume):
        """Initialize the zone device."""
        super().__init__()

        sources[256] = "Off"

        self._entity_id = entity_id
        self._hass = hass
        self._name = name
        self._topic_state = state
        self._topic_command = command
        self._sources = sources
        self._mqtt = hass.components.mqtt
        self._source_list = list(sources.values())
        self._source_mapping = sources
        self._source_reverse = {value: key for key, value in sources.items()}
        self._default_source = default_source
        self._default_volme = default_volume

        self._st_power = "Off"
        self._st_volume = 0
        self._st_mute = False
        self._st_source = 256

 

    async def async_added_to_hass(self):
        async def message_received(msg):
            try:
                payload = ZONE_JSON_PAYLOAD_SCHEMA(json.loads(msg.payload))
            except vol.MultipleInvalid:
                _LOGGER.error(
                    "Skipping update for following data "
                    "because of missing or malformatted data: %s",
                    msg.payload,
                )
                return
            except ValueError:
                _LOGGER.error("Error parsing JSON payload: %s", msg.payload)
                return
            
            self._st_volume = payload["Volume"] / 100.00
            self._st_mute = payload["Mute"]
            self._st_power = payload["Power"]
            self._st_source = payload["Source"]
            self.schedule_update_ha_state() 

        await self._mqtt.async_subscribe(self._topic_state, message_received)
        
        
    @property
    def should_poll(self):
        """No polling needed."""
        return False

    @property
    def name(self):
        """Return the name of the zone."""
        return self._name

    @property
    def state(self):
        """Return the state of the device."""
        
        if self._st_power == "On":
            return STATE_ON
        else:
            return STATE_OFF

    @property
    def icon(self):
        return "mdi:speaker"

    @property
    def unique_id(self):
        return self._entity_id


    @property
    def device_class(self):
        """Volume level of the media player (0..1)."""
        return "speaker"

    @property
    def supported_features(self):
        """Flag media player features that are supported."""
        return (SUPPORT_VOLUME_MUTE | SUPPORT_VOLUME_SET | SUPPORT_TURN_ON | SUPPORT_TURN_OFF | SUPPORT_SELECT_SOURCE | SUPPORT_VOLUME_STEP)

    @property
    def source(self):
        """Get the currently selected source."""
        if self._st_source in self._source_mapping:
            return self._source_mapping[self._st_source]
        else:
            return "Unknown"

    @property
    def source_list(self):
        """Return a list of available input sources."""
        """return [x[1] for x in self._sources]"""
        return self._source_list

    @property
    def volume_level(self):
        """Volume level of the media player (0..1)."""
        return self._st_volume

    @property
    def is_volume_muted(self):
        """Volume level of the media player (0..1)."""
        if self._st_mute == "Muted":
            return True
        else:
            return False

    

    async def async_turn_off(self):
        await mqtt.async_publish(self.hass, self._topic_command, "Power Off")
        if self._default_volme > 0:
            await mqtt.async_publish(self.hass, self._topic_command, "Volume Level " + str(self._default_volme))

    async def async_turn_on(self):
        
        if self._default_source > 0:
            await mqtt.async_publish(self.hass, self._topic_command, "Source " + str(self._default_source))
        else:
            await mqtt.async_publish(self.hass, self._topic_command, "Power On")
            

    async def async_set_volume_level(self, volume):
        volumepc = volume * 100
        await mqtt.async_publish(self.hass, self._topic_command, "Volume Level " + str(int(volumepc)))

    async def async_select_source(self, source):
        """Set the input source."""
        if source in self._source_list:
            source = self._source_reverse[source]
            await mqtt.async_publish(self.hass, self._topic_command, "Source " + str(source))
        

    async def async_mute_volume(self, mute):
        if mute:
             await mqtt.async_publish(self.hass, self._topic_command, "Mute")
        else:
             await mqtt.async_publish(self.hass, self._topic_command, "Unmute")
        
    async def async_volume_up(self):
        await mqtt.async_publish(self.hass, self._topic_command, "Volume Up")

    async def async_volume_down(self):
        await mqtt.async_publish(self.hass, self._topic_command, "Volume Down")
