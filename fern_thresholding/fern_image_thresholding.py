# Imports
import numpy as np
import os
import matplotlib.pyplot as plt
import cv2
import pandas as pd
import re
import argparse
import warnings

# Configuration
from configuration import parameters

def collect_data(color_lower, color_upper, collections, special_cases, visually_verify):
    """
    Args:
        color_lower, color_upper : The default lower and upper color thresholds. 
            Format is (#,#,#)
        collections : The columns to collect from the file name. 
            Format is {column_name : regex with 1 capturing group, ...}
        special_cases : The cases to use a differen lower and upper threshold for.
            Format is [(regex with 1 capturing group, what that capturing group should equal, new lower, new upper), ...]
        visually_verify : The boolean for if you want to visually confirm that the computer is seeing what it should be.
                          Very useful for manually tuning the color_lower, color_upper, and special cases.
    """
    data_collector = {}
    for file in os.listdir(PATH):
        if file[-4:] == ".png":
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

            # Actual thresholding + special cases
            lower = color_lower
            upper = color_upper
            special = False
            for special_case in special_cases:
                if re.search(special_case[0], file)[1] == special_case[1]:
                    if special:
                        warnings.warn("\n\nWarning...........You have multiple special cases that can apply to" +
                                      file + " The top most special case will be applied.\n")
                    else:
                        special=True
                        lower = special_case[2]
                        upper = special_case[3]

            green_mask = cv2.inRange(img_hsv, lower, upper)
            black_mask = cv2.inRange(img_rgb, (0,0,0), (0,0,0))

            # Calculating percent covered
            if "% Fern Coverage" not in data_collector:
                data_collector["% Fern Coverage"] = []
            data_collector["% Fern Coverage"].append(100 * np.sum(green_mask/255) / np.sum(np.invert(black_mask)/255))

            # Visually Verify 
            if visually_verify:
                verify_visually(file, img_rgb, green_mask)
                
    return data_collector

def verify_visually(file, img_rgb, green_mask):
    new_file_name = file[:-4] + "_verify" + file[-4:]
    new_file_path = os.path.join(VERIFY_PATH, new_file_name)

    # This code generates three side by side pictures 
    # demonstrating what the computer sees.
    result1 = cv2.bitwise_and(img_rgb, img_rgb, mask=np.invert(green_mask))
    result2 = cv2.bitwise_and(img_rgb, img_rgb, mask=green_mask)

    fig, axs = plt.subplots(1, 3, figsize=(15,5))
    axs[0].imshow(img_rgb)
    axs[1].imshow(result1)
    axs[2].imshow(result2)
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
    args = parser.parse_args()
    
    # Globals
    PATH = os.path.realpath(args.ImagesPath)
    CSV_FILE_NAME = os.path.realpath(args.CsvPath)
    VERIFY_PATH = os.path.realpath(args.VerifyPath)
    
    # Convert the information into a dataframe.
    data = pd.DataFrame(collect_data(**parameters))
    data.to_csv(CSV_FILE_NAME, index=False) 
