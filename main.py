import requests
from datetime import datetime
from datetime import date, timedelta
import math
import matplotlib.pyplot as plt
import os
import json



# Load data from JSON file
with open('core_variables.json', 'r') as file:
    data = json.load(file)

# USER VARIABLES from json file
start_date      = datetime.strptime(data['start_date'], "%Y-%m-%d").date()
m2_irrigation_1 = data['m2_irrigation_1']
m2_irrigation_2 = data['m2_irrigation_2']
m2_irrigation_3 = data['m2_irrigation_3']
latitude        = data['latitude']                            # Latitude of the location in degrees (decimal)

# SYSTEM VARIABLES (GLOBAL)
overall_area = m2_irrigation_1 + m2_irrigation_2 + m2_irrigation_3
days_since_sowing = (datetime.now().date() - start_date).days
url_24h = "https://veenkampen.nl/data/10min_current.txt"  # URL to scrape the data from


def timestamp_from_URL(url):
    return datetime.strptime(url[-12:-4], "%Y%m%d").date()


def get_save_data(url):                             #MARK: get and save data
    global filename_since_sowing                    # Create a file name with the timestamp
    global filename_24h

    if isinstance(url, str):                        #only one URL, not a list of URLs, 24h data
        response = requests.get(url)                # Send a GET request to the website
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")    # Get the current timestamp

        filename_24h = f"entrie_raw_data_24h/raw_data_{timestamp}.csv"

        with open(filename_24h, "w") as file:       # Save the scraped text into a file
            file.write(response.text)

        print(f"Weather data saved to {filename_24h}")

    elif isinstance(url, list):                     #list of URLs, not a single URL, since sowing data
        for day in url:
            filename_since_sowing = f"entire_raw_data_since_sowing/raw_data_since_sowing_{timestamp_from_URL(day)}.csv"

            if os.path.isfile(filename_since_sowing):
                #print(f"File \"{filename_since_sowing}\" already exists.")
                continue
            else:
                response = requests.get(day)        # Send a GET request to the website
                with open(filename_since_sowing, "w") as file:   # Save the scraped text into a file
                    file.write(response.text)

                print(f"Weather data saved to \"{filename_since_sowing}\"")

    else:
        raise ValueError("URL must be a string or a list of strings")


def compile_weather_data_avg_24h(temperature, humidity, wind_speed, solar_radiation, pressure, rain): #MARK: Class Def
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


def extract_data(filename):                         #MARK: Extract data from file

    temp, humi, wind, radi, pres, rain, time = [], [], [], [], [], [], []

    if isinstance(filename, str):                   # If the data is from a single file (daily data)

        data = open(filename, "r")

        for line in data:
            line = line.strip()
            if line == "":                          # If line is only whitespace
                continue                            # Skip to the next iteration
            line = line.split(",")

            temp.append (float(line[ 2]))
            humi.append (float(line[18]))
            wind.append (float(line[38]))
            radi.append (float(line[19]))
            pres.append (float(line[32]))
            rain.append (float(line[29]))
            time.append (      line[ 1])
        
        data.close()   
        
        temp24hAverage = sum(temp) / len(temp)
        humi24hAverage = sum(humi) / len(humi)
        wind24hAverage = sum(wind) / len(wind)
        radi24hAverage = sum(radi) / len(radi)
        pres24hAverage = sum(pres) / len(pres)
        rain24hAverage = sum(rain)

        
        
        compile_weather_data_avg_24h(temp24hAverage, humi24hAverage, wind24hAverage, radi24hAverage, pres24hAverage, rain24hAverage)
        compile_weather_data_all(temp, humi, wind, radi, pres, rain, time)

    elif isinstance(filename, list):                # If the data is from multiple files (since sowing data)
        
        temp, humi, wind, radi, pres, rain, time = [], [], [], [], [], [], []

        for day in filename:                        # Data from date of sowing until last midnight
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
            
            data.close()


        timestamp = "00:10"
        line_number_0_10 = 0
        with open(filename_24h, 'r') as data_24h:
            for line in data_24h:
                line_number_0_10 += 1
                if timestamp in line:
                    break


        with open(filename_24h, 'r') as data_24h:
            lines = data_24h.readlines()[line_number_0_10-1:]
            for line in lines:
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
        rainSowingAverage = sum(rain)

        compile_weather_data_avg_sowing(tempSowingAverage, humiSowingAverage, windSowingAverage, radiSowingAverage, presSowingAverage, rainSowingAverage)

    else:
        raise ValueError("Filename must be a string or a list of strings")


def calc_PET(weather_data):                             #MARK: PET calculation
    T_mean   = weather_data.temperature                 # Mean temperature in degrees Celsius
    R_s      = weather_data.solar_radiation             # Solar radiation in MJ/m²/day
    u_2      = weather_data.wind_speed                  # Wind speed at 2 meters in m/s
    DELTA    = 4098 * (0.6108 * math.exp((17.27 * T_mean) / (T_mean + 237.3))) / ((T_mean + 237.3) ** 2) # Slope of the saturation vapor pressure-temperature curve in kPa/°C
    p        = weather_data.pressure                    # Atmospheric pressure in kPa
    y        = (1.013 ** -3 * p) / 0.622                # Psychrometric constant in kPa/°C
    DT       = DELTA / (DELTA + y * (1 + 0.34 * u_2))   # Slope of the vapor pressure-temperature curve in kPa/°C
    PT       = y/(DELTA + y * (1 + 0.34 * u_2))         # Psychrometric constant in kPa/°C
    TT       = 900 / (T_mean + 273.3) * u_2             # Temperature term in kPa/°C
    e_s      = 0.6108 * math.exp((17.27 * T_mean) / (T_mean + 237.3)) # Saturation vapor pressure in kPa
    e_a      = e_s * (weather_data.humidity/100)        # Actual vapor pressure in kPa
    dr       = 1 + 0.033 * math.cos((2 * math.pi) / 365 * datetime.now().timetuple().tm_yday) # Inverse relative distance Earth-Sun
    delta    = 0.409 * math.sin((2 * math.pi) / 365 * datetime.now().timetuple().tm_yday - 1.39) # Solar declination in radians
    lat_rad  = math.radians(latitude)                     #phi
    w_s      = math.acos(-math.tan(lat_rad) * math.tan(delta)) # Sunset hour angle in radians
    R_a      = 24 * 60 / math.pi * 0.082 * dr * (w_s * math.sin(lat_rad) * math.sin(delta) + math.cos(lat_rad) * math.cos(delta) * math.sin(w_s)) # Extraterrestrial radiation in MJ/m²/day
    R_so     = (0.75 + 2 * 10 ** -5 * 9.5) * R_a        # Clear-sky solar radiation in MJ/m²/day
    R_ns     = (1 - 0.23) * R_s                         # Net solar radiation in MJ/m²/day
    R_nl     = 4.903e-9 * (T_mean+273.16) ** 4 * (0.34-0.14 * math.sqrt(e_a)) * (1.35 * R_s / R_so - 0.35) # Net outgoing longwave radiation in MJ/m²/day
    R_n      = R_ns - R_nl                              # Net radiation in MJ/m²/day
    R_ng     = R_n * 0.408                              # Net radiation in MJ/m²/day
    ET_rad   = DT * R_ng                                # Radiation term in mm/day
    ET_wind  = PT * TT * (e_s - e_a)                    # Wind term in mm/day
    
    global ET_0
    ET_0    = ET_rad + ET_wind                          # Potential evapotranspiration in mm/day

    #print("T_mean:\t", round(T_mean, 3), "C\nRs:\t", round(R_s, 3), "MJ/m²/day\nu2:\t", round(u_2, 3), "m/s\nDELTA:\t", round(DELTA, 3), "kPa/°C\np:\t", round(p, 3), "kPa\ny:\t", round(y, 3), "kPa/°C\nDT:\t", round(DT, 3), "kPa/°C\nPT:\t", round(PT, 3), "kPa/°C\nTT:\t", round(TT, 3), "kPa/°C\nes:\t", round(e_s, 3), "kPa\nea:\t", round(e_a, 3), "kPa\ndr:\t", round(dr, 3), "\ndelta:\t", round(delta, 3), "\nlat_rad:", round(lat_rad, 3), "\nws:\t", round(w_s, 3), "\nRa:\t", round(R_a, 3), "MJ/m²/day\nRso:\t", round(R_so, 3), "MJ/m²/day\nRns:\t", round(R_ns, 3), "MJ/m²/day\nRnl:\t", round(R_nl, 3), "MJ/m²/day\nRn:\t", round(R_n, 3), "MJ/m²/day\nR_ng:\t", round(R_ng, 3), "MJ/m²/day\nET_rad:\t", round(ET_rad, 3), "mm/day\nET_wind:", round(ET_wind, 3), "mm/day\nET_0:\t", round(ET_0, 3), "mm/day")

    return ET_0


def construct_filename(year, month, day):           #MARK: List of URLs
    return f"https://veenkampen.nl/data/{year:04d}/{month:02d}/10min_{year:04d}{month:02d}{day:02d}.txt"


def get_URLs(start_date):
    yesterday = date.today() - timedelta(days=1)
    filenames = []
    current_date = start_date

    while current_date <= yesterday:
        filenames.append(construct_filename(current_date.year, current_date.month, current_date.day))
        current_date += timedelta(days=1)

    return filenames


def file_names():                                   # MARK:Filenames
    directory = "entire_raw_data_since_sowing/"     # Replace with the actual directory path
    filenames = []

    for filename in os.listdir(directory):
        if filename.endswith(".csv"):
            filenames.append(os.path.join(directory, filename))

    return filenames


def add_irrigation():
    irrigation_data = {}

    # Get user input for irrigation data
    irrigation_data['date'] = input("Enter the date of irrigation (YYYY-MM-DD): ")
    irrigation_data['time'] = input("Enter the time of irrigation (HH:MM): ")
    irrigation_data['amount'] = float(input("Enter the amount of water applied (in mm): "))

    # Write irrigation data to a file
    with open('irrigation_data.json', 'r+') as file:
        data = json.load(file)
        data.append(irrigation_data)
        file.seek(0)
        file.write(json.dumps(data, indent=4))
        file.truncate()

    print("Irrigation data has been recorded.")


def print_irrigation_data():
    with open('irrigation_data.json', 'r') as file:
        for line in file:
            data = json.loads(line)
            print("Date:\t", data['date'])
            print("Time:\t", data['time'])
            print("Amount:\t", data['amount'], "mm")
            print()


def change_core_variables():
    core_variables = {
        "start_date": input("Enter the start date (YYYY-MM-DD): "),
        "m2_irrigation_1": float(input("Enter the area covered by irrigation system 1 (in m²): ")),
        "m2_irrigation_2": float(input("Enter the area covered by irrigation system 2 (in m²): ")),
        "m2_irrigation_3": float(input("Enter the area covered by irrigation system 3 (in m²): ")),
        "latitude": float(input("Enter the latitude of the location (in degrees, decimal): "))
    }

    with open('core_variables.json', 'w') as file:
        json.dump(core_variables, file)

    print("Core variables have been updated and saved to core_variables.json.")


def cal_water_deficit():
    sum_irrigation = 0

    with open('irrigation_data.json', 'r') as file:
        irrigation_data = json.load(file)

    for data in irrigation_data:    # Calculate the total irrigation amount
        sum_irrigation += data['amount']

    water_deficit = (ET_0 * days_since_sowing) - weather_data_avg_sowing.rain - sum_irrigation

    return water_deficit


def visulize_last_24h():                                #MARK: Visualize data
    fig, axs = plt.subplots(3, 2, figsize=(15, 60)) # Increase the figsize to create more vertical space

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




if __name__ == "__main__":                          # MARK: Main
    
    while True:
        user_input = input("> ")
        
        if user_input == "add irrigation":
            add_irrigation()
        elif user_input == "print irrigation":
            print_irrigation_data()
        # elif user_input == "visualize data":
        #     visulize_data()
        elif user_input == "exit":
            exit()
        elif user_input == "":
            break
        elif user_input == "change core variables":
            change_core_variables()
        else:
            print("Invalid command.")

# 24h-REPORT   
    get_save_data(url_24h)
    extract_data(filename_24h)

    print ("\nLast data set update:\t\t\t\t", timestamp_from_URL(get_URLs(start_date)[-1]), weather_data_all.time[-1], "(UTC)")
    print ("Data of sowing:\t\t\t\t\t", start_date, "(", days_since_sowing, "days ago)")

    print ("\n24H REPORT:")
    print ("Potential evapotranspiration:\t\t\t", round(calc_PET(weather_data_avg_24h), 2), "mm/day")

    if weather_data_avg_24h.rain == 0:
        print ("Rainfall:\t\t\t\t\t", "na")
    else:
        print ("Rainfall:\t\t\t\t\t", round(weather_data_avg_24h.rain,2), "mm/day")

    print ("Water deficit:\t\t\t\t\t", round(ET_0 - weather_data_avg_24h.rain,2), "mm/day\n")
    #print (weather_data_avg_24h.temperature, weather_data_avg_24h.humidity, weather_data_avg_24h.wind_speed, weather_data_avg_24h.solar_radiation, weather_data_avg_24h.pressure, weather_data_avg_24h.rain)


# since sowing REPORT
    
    get_save_data(get_URLs(start_date))             #calls get_save_data with a list of URLs, since sowing the date
    extract_data(file_names())
    
    print (f"SINCE SOWING REPORT (untill {weather_data_all.time[-1]} (UTC)):")
    print ("Acumulative potential evapotranspiration:\t", round (calc_PET(weather_data_avg_sowing) * days_since_sowing,2), "mm")

    if weather_data_avg_sowing.rain == 0:
        print ("Acumulative rainfall:\t\t\t\t", "na")
    else:
        print ("Acumulative rainfall:\t\t\t\t",  round (weather_data_avg_sowing.rain,2), "mm")

    print ("Water deficit:\t\t\t\t\t",  round (cal_water_deficit(), 2), "mm\n")

    print ("IRRIGATION NEEDED (90% efficiency):")
    overall_irrigation = (cal_water_deficit() * overall_area) / 0.9
    print (f"Irrigation needed overall ({overall_area} m²):\t\t", round ((overall_irrigation), 2), "L")
    print (f"Irrigation System 1 ({m2_irrigation_1} m²):\t\t\t", round ((m2_irrigation_1/overall_area)*overall_irrigation, 2), "L")
    print (f"Irrigation System 2 ({m2_irrigation_2} m²):\t\t\t", round ((m2_irrigation_2/overall_area)*overall_irrigation, 2), "L")
    print (f"Irrigation System 3 ({m2_irrigation_3} m²):\t\t\t", round ((m2_irrigation_3/overall_area)*overall_irrigation, 2), "L\n")

    #visulize_last_24h()

    print("Job done!")