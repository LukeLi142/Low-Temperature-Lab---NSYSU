import numpy as np
import re
import os

# get last number from txt file

def get_last_number(inputfile):
    with open(inputfile, "r", encoding="utf-8", errors="ignore") as f:
        last_line = f.readlines()[-2]
        numbers = re.findall(r"[-+]?\d*\.\d+|\d+", last_line)
        last_number = float(numbers[-1])
        return last_number

# load data from txt file

def load_data(inputfile):
    data  = np.loadtxt(inputfile, comments="#")
    duration = get_last_number(inputfile)
    return data, duration

# get DC voltage from filename
def get_dc_voltage_from_filename(filename):
    match = re.search(r'HzE([+-]?\d*\.?\d+)V', filename)
    if match:
        return float(match.group(1))
    else:
        raise ValueError("DC voltage not found in filename.")
    
def get_temperature_from_filename(filename):
    match = re.search(r'sample(\d+)K', filename)
    if match:
        return int(match.group(1))
    else:
        raise ValueError("Temperature not found in filename.")