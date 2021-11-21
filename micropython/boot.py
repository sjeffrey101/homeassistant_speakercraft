
import esp

# you can run this from the REPL as well
esp.osdebug(None)


import network
sta_if = network.WLAN(network.STA_IF)
if not sta_if.isconnected():
	print('connecting to network...')
	sta_if.active(True)
	sta_if.connect('Wifi', 'Pass')
	while not sta_if.isconnected():
		pass
print('network config:', sta_if.ifconfig())



import webrepl
webrepl.start()


