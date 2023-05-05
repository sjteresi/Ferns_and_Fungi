"""
Author: Alder Fulton
Usage: fern_image_threshold.py /imagespath /csvpath.csv /verifypath /configurationpath.ini

This python script thresholds a region in the images given and then normalizes based on another region.
The goal is to find the area of the region.
"""

# Imports
import numpy as np
import os
import matplotlib.pyplot as plt
import cv2
import pandas as pd
import re
import argparse

# Configuration
import configparser
from ast import literal_eval

def parse_configuration():
    """
    Parses the configuration file into a single dictionary to be used as key word arguments (kwargs)
    for the function "collect_data"
    """
    config = configparser.ConfigParser()
    config.read(CONFIGURATION)
    
    cases = []
    for case in config.items("Cases"):
        cases.append(literal_eval(case[1]))
        
    parameters = {
        "visually_verify": config.getboolean('Output', 'visually_verify'),
        "collections": dict(config.items('Collections')),
        "cases": cases,
        "file_extension": config.get("Input", "file_extension"),
        "capturing_name": config.get("Output", "capturing_name"),
        "normalize_unit": config.get("Output", "normalize_unit")
    }
    return parameters

def collect_data(cases, collections, visually_verify, file_extension, capturing_name, normalize_unit):
    """
    Args:
        cases: A list of dictionaries of the following structure.
            {'regex': '(regex with 1 capturing group)',
             'equals': 'what the regex should equal',
             'color_lower': (#,#,#) the lower bound of the hsv colors to pick out,
             'color_upper': (#,#,#) the upper bound of the hsv colors to pick out,
             'normalize_lower': (#,#,#) the lower hsv bound for the normalizing region,
             'normalize_upper': (#,#,#) the upper hsv bound for the normalizing region,
             'normalize_area' : # the area of the normalizing region.}
        collections: The columns to collect from the file name. 
            Format is {column_name : regex with 1 capturing group, ...}
        visually_verify : The boolean for if you want to visually confirm that the computer is seeing what it should be.
            Very useful for manually tuning the color_lower, color_upper.
        file_extension : The file extension for the images.
        capturing_name : The name of the column that has the substantive data.
     Output:
        A dictionary containing all of the values from collections as well as the coverage value in terms of the normalizing region.
        This dictionary is intended to be converted into a pandas dataframe.
    """
    capturing_name += " (" + normalize_unit + ")"
    data_collector = {}
    for file in os.listdir(PATH):
        if file[-len(file_extension):] == file_extension:
            img_file = os.path.join(PATH, file)
            img_bgr = cv2.imread(img_file)
            
            # Transform each image to RGB and HSV types.
            img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
            img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
            
            # Gather the data
            for collector in collections:
                if collector not in data_collector:
                    data_collector[collector] = []
                data_collector[collector].append(re.search(collections[collector], file)[1])
            
            # Determine which case is applied.
            c = cases[0]  # The first is the default, and is overwritten by future cases.
            for case in cases[1:]:
                if re.search(case["regex"], file)[1] == case["equals"]:
                    c = case
                    
            # Create masks
            collected_mask, normalize_mask = get_masks(img_hsv, c["color_lower"], c["color_upper"],
                                                       c["normalize_lower"], c["normalize_upper"],)
            
            # Calculate coverage
            if capturing_name not in data_collector:
                data_collector[capturing_name] = []
            data_collector[capturing_name].append(np.sum(collected_mask) / np.sum(normalize_mask) * c["normalize_area"])
               
            # Visually Verify 
            if visually_verify:
                verify_visually(file, img_rgb, collected_mask, normalize_mask, file_extension)
                
    return data_collector
    
def get_masks(img, color_lower, color_upper, normalize_lower, normalize_upper):
    """
    Uses the lower and upper thresholds to find the regions for both the capturing region
    and the normalizing region.
    """
    collected_mask = cv2.inRange(img, color_lower, color_upper)
    normalize_mask = cv2.inRange(img, normalize_lower, normalize_upper)
    return (collected_mask, normalize_mask)
    
def verify_visually(file, img_rgb, captured_mask, normalize_mask, file_extension):
    """
    This code generates three side by side pictures demonstrating what the computer sees.
    """
    new_file_name = file[:-len(file_extension)] + "_verify" + file_extension
    new_file_path = os.path.join(VERIFY_PATH, new_file_name)

    result1 = cv2.bitwise_and(img_rgb, img_rgb, mask=np.invert(captured_mask))
    result2 = cv2.bitwise_and(img_rgb, img_rgb, mask=captured_mask)

    fig, axs = plt.subplots(1, 4, figsize=(20,5))
    axs[0].set_title("Original Image")
    axs[0].imshow(img_rgb)
    axs[1].set_title("Capturing Region")
    axs[1].imshow(result1)
    axs[2].set_title("Capturing Region")
    axs[2].imshow(result2)
    axs[3].set_title("Normalizing Region")
    axs[3].imshow(normalize_mask, cmap="gray")
    for ax in axs:
        ax.xaxis.set_visible(False)
        ax.yaxis.set_visible(False)
    fig.savefig(new_file_path, dpi=300)
    plt.close(fig)
    
if __name__ == "__main__":
    # Paths
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("ImagesPath", type=str, help="Folder containing all the fern images.")
    parser.add_argument("CsvPath", type=str, help="Path and name of the output csv file.")
    parser.add_argument("VerifyPath", type=str, help="Folder, preferably empty, meant to contain the outputs for visual verification.")
    parser.add_argument("Configuration", type=str, help="Path to the configuration file.")
    args = parser.parse_args()
    
    # Globals
    PATH = os.path.realpath(args.ImagesPath)
    CSV_FILE_NAME = os.path.realpath(args.CsvPath)
    VERIFY_PATH = os.path.realpath(args.VerifyPath)
    CONFIGURATION = os.path.realpath(args.Configuration)
    
    # Configuration
    parameters = parse_configuration()
    
    # Convert the information into a dataframe.
    data = pd.DataFrame(collect_data(**parameters))
    data.to_csv(CSV_FILE_NAME, index=False) 

    