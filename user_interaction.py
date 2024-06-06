from datetime import datetime
from datetime import date, timedelta
import json


def add_irrigation():
    
    with open('core_variables.json', 'r') as file:
        data = json.load(file)
        start_date  = datetime.strptime(data['start_date'], "%Y-%m-%d").date()

    irrigation_data = {}

    # Get user input for irrigation data
    irrigation_data['date'] = input("\nEnter the date of irrigation (YYYY-MM-DD): ")
    irrigation_data['time'] = input("Enter the time of irrigation (HH:MM): ")
    amount = input("Enter the amount of water applied (in mm): ")
    
    try:
        sowing_date = datetime.strptime(start_date.strftime("%Y-%m-%d"), "%Y-%m-%d").date()
        irrigation_date = datetime.strptime(irrigation_data['date'], "%Y-%m-%d").date()
        irrigation_time = datetime.strptime(irrigation_data['time'], "%H:%M").time()
        current_datetime = datetime.now().date()
    
        if irrigation_date < sowing_date or irrigation_date > current_datetime:
            print("Invalid input. Please enter a date between the sowing date and today.\n")
            return
    
        if irrigation_date == sowing_date and irrigation_time < datetime.now().time():
            print("Invalid input. Please enter a time after the current time.\n")
            return
    
        irrigation_data['amount'] = float(amount)
    except ValueError:
        print("Invalid input. Please enter a valid date, time, and amount.\n")
        return
    
    # Write irrigation data to a file
    with open('irrigation_data.json', 'r+') as file:
        data = json.load(file)
        data.append(irrigation_data)
        file.seek(0)
        file.write(json.dumps(data, indent=4))
        file.truncate()

    print("Irrigation data has been recorded.\n")


def print_irrigation_data():
    with open('irrigation_data.json', 'r') as file:
        try:
            data = json.load(file)  # load the entire JSON file
            print("\nSaved irrigations:")
            for item in data:
                print(f"{item['date']} {item['time']}: {item['amount']} mm")
        except json.JSONDecodeError:
            print("Invalid JSON file")
    print("")  # Add a newline after printing the data


def change_core_variables():
    core_variables = {
        "start_date": input("Enter the start date (YYYY-MM-DD): "),
        "m2_irrigation_1":  float(input("Enter the area covered by irrigation system 1 (in m²): "   )),
        "m2_irrigation_2":  float(input("Enter the area covered by irrigation system 2 (in m²): "   )),
        "m2_irrigation_3":  float(input("Enter the area covered by irrigation system 3 (in m²): "   )),
        "latitude":         float(input("Enter the latitude of the location (in degrees, decimal): ")),
        "field_capacity":   float(input("Enter the field capacity of the soil (in mm/mm): "         ))
    }

    with open('core_variables.json', 'w') as file:
        json.dump(core_variables, file)

    print("Core variables have been updated and saved to core_variables.json.")


def delete_irrigation():

    with open('irrigation_data.json', 'r') as file:
        try:
            data = json.load(file)  # load the entire JSON file
        except json.JSONDecodeError:
            print("Invalid JSON file")
            return

    print("\nSaved irrigations:")
    for i, item in enumerate(data):
        print(f"{i + 1}. {item['date']} {item['time']}: {item['amount']} mm")

    try:
        index = int(input("Enter the index of the irrigation data you want to delete: ")) - 1
        del data[index]
    except (ValueError, IndexError):
        print("Invalid input. Please enter a valid index.\n")
        return

    with open('irrigation_data.json', 'w') as file:
        json.dump(data, file, indent=4)

    print("Irrigation data has been deleted.\n")