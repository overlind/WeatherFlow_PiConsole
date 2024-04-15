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
        self.app.CurrentConditions.Obs['Obs_inSensTemp'] = ['-', 'c']
        self.app.CurrentConditions.Obs['Obs_inSensHum'] = ['-', '%']
        self.sensor_pin = board.D4
        self.gpio_reset_cnt = 0
        self.inSensTemp = StringProperty('-')
        self.inSensHum = StringProperty('-')
        self.sensor_poll = Clock.schedule_interval(self.get_temperature, 10)
        self.set_feels_like_icon()
        self.set_indoor_temp_display()

    # Set "Feels Like" icon
    def set_feels_like_icon(self):
        self.feelsLikeIcon = self.app.CurrentConditions.Obs['FeelsLike'][3]

    # Set whether to display indoor temperature  (from AIR)
    def set_indoor_temp_display(self):
        self.indoor_temperature = self.app.config['Display']['IndoorTemp']

    def get_temperature(self, *largs):
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.sensor_pin.id, GPIO.IN)
            # Attempt to get a temperature and humidity reading
            dht_sensor = adafruit_dht.DHT22(self.sensor_pin, use_pulseio=False)

            self.inSensTemp = dht_sensor.temperature or self.inSensTemp
            self.inSensHum = int(dht_sensor.humidity) or self.inSensHum

            inTemp = observation.units([self.inSensTemp, 'c'], self.config['Units']['Temp'])
            inHum = observation.units([self.inSensHum, '%'], self.config['Units']['Other'])

            self.app.CurrentConditions.Obs['Obs_inSensTemp'] = observation.format(inTemp, 'Temp')
            self.app.CurrentConditions.Obs['Obs_inSensHum'] = observation.format(inHum, 'Other')

        except RuntimeError as error:
            if self.gpio_reset_cnt < 3:
                self.gpio_reset_cnt += 1
            elif self.gpio_reset_cnt >= 3:
                GPIO.cleanup()
                self.gpio_reset_cnt = 0
        finally:
            dht_sensor.exit()

class TemperatureRPButton(RelativeLayout):
    pass
