import requests
from datetime import datetime
from datetime import date, timedelta
import math
import matplotlib.pyplot as plt
import os

# USER VARIABLES (GLOBAL)
start_date = date(2024, 5, 13)  #YYYY, MM, DD   # Start date for the data scraping
save_data_to_file = True        # Save the scraped data to a file
url_24h = "https://veenkampen.nl/data/10min_current.txt"  # URL to scrape the data from


def timestamp_from_URL(url):
    return datetime.strptime(url[-12:-4], "%Y%m%d").date()


def get_save_data(url):#MARK: get and save data
    global filename    # Create a file name with the timestamp

    if isinstance(url, str): #only one URL, not a list of URLs, 24h data
        #print ("URL is a string")

        response = requests.get(url)    # Send a GET request to the website
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")    # Get the current timestamp

        filename = f"entrie_raw_data_24h/raw_data_{timestamp}.csv"

        with open(filename, "w") as file:    # Save the scraped text into a file
            file.write(response.text)

        print(f"Scraped text saved to {filename}")

    elif isinstance(url, list): #list of URLs, not a single URL, since sowing data
        for day in url:
            filename = f"entire_raw_data_since_sowing/raw_data_since {timestamp_from_URL(day)}.csv"

            if os.path.isfile(filename):
                #print(f"File \"{filename}\" already exists.")
                continue
            else:
                response = requests.get(day)    # Send a GET request to the website
                with open(filename, "w") as file:    # Save the scraped text into a file
                    file.write(response.text)

                print(f"Scraped text saved to \"{filename}\"")

    else:
        raise ValueError("URL must be a string or a list of strings")


def compile_weather_data_avg_24h(temperature, humidity, wind_speed, solar_radiation, pressure, rain):
    class WeatherData_avg:
        def __init__(self, temperature, humidity, wind_speed, solar_radiation, pressure, rain):
            self.temperature        = temperature
            self.humidity           = humidity
            self.wind_speed         = wind_speed
            self.solar_radiation    = solar_radiation
            self.pressure           = pressure
            self.rain               = rain
    
    global weather_data_avg_24h
    weather_data_avg_24h = WeatherData_avg(temperature, humidity, wind_speed, solar_radiation, pressure, rain)


def compile_weather_data_avg_sowing(temperature, humidity, wind_speed, solar_radiation, pressure, rain):
    class WeatherData_avg_sowing:
        def __init__(self, temperature, humidity, wind_speed, solar_radiation, pressure, rain):
            self.temperature        = temperature
            self.humidity           = humidity
            self.wind_speed         = wind_speed
            self.solar_radiation    = solar_radiation
            self.pressure           = pressure
            self.rain               = rain
    
    global weather_data_avg_sowing
    weather_data_avg_sowing = WeatherData_avg_sowing(temperature, humidity, wind_speed, solar_radiation, pressure, rain)


def compile_weather_data_all(temperature, humidity, wind_speed, solar_radiation, pressure, rain, time):
    class WeatherData_all:
        def __init__(self, temperature, humidity, wind_speed, solar_radiation, pressure, rain, time):
            self.temperature        = temperature
            self.humidity           = humidity
            self.wind_speed         = wind_speed
            self.solar_radiation    = solar_radiation
            self.pressure           = pressure
            self.rain               = rain
            self.time               = time

    global weather_data_all
    weather_data_all = WeatherData_all(temperature, humidity, wind_speed, solar_radiation, pressure, rain, time)


def extract_data(filename): #MARK: Extract data from file

    temp = []
    humi = []
    wind = []
    radi = []
    pres = []
    rain = []
    time = []

    if isinstance(filename, str):
        #print ("Filename is a string")

        data = open(filename, "r")

        for line in data:
            line = line.strip()
            if line == "":  # If line is only whitespace
                continue  # Skip to the next iteration
            line = line.split(",")

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
        
        compile_weather_data_avg_24h(temp24hAverage, humi24hAverage, wind24hAverage, radi24hAverage, pres24hAverage, rain24hAverage)
        compile_weather_data_all(temp, humi, wind, radi, pres, rain, time)

    elif isinstance(filename, list):
        #print ("Filename is a list")
        temp = []
        humi = []
        wind = []
        radi = []
        pres = []
        rain = []
        time = []

        for day in filename:
            data = open(day, "r")

            for line in data:
                line = line.strip()
                if line == "":
                    continue
                line = line.split(",")
        
                temp.append (float(line[ 2]))
                humi.append (float(line[18]))
                wind.append (float(line[38]))
                radi.append (float(line[19]))
                pres.append (float(line[32]))
                rain.append (float(line[29]))
                time.append (line[1])
            
            tempSowingAverage = sum(temp) / len(temp)
            humiSowingAverage = sum(humi) / len(humi)
            windSowingAverage = sum(wind) / len(wind)
            radiSowingAverage = sum(radi) / len(radi)
            presSowingAverage = sum(pres) / len(pres)
            rainSowingAverage = sum(rain) / len(rain)

            data.close()

            compile_weather_data_avg_sowing(tempSowingAverage, humiSowingAverage, windSowingAverage, radiSowingAverage, presSowingAverage, rainSowingAverage)
            #compile_weather_data_all(temp, humi, wind, radi, pres, rain, time)


    else:
        raise ValueError("Filename must be a string or a list of strings")


def calc_PET(weather_data):
    T_mean   = weather_data.temperature      # Mean temperature in degrees Celsius
    R_s      = weather_data.solar_radiation  # Solar radiation in MJ/m²/day
    u_2      = weather_data.wind_speed       # Wind speed at 2 meters in m/s
    DELTA    = 4098 * (0.6108 * math.exp((17.27 * T_mean) / (T_mean + 237.3))) / ((T_mean + 237.3) ** 2) # Slope of the saturation vapor pressure-temperature curve in kPa/°C
    p        = weather_data.pressure         # Atmospheric pressure in kPa
    y        = (1.013**-3 * p) / 0.622               # Psychrometric constant in kPa/°C
    DT       = DELTA / (DELTA + y * (1 + 0.34 * u_2))# Slope of the vapor pressure-temperature curve in kPa/°C
    PT       = y/(DELTA+y*(1+0.34*u_2))              # Psychrometric constant in kPa/°C
    TT       = 900/(T_mean + 273.3)*u_2              # Temperature term in kPa/°C
    e_s      = 0.6108 * math.exp((17.27 * T_mean) / (T_mean + 237.3)) # Saturation vapor pressure in kPa
    e_a      = e_s * (weather_data.humidity/100)  # Actual vapor pressure in kPa
    dr       = 1 + 0.033 * math.cos((2 * math.pi) / 365 * datetime.now().timetuple().tm_yday) # Inverse relative distance Earth-Sun
    delta    = 0.409 * math.sin((2 * math.pi) / 365 * datetime.now().timetuple().tm_yday - 1.39) # Solar declination in radians
    lat_rad  = math.radians(51.989)                  #phi
    w_s      = math.acos(-math.tan(lat_rad) * math.tan(delta)) # Sunset hour angle in radians
    R_a      = 24 * 60 / math.pi * 0.082 * dr * (w_s * math.sin(lat_rad) * math.sin(delta) + math.cos(lat_rad) * math.cos(delta) * math.sin(w_s)) # Extraterrestrial radiation in MJ/m²/day
    R_so     = (0.75 + 2 * 10**-5 * 9.5) * R_a       # Clear-sky solar radiation in MJ/m²/day
    R_ns     = (1 - 0.23) * R_s                      # Net solar radiation in MJ/m²/day
    R_nl     = 4.903e-9 * (T_mean+273.16)**4 * (0.34-0.14*math.sqrt(e_a)) * (1.35 * R_s / R_so - 0.35) 
    R_n      = R_ns - R_nl                           # Net radiation in MJ/m²/day
    R_ng     = R_n * 0.408                           # Net radiation in MJ/m²/day
    ET_rad   = DT * R_ng                             # Radiation term in mm/day
    ET_wind  = PT * TT * (e_s - e_a)                 # Wind term in mm/day
    
    global ET_0
    ET_0    = ET_rad + ET_wind                  # Potential evapotranspiration in mm/day

    #print("T_mean:\t", round(T_mean, 3), "C\nRs:\t", round(R_s, 3), "MJ/m²/day\nu2:\t", round(u_2, 3), "m/s\nDELTA:\t", round(DELTA, 3), "kPa/°C\np:\t", round(p, 3), "kPa\ny:\t", round(y, 3), "kPa/°C\nDT:\t", round(DT, 3), "kPa/°C\nPT:\t", round(PT, 3), "kPa/°C\nTT:\t", round(TT, 3), "kPa/°C\nes:\t", round(e_s, 3), "kPa\nea:\t", round(e_a, 3), "kPa\ndr:\t", round(dr, 3), "\ndelta:\t", round(delta, 3), "\nlat_rad:", round(lat_rad, 3), "\nws:\t", round(w_s, 3), "\nRa:\t", round(R_a, 3), "MJ/m²/day\nRso:\t", round(R_so, 3), "MJ/m²/day\nRns:\t", round(R_ns, 3), "MJ/m²/day\nRnl:\t", round(R_nl, 3), "MJ/m²/day\nRn:\t", round(R_n, 3), "MJ/m²/day\nR_ng:\t", round(R_ng, 3), "MJ/m²/day\nET_rad:\t", round(ET_rad, 3), "mm/day\nET_wind:", round(ET_wind, 3), "mm/day\nET_0:\t", round(ET_0, 3), "mm/day")

    return ET_0


def construct_filename(year, month, day): #MARK: List of URLs
    return f"https://veenkampen.nl/data/{year:04d}/{month:02d}/10min_{year:04d}{month:02d}{day:02d}.txt"


def get_URLs(start_date):
    yesterday = date.today() - timedelta(days=1)
    filenames = []
    current_date = start_date

    while current_date <= yesterday:
        filenames.append(construct_filename(current_date.year, current_date.month, current_date.day))
        current_date += timedelta(days=1)

    return filenames


def file_names(): #MARK:Filenames
    directory = "entire_raw_data_since_sowing/"  # Replace with the actual directory path
    filenames = []

    for filename in os.listdir(directory):
        if filename.endswith(".csv"):
            filenames.append(os.path.join(directory, filename))

    #print (filenames)
    return filenames


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

def calc_water_deficit(weather_data):
    water_content = 0
    water_deficit = water_content + (ET_0 - weather_data.rain)
    return water_deficit




if __name__ == "__main__":
    get_save_data(url_24h)
    extract_data(filename)

    print ("\n24H REPORT:")
    print ("Potential evapotranspiration:\t",calc_PET(weather_data_avg_24h), "mm/day")
    print ("Water deficit:\t\t\t", calc_water_deficit(weather_data_avg_24h), "mm/day\n")
    #print (weather_data_avg_24h.temperature, weather_data_avg_24h.humidity, weather_data_avg_24h.wind_speed, weather_data_avg_24h.solar_radiation, weather_data_avg_24h.pressure, weather_data_avg_24h.rain)


    get_save_data(get_URLs(start_date)) #calls get_save_data with a list of URLs, since sowing the date
    extract_data(file_names())
    
    print ("SINCE SOWING REPORT (untill last midnight):")
    print ("Acumulative potential evapotranspiration:\t",calc_PET(weather_data_avg_sowing), "mm/day")
    print ("Acumulative water deficit:\t\t\t", calc_water_deficit(weather_data_avg_sowing), "mm/day\n")


    #visulize_data()


    print("Job done!")