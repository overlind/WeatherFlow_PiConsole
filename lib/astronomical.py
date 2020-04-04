""" Returns the astronomical variables required by the Raspberry Pi Python 
console for Weather Flow Smart Home Weather Stations. Copyright (C) 2018-2020  
Peter Davis

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.
"""

# Import required modules
from astral.sun  import sun
from datetime    import datetime, timedelta, date, time
from astral      import LocationInfo
from astral      import moon
import pytz

import ephem

def SunriseSunset(astroData,Config):

    """ Calculate sunrise and sunset times for the current day or tomorrow
    in the station timezone
	
	INPUTS: 
		astroData			Dictionary holding sunrise and sunset data
		Config              Station configuration
		
	OUTPUT: 
        astroData           Dictionary holding sunrise and sunset data
	"""
    
    # Define Sunrise/Sunset location properties
    Tz = pytz.timezone(Config['Station']['Timezone'])
    Station = LocationInfo()
    Station.latitude  = Config['Station']['Latitude']
    Station.longitude = Config['Station']['Longitude']
    Station.timezone  = Config['Station']['Timezone']
    
    # The code is initialising. Calculate sunset/sunrise times for current day 
    # starting at midnight in Station timezone
    if astroData['Sunset'][0] == '-':

        # Set Observer time to midnight today in Station timezone 
        Now = datetime.now(pytz.utc).astimezone(Tz)
        Midnight = datetime(Now.year,Now.month,Now.day,0,0,0)

        # Sunrise and sunset time
        Sunrise = sun(Station.observer, Midnight)['sunrise']
        Sunset = sun(Station.observer, Midnight)['sunset']

        # Define Kivy label binds in Station timezone
        astroData['Sunrise'][0] = Sunrise.astimezone(Tz)
        astroData['Sunset'][0] = Sunset.astimezone(Tz)

    # Sunset has passed. Calculate sunset/sunrise times for tomorrow starting at 
    # midnight in Station timezone
    else:

        # Set Observer time to midnight tomorrow in Station timezone 
        Now = datetime.now(pytz.utc).astimezone(Tz)
        Midnight = datetime(Now.year,Now.month,Now.day,0,0,0) + timedelta(days=1)

        # Sunrise and sunset time
        Sunrise = sun(Station.observer, Midnight)['sunrise']
        Sunset = sun(Station.observer, Midnight)['sunset']

        # Define Kivy label binds in Station timezone
        astroData['Sunrise'][0] = Sunrise.astimezone(Tz)
        astroData['Sunset'][0] = Sunset.astimezone(Tz)
        
    # Format sunrise/sunset labels based on date of next sunrise
    astroData = Format(astroData,Config,'Sun')
    
    # Return astroData
    return astroData
    
def MoonriseMoonset(astroData,Config):

    """ Calculate moonrise and moonset times for the current day or 
    tomorrow in the station timezone
	
	INPUTS: 
		astroData			Dictionary holding moonrise and moonset data
		Config              Station configuration
		
	OUTPUT: 
        astroData           Dictionary holding moonrise and moonset data
	"""

    # Define Moonrise/Moonset location properties
    Tz = pytz.timezone(Config['Station']['Timezone'])
    Now = datetime.now(pytz.utc).astimezone(Tz)
    Ob = ephem.Observer()
    Ob.lat = str(Config['Station']['Latitude'])
    Ob.lon = str(Config['Station']['Longitude'])

    # The code is initialising. Calculate moonrise time for current day
    # starting at midnight in station time zone
    if astroData['Moonrise'][0] == '-':

        # Convert midnight in Station timezone to midnight in UTC
        Date = date.today()
        Midnight = Tz.localize(datetime.combine(Date,time()))
        Midnight_UTC = Midnight.astimezone(pytz.utc)
        Ob.date = Midnight_UTC.strftime('%Y/%m/%d %H:%M:%S')

        # Calculate Moonrise time in Station time zone
        Moonrise = Ob.next_rising(ephem.Moon())
        Moonrise = pytz.utc.localize(Moonrise.datetime())
        astroData['Moonrise'][0] = Moonrise.astimezone(Tz)

    # Moonset has passed. Calculate time of next moonrise in station
    # timezone
    else:

        # Convert moonset time in Station timezone to moonset time in UTC
        Moonset = astroData['Moonset'][0].astimezone(pytz.utc)
        Ob.date = Moonset.strftime('%Y/%m/%d %H:%M:%S')

        # Calculate Moonrise time in Station time zone
        Moonrise = Ob.next_rising(ephem.Moon())
        Moonrise = pytz.utc.localize(Moonrise.datetime())
        astroData['Moonrise'][0] = Moonrise.astimezone(Tz)

    # Convert Moonrise time in Station timezone to Moonrise time in UTC
    Moonrise = astroData['Moonrise'][0].astimezone(pytz.utc)
    Ob.date = Moonrise.strftime('%Y/%m/%d %H:%M:%S')

    # Calculate time of next Moonset in station timezone based on current
    # Moonrise time in UTC
    Moonset = Ob.next_setting(ephem.Moon())
    Moonset = pytz.utc.localize(Moonset.datetime())
    astroData['Moonset'][0] = Moonset.astimezone(Tz)

    # Calculate date of next full moon in UTC
    Ob.date = Now.strftime('%Y/%m/%d')
    FullMoon = ephem.next_full_moon(Ob.date)
    FullMoon = pytz.utc.localize(FullMoon.datetime())

    # Calculate date of next new moon in UTC
    NewMoon = ephem.next_new_moon(Ob.date)
    NewMoon = pytz.utc.localize(NewMoon.datetime())

    # Define Kivy label binds for next new/full moon in station time zone
    astroData['FullMoon'] = [FullMoon.astimezone(Tz).strftime('%b %d'),FullMoon]
    astroData['NewMoon'] = [NewMoon.astimezone(Tz).strftime('%b %d'),NewMoon]

    # Format sunrise/sunset labels based on date of next sunrise
    astroData = Format(astroData,Config,'Moon')
    
    # Return astroData
    return astroData
         
def Format(astroData,Config,Type):

    """ Format the sunrise/sunset labels and moonrise/moonset labels based on 
    the current time of day in the station timezone
	
	INPUTS: 
		astroData			Dictionary holding sunrise/sunset and moonrise/moonset 
                            data
		Config              Station configuration
        Type                Flag specifying whether to format sun or moon data
		
	OUTPUT: 
        astroData           Dictionary holding moonrise and moonset data
	"""

    # Calculate current time in Station timezone
    Tz = pytz.timezone(Config['Station']['Timezone'])
    Now = datetime.now(pytz.utc).astimezone(Tz)
    
    # Format Sunrise/Sunset data
    if Type == 'Sun':
        if Now.date() == astroData['Sunrise'][0].date():
            astroData['Sunrise'][1] = astroData['Sunrise'][0].strftime('%H:%M')
            astroData['Sunset'][1] = astroData['Sunset'][0].strftime('%H:%M')
        else:
            astroData['Sunrise'][1] = astroData['Sunrise'][0].strftime('%H:%M') + ' (+1)'
            astroData['Sunset'][1] = astroData['Sunset'][0].strftime('%H:%M') + ' (+1)'
            
    # Format Moonrise/Moonset data        
    elif Type == 'Moon':
    
        # Update Moonrise Kivy Label bind based on date of next moonrise
        if Now.date() == astroData['Moonrise'][0].date():
            astroData['Moonrise'][1] = astroData['Moonrise'][0].strftime('%H:%M')
        elif Now.date() < astroData['Moonrise'][0].date():
            astroData['Moonrise'][1] = astroData['Moonrise'][0].strftime('%H:%M') + ' (+1)'
        else:
            astroData['Moonrise'][1] = astroData['Moonrise'][0].strftime('%H:%M') + ' (-1)'

        # Update Moonset Kivy Label bind based on date of next moonset
        if Now.date() == astroData['Moonset'][0].date():
            astroData['Moonset'][1] = astroData['Moonset'][0].strftime('%H:%M')
        elif Now.date() < astroData['Moonset'][0].date():
            astroData['Moonset'][1] = astroData['Moonset'][0].strftime('%H:%M') + ' (+1)'
        else:
            astroData['Moonset'][1] = astroData['Moonset'][0].strftime('%H:%M') + ' (-1)'

        # Update New Moon Kivy Label bind based on date of next new moon
        if astroData['FullMoon'][1].date() == Now.date():
            astroData['FullMoon'] = ['[color=ff8837ff]Today[/color]',astroData['FullMoon'][1]]

        # Update Full Moon Kivy Label bind based on date of next full moon
        elif astroData['NewMoon'][1].date() == Now.date():
            astroData['NewMoon'] = ['[color=ff8837ff]Today[/color]',astroData['NewMoon'][1]]

    # Return dictionary holding sunrise/sunset and moonrise/moonset data
    return astroData
    
def sunTransit(astroData, Config, *largs):

    """ Calculate the sun transit between sunrise and sunset
	
	INPUTS: 
		astroData			Dictionary holding sunrise and sunset data
		Config              Station configuration
		
	OUTPUT: 
        astroData           Dictionary holding moonrise and moonset data
	"""

    # Get current time in station time zone
    Tz = pytz.timezone(Config['Station']['Timezone'])
    Now = datetime.now(pytz.utc).astimezone(Tz)

    # If time is between sunrise and sun set, calculate sun
    # transit angle
    if Now >= astroData['Sunrise'][0] and Now <= astroData['Sunset'][0]:

        # Determine total length of daylight, amount of daylight
        # that has passed, and amount of daylight left
        DaylightTotal = astroData['Sunset'][0] - astroData['Sunrise'][0]
        DaylightLapsed = Now - astroData['Sunrise'][0]
        DaylightLeft = astroData['Sunset'][0] - Now

        # Determine sun transit angle
        Angle = DaylightLapsed.total_seconds() / DaylightTotal.total_seconds() * 180
        Angle = int(Angle*10)/10.0

        # Determine hours and minutes left until sunset
        hours,remainder = divmod(DaylightLeft.total_seconds(), 3600)
        minutes,seconds = divmod(remainder,60)

        # Define Kivy Label binds
        astroData['SunAngle'] = '{:.1f}'.format(Angle)
        astroData['sunEvent'] = ['Till [color=f05e40ff]Sunset[/color]','{:02.0f}'.format(hours),'{:02.0f}'.format(minutes)]

    # When not daylight, set sun transit angle to building
    # value. Define time until sunrise
    elif Now <= astroData['Sunrise'][0]:

        # Determine hours and minutes left until sunrise
        NightLeft = astroData['Sunrise'][0] - Now
        hours,remainder = divmod(NightLeft.total_seconds(), 3600)
        minutes,seconds = divmod(remainder,60)

        # Define Kivy Label binds
        astroData['SunAngle'] = '-'
        astroData['sunEvent'] = ['Till [color=f0b240ff]Sunrise[/color]','{:02.0f}'.format(hours),'{:02.0f}'.format(minutes)]

    # Return dictionary containing sun transit data
    return astroData
    
def moonPhase(astroData, Config, *largs):

    """ Calculate the moon phase for the current time in station timezone
	
	INPUTS: 
		astroData			Dictionary holding moonrise and moonset data
		Config              Station configuration
		
	OUTPUT: 
        astroData           Dictionary holding moonrise and moonset data
	"""

    # Define current time and date in UTC and station timezone
    Tz = pytz.timezone(Config['Station']['Timezone'])
    UTC = datetime.now(pytz.utc)
    Now = UTC.astimezone(Tz)

    # Define moon phase location properties
    Ob = ephem.Observer()
    Ob.lat = str(Config['Station']['Latitude'])
    Ob.lon = str(Config['Station']['Longitude'])

    # Calculate date of next full moon in station time zone
    Ob.date = Now.strftime('%Y/%m/%d')
    FullMoon = ephem.next_full_moon(Ob.date)
    FullMoon = pytz.utc.localize(FullMoon.datetime())
    FullMoon = FullMoon.astimezone(Tz)

    # Calculate date of next new moon in station time zone
    NewMoon = ephem.next_new_moon(Ob.date)
    NewMoon = pytz.utc.localize(NewMoon.datetime())
    NewMoon = NewMoon.astimezone(Tz)

    # Calculate phase of moon
    Moon = ephem.Moon()
    Moon.compute(UTC.strftime('%Y/%m/%d %H:%M:%S'))

    # Define Moon phase icon
    if FullMoon < NewMoon:
        PhaseIcon = 'Waxing_' + '{:.0f}'.format(Moon.phase)
    elif NewMoon < FullMoon:
        PhaseIcon = 'Waning_' + '{:.0f}'.format(Moon.phase)

    # Define Moon phase text
    if astroData['NewMoon'] == '[color=ff8837ff]Today[/color]':
        PhaseTxt = 'New Moon'
    elif astroData['FullMoon'] == '[color=ff8837ff]Today[/color]':
        PhaseTxt = 'Full Moon'
    elif FullMoon < NewMoon and Moon.phase < 49:
        PhaseTxt = 'Waxing crescent'
    elif FullMoon < NewMoon and 49 <= Moon.phase <= 51:
        PhaseTxt = 'First Quarter'
    elif FullMoon < NewMoon and Moon.phase > 51:
        PhaseTxt = 'Waxing gibbous'
    elif NewMoon < FullMoon and Moon.phase > 51:
        PhaseTxt = 'Waning gibbous'
    elif NewMoon < FullMoon and 49 <= Moon.phase <= 51:
        PhaseTxt = 'Last Quarter'
    elif NewMoon < FullMoon and Moon.phase < 49:
        PhaseTxt = 'Waning crescent'

    # Define Moon phase illumination
    Illumination = '{:.0f}'.format(Moon.phase)

    # Define Kivy Label binds
    astroData['Phase'] = [PhaseIcon,PhaseTxt,Illumination]
    
    # Return dictionary containing moon phase data
    return astroData
