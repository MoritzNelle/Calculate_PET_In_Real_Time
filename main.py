import requests
from datetime import datetime
import math
import matplotlib.pyplot as plt


def get_save_data(url):
    
    response = requests.get(url)    # Send a GET request to the website

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")    # Get the current timestamp

    # Create a file name with the timestamp
    global filename
    filename = f"entrie_raw_data_24h/raw_data_{timestamp}.csv"

    with open(filename, "w") as file:    # Save the scraped text into a file
        file.write(response.text)

    print(f"Scraped text saved to {filename}")


def compile_weather_data_avg(temperature, humidity, wind_speed, solar_radiation, pressure, rain):
    class WeatherData_avg:
        def __init__(self, temperature, humidity, wind_speed, solar_radiation, pressure, rain):
            self.temperature = temperature
            self.humidity = humidity
            self.wind_speed = wind_speed
            self.solar_radiation = solar_radiation
            self.pressure = pressure
            self.rain = rain
    
    global weather_data_avg
    weather_data_avg = WeatherData_avg(temperature, humidity, wind_speed, solar_radiation, pressure, rain)

def compile_weather_data_all(temperature, humidity, wind_speed, solar_radiation, pressure, rain, time):
    class WeatherData_all:
        def __init__(self, temperature, humidity, wind_speed, solar_radiation, pressure, rain, time):
            self.temperature = temperature
            self.humidity = humidity
            self.wind_speed = wind_speed
            self.solar_radiation = solar_radiation
            self.pressure = pressure
            self.rain = rain
            self.time = time

    global weather_data_all
    weather_data_all = WeatherData_all(temperature, humidity, wind_speed, solar_radiation, pressure, rain, time)


def extract_data(filename):
    temp = []
    humi = []
    wind = []
    radi = []
    pres = []
    rain = []
    time = []

    data = open(filename, "r")

    for line in data:
        line = line.strip()
        if line == "":  # If line is only whitespace
            continue  # Skip to the next iteration
        line = line.split(",")



        #print ("Line: ",line)
        temp.append (float(line[ 2]))
        humi.append (float(line[18]))
        wind.append (float(line[38]))
        radi.append (float(line[19]))
        pres.append (float(line[32]))
        rain.append (float(line[29]))
        time.append (line[1])
        
    temp24hAverage = sum(temp) / len(temp)
    humi24hAverage = sum(humi) / len(humi)
    wind24hAverage = sum(wind) / len(wind)
    radi24hAverage = sum(radi) / len(radi)
    pres24hAverage = sum(pres) / len(pres)
    rain24hAverage = sum(rain) / len(rain)

    data.close()
    
    compile_weather_data_avg(temp24hAverage, humi24hAverage, wind24hAverage, radi24hAverage, pres24hAverage, rain24hAverage)
    compile_weather_data_all(temp, humi, wind, radi, pres, rain, time)

    return

def calc_PET():
    T_mean  = weather_data_avg.temperature      # Mean temperature in degrees Celsius
    R_s      = weather_data_avg.solar_radiation  # Solar radiation in MJ/m²/day
    u_2      = weather_data_avg.wind_speed       # Wind speed at 2 meters in m/s
    DELTA   = 4098 * (0.6108 * math.exp((17.27 * T_mean) / (T_mean + 237.3))) / ((T_mean + 237.3) ** 2) # Slope of the saturation vapor pressure-temperature curve in kPa/°C
    p       = weather_data_avg.pressure         # Atmospheric pressure in kPa
    y       = (1.013**-3 * p) / 0.622           # Psychrometric constant in kPa/°C
    DT      = DELTA / (DELTA + y * (1 + 0.34 * u_2)) # Slope of the vapor pressure-temperature curve in kPa/°C
    PT      = y/(DELTA+y*(1+0.34*u_2))           # Psychrometric constant in kPa/°C
    TT      = 900/(T_mean + 273.3)*u_2           # Temperature term in kPa/°C
    e_s      = 0.6108 * math.exp((17.27 * T_mean) / (T_mean + 237.3)) # Saturation vapor pressure in kPa
    e_a      = e_s * (weather_data_avg.humidity/100)  # Actual vapor pressure in kPa
    dr      = 1 + 0.033 * math.cos((2 * math.pi) / 365 * datetime.now().timetuple().tm_yday) # Inverse relative distance Earth-Sun
    delta   = 0.409 * math.sin((2 * math.pi) / 365 * datetime.now().timetuple().tm_yday - 1.39) # Solar declination in radians
    lat_rad = math.radians(51.989)              #phi
    w_s      = math.acos(-math.tan(lat_rad) * math.tan(delta)) # Sunset hour angle in radians
    R_a      = 24 * 60 / math.pi * 0.082 * dr * (w_s * math.sin(lat_rad) * math.sin(delta) + math.cos(lat_rad) * math.cos(delta) * math.sin(w_s)) # Extraterrestrial radiation in MJ/m²/day
    R_so     = (0.75 + 2 * 10**-5 * 9.5) * R_a    # Clear-sky solar radiation in MJ/m²/day
    R_ns     = (1 - 0.23) * R_s                   # Net solar radiation in MJ/m²/day
    R_nl     = 4.903e-9 * (T_mean+273.16)**4 * (0.34-0.14*math.sqrt(e_a)) * (1.35 * R_s / R_so - 0.35) 
    R_n      = R_ns - R_nl                         # Net radiation in MJ/m²/day
    R_ng    = R_n * 0.408                        # Net radiation in MJ/m²/day
    ET_rad  = DT * R_ng                         # Radiation term in mm/day
    ET_wind = PT * TT * (e_s - e_a)               # Wind term in mm/day
    
    global ET_0
    ET_0    = ET_rad + ET_wind                  # Potential evapotranspiration in mm/day

    print("T_mean:\t", round(T_mean, 3), "C\nRs:\t", round(R_s, 3), "MJ/m²/day\nu2:\t", round(u_2, 3), "m/s\nDELTA:\t", round(DELTA, 3), "kPa/°C\np:\t", round(p, 3), "kPa\ny:\t", round(y, 3), "kPa/°C\nDT:\t", round(DT, 3), "kPa/°C\nPT:\t", round(PT, 3), "kPa/°C\nTT:\t", round(TT, 3), "kPa/°C\nes:\t", round(e_s, 3), "kPa\nea:\t", round(e_a, 3), "kPa\ndr:\t", round(dr, 3), "\ndelta:\t", round(delta, 3), "\nlat_rad:", round(lat_rad, 3), "\nws:\t", round(w_s, 3), "\nRa:\t", round(R_a, 3), "MJ/m²/day\nRso:\t", round(R_so, 3), "MJ/m²/day\nRns:\t", round(R_ns, 3), "MJ/m²/day\nRnl:\t", round(R_nl, 3), "MJ/m²/day\nRn:\t", round(R_n, 3), "MJ/m²/day\nR_ng:\t", round(R_ng, 3), "MJ/m²/day\nET_rad:\t", round(ET_rad, 3), "mm/day\nET_wind:", round(ET_wind, 3), "mm/day\nET_0:\t", round(ET_0, 3), "mm/day")

    return ET_0


def visulize_data():
    fig, axs = plt.subplots(3, 2, figsize=(15, 60))  # Increase the figsize to create more vertical space

    axs[0, 0].plot(weather_data_all.time, weather_data_all.temperature, label="Temperature")
    axs[0, 0].set_title("Temperature")
    axs[0, 0].set_ylabel("Temperature (°C)")
    axs[0, 0].set_xticklabels([])

    axs[0, 1].plot(weather_data_all.time, weather_data_all.humidity, label="Humidity")
    axs[0, 1].set_title("Humidity")
    axs[0, 1].set_ylabel("Humidity (%)")
    axs[0, 1].set_xticklabels([])

    axs[1, 0].plot(weather_data_all.time, weather_data_all.wind_speed, label="Wind Speed")
    axs[1, 0].set_title("Wind Speed")
    axs[1, 0].set_ylabel("Wind Speed (m/s)")
    axs[1, 0].set_xticklabels([])

    axs[1, 1].plot(weather_data_all.time, weather_data_all.solar_radiation, label="Solar Radiation")
    axs[1, 1].set_title("Solar Radiation")
    axs[1, 1].set_ylabel("Solar Radiation (W/m²)")
    axs[1, 1].set_xticklabels([])

    axs[2, 0].plot(weather_data_all.time, weather_data_all.pressure, label="Pressure")
    axs[2, 0].set_title("Pressure")
    axs[2, 0].set_ylabel("Pressure (hPa)")
    axs[2, 0].set_xlabel("Time")

    axs[2, 1].plot(weather_data_all.time, weather_data_all.rain, label="Rain")
    axs[2, 1].set_title("Rain")
    axs[2, 1].set_xlabel("Time")
    axs[2, 1].set_ylabel("Rain (mm)")

    # Set x-axis ticks to show only 4 hour increments
    axs[0, 0].set_xticks(weather_data_all.time[::18])
    axs[0, 1].set_xticks(weather_data_all.time[::18])
    axs[1, 0].set_xticks(weather_data_all.time[::18])
    axs[1, 1].set_xticks(weather_data_all.time[::18])
    axs[2, 0].set_xticks(weather_data_all.time[::18])
    axs[2, 1].set_xticks(weather_data_all.time[::18])

    plt.show()

def calc_water_deficit():

    water_content = 0
    water_deficit = water_content + (ET_0 - weather_data_avg.rain)
    return water_deficit
    


if __name__ == "__main__":
    get_save_data("https://veenkampen.nl/data/10min_current.txt")
    extract_data(filename)
    #print (weather_data_avg.temperature, weather_data_avg.humidity, weather_data_avg.wind_speed, weather_data_avg.solar_radiation, weather_data_avg.pressure, weather_data_avg.rain)
    print ("\nPotential evapotranspiration:\t",calc_PET(), "mm/day")
    print ("Water deficit:\t\t\t", calc_water_deficit(), "mm/day\n")
    visulize_data()
    
    
    print("Job done!")