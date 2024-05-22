import requests
from datetime import datetime
import math


def get_save_data(url):
    
    response = requests.get(url)    # Send a GET request to the website

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")    # Get the current timestamp

    # Create a file name with the timestamp
    global filename
    filename = f"entrie_raw_data_24h/scraped_text_{timestamp}.csv"

    with open(filename, "w") as file:    # Save the scraped text into a file
        file.write(response.text)

    print(f"Scraped text saved to {filename}")


def compile_to_class(temperature, humidity, wind_speed, solar_radiation, pressure, rain):
    class WeatherData:
        def __init__(self, temperature, humidity, wind_speed, solar_radiation, pressure, rain):
            self.temperature = temperature
            self.humidity = humidity
            self.wind_speed = wind_speed
            self.solar_radiation = solar_radiation
            self.pressure = pressure
            self.rain = rain
    
    global weather_data
    weather_data = WeatherData(temperature, humidity, wind_speed, solar_radiation, pressure, rain)


def extract_data(filename):
    temp = []  # Initialize temp as an empty list
    humi = []  # Initialize humi as an empty list
    wind = []  # Initialize wind as an empty list
    radi = []  # Initialize radi as an empty list
    pres = []  # Initialize pres as an empty list
    rain = []  # Initialize rain as an empty list
    
    data = open(filename, "r")

    for line in data:
        line = line.strip()
        if line == "":  # If line is only whitespace
            continue  # Skip to the next iteration
        line = line.split(",")



        #print ("Line: ",line)
        temp.append (float(line[ 2]))
        humi.append (float(line[18]))
        wind.append (float(line[33]))
        radi.append (float(line[19]))
        pres.append (float(line[32]))
        rain.append (float(line[29]))
    
    temp24hAverage = sum(temp) / len(temp)
    humi24hAverage = sum(humi) / len(humi)
    wind24hAverage = sum(wind) / len(wind)
    radi24hAverage = sum(radi) / len(radi)
    pres24hAverage = sum(pres) / len(pres)
    rain24hAverage = sum(rain) / len(rain)

    data.close()
    
    compile_to_class(temp24hAverage, humi24hAverage, wind24hAverage, radi24hAverage, pres24hAverage, rain24hAverage)

    return

def calc_PET():
    T_mean  = weather_data.temperature      # Mean temperature in degrees Celsius
    Rs      = weather_data.solar_radiation  # Solar radiation in MJ/m²/day
    u2      = weather_data.wind_speed       # Wind speed at 2 meters in m/s
    DELTA   = 4098 * (0.6108 * math.exp((17.27 * T_mean) / (T_mean + 237.3))) / ((T_mean + 237.3) ** 2) # Slope of the saturation vapor pressure-temperature curve in kPa/°C
    p       = weather_data.pressure         # Atmospheric pressure in kPa
    y       = (1.013**-3 * p) / 0.622       # Psychrometric constant in kPa/°C
    DT      = DELTA / (DELTA + y * (1 + 0.34 * u2)) # Slope of the vapor pressure-temperature curve in kPa/°C
    PT      = y/(DELTA+y*(1+0.34*u2))       # Psychrometric constant in kPa/°C
    TT      = 900/(T_mean + 273.3)*u2       # Temperature term in kPa/°C
    es      = 0.6108 * math.exp((17.27 * T_mean) / (T_mean + 237.3)) # Saturation vapor pressure in kPa
    ea      = es * (weather_data.humidity/100) # Actual vapor pressure in kPa
    dr      = 1 + 0.033 * math.cos((2 * math.pi) / 365 * datetime.now().timetuple().tm_yday) # Inverse relative distance Earth-Sun
    delta   = 0.409 * math.sin((2 * math.pi) / 365 * datetime.now().timetuple().tm_yday - 1.39) # Solar declination in radians
    lat_rad = math.radians(51.989)          #phi
    ws      = math.acos(-math.tan(lat_rad) * math.tan(delta)) # Sunset hour angle in radians
    Ra      = 24 * 60 / math.pi * 0.082 * dr * (ws * math.sin(lat_rad) * math.sin(delta) + math.cos(lat_rad) * math.cos(delta) * math.sin(ws)) # Extraterrestrial radiation in MJ/m²/day
    Rso     = (0.75 + 2 * 10**-5 * 9.5) * Ra# Clear-sky solar radiation in MJ/m²/day
    Rns     = (1 - 0.23) * Rs               # Net solar radiation in MJ/m²/day
    Rnl     = (T_mean+273.16)**4 * (0.34-0.14*math.sqrt(ea)) * (1.35 * Rs / Rso - 0.35) # Net outgoing longwave radiation in MJ/m²/day
    Rn      = Rns - Rnl                     # Net radiation in MJ/m²/day
    R_ng    = Rn * 0.408                    # Net radiation in MJ/m²/day
    ET_rad  = DT * R_ng                     # Radiation term in mm/day
    ET_wind = PT * TT * (es - ea)           # Wind term in mm/day
    ET_0    = ET_rad + ET_wind              # Potential evapotranspiration in mm/day

    #print("T_mean:\t", T_mean, "\nRs:\t", Rs, "\nu2:\t", u2, "\nDELTA:\t", DELTA, "\np:\t", p, "\ny:\t", y, "\nDT:\t", DT, "\nPT:\t", PT, "\nTT:\t", TT, "\nes:\t", es, "\nea:\t", ea, "\ndr:\t", dr, "\ndelta:\t", delta, "\nlat_rad:", lat_rad, "\nws:\t", ws, "\nRa:\t", Ra, "\nRso:\t", Rso, "\nRns:\t", Rns, "\nRnl:\t", Rnl, "\nRn:\t", Rn, "\nR_ng:\t", R_ng, "\nET_rad:\t", ET_rad, "\nET_wind:", ET_wind, "\nET_0:\t", ET_0)

    return ET_0


if __name__ == "__main__":
    get_save_data("https://veenkampen.nl/data/10min_current.txt")
    extract_data(filename)
    #print (weather_data.temperature, weather_data.humidity, weather_data.wind_speed, weather_data.solar_radiation, weather_data.pressure, weather_data.rain)
    print ("Potential evapotranspiration: ",calc_PET(), "mm/day")
    
    
    print("Job done!")
