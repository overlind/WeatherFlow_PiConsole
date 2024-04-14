""" Defines the Temperature panel required by the Raspberry Pi Python console
for WeatherFlow Tempest and Smart Home Weather stations.
Copyright (C) 2018-2023 Peter Davis

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.
"""

# Load required Raspberry Pi modules
import board
import adafruit_dht
import RPi.GPIO as GPIO

# Import required library modules
from lib             import derived_variables  as derive
from lib             import observation_format as observation

# Load required Kivy modules
from kivy.uix.relativelayout import RelativeLayout
from kivy.properties         import StringProperty
from kivy.clock              import Clock

# Load required panel modules
from panels.template         import panelTemplate


# ==============================================================================
# TemperatureRPPanel AND TemperatureRPButton CLASS
# ==============================================================================
class TemperatureRPPanel(panelTemplate):
    # Define TemperaturePanel class properties
    feelsLikeIcon = StringProperty('-')
    indoor_temperature = StringProperty('-')

    # Initialise TemperatureRPPanel
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.config = self.app.config
        self.sensor_pin = board.D4
        self.app.CurrentConditions.Obs['inSensTemp'] = [None, 'c']
        self.sensor_poll = Clock.schedule_interval(self.get_temperature, 10)
        self.inSensTemp = None
        self.set_feels_like_icon()
        self.set_indoor_temp_display()

    # Set "Feels Like" icon
    def set_feels_like_icon(self):
        self.feelsLikeIcon = self.app.CurrentConditions.Obs['FeelsLike'][3]

    # Set whether to display indoor temperature
    def set_indoor_temp_display(self):
        self.indoor_temperature = self.app.config['Display']['IndoorTemp']

    def get_temperature(self, *largs):
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.sensor_pin.id, GPIO.IN)
            # Attempt to get a temperature and humidity reading
            dht_sensor = adafruit_dht.DHT22(self.sensor_pin, use_pulseio=False)
            self.inSensTemp = dht_sensor.temperature or self.inSensTemp
            self.app.CurrentConditions.Obs['inSensTemp'] = [f"{self.inSensTemp:.1f}", 'c']

            # humidity = observation.units(self.device_obs['humidity'], self.config['Units']['Other'])
            inTemp = observation.units(self.app.CurrentConditions.Obs['inSensTemp'], self.config['Units']['Temp'])

            # self.display_obs['Humidity'] = observation.format(humidity, 'Humidity')
            self.app.CurrentConditions.Obs['inSensTemp'] = observation.format(inTemp, 'Temp')

            # self.app.CurrentConditions.Obs['inTempMax'] = self.inTemp
            # self.app.CurrentConditions.Obs['inTempMin'] = self.inTemp
            # self.humidity = dht_sensor.humidity
            # GPIO.cleanup()
            # light_state = GPIO.input(LIGHT_PIN.id)
            # light_condition = "On" if light_state == GPIO.LOW else "Off"

            # temperature_farenheit = (9 / 5 * temperature_celsius) + 32

            # Check if the values are valid (e.g., not None)
            # if temperature_celsius is not None and humidity_percent is not None:
            #     print(f"Temp: {temperature_celsius:.1f}deg C, "
            #           f"{temperature_farenheit:.1f}deg F, "
            #           f"Humidity: {humidity_percent:.1f}%, ")
            #           # f"Light: {light_condition}")
            # else:
            #     print("Failed to retrieve data from the sensor")

        except RuntimeError as error:
            pass
            # Errors happen fairly often, DHT's are hard to read, just keep going
            # GPIO.cleanup()
            # GPIO.setmode(GPIO.BCM)
            # GPIO.setup(self.sensor_pin.id, GPIO.IN)
            # GPIO.setup(LIGHT_PIN.id, GPIO.IN)
            # continue
        finally:
            dht_sensor.exit()


class TemperatureRPButton(RelativeLayout):
    pass
