import requests
from datetime import datetime


temp24hAverage = None
humi24hAverage = None
wind24hAverage = None
radi24hAverage = None
pres24hAverage = None


def get_save_data(url):
    
    response = requests.get(url)    # Send a GET request to the website

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")    # Get the current timestamp

    # Create a file name with the timestamp
    global filename
    filename = f"entrie_raw_data_24h/scraped_text_{timestamp}.csv"

    with open(filename, "w") as file:    # Save the scraped text into a file
        file.write(response.text)

    print(f"Scraped text saved to {filename}")

def extract_data(filename):
    values = []
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
    
    return temp24hAverage, humi24hAverage, wind24hAverage, radi24hAverage, pres24hAverage, rain24hAverage




if __name__ == "__main__":
    get_save_data("https://veenkampen.nl/data/10min_current.txt")
    extract_data(filename)
    print (extract_data(filename))    
    
    print("Job done!")
