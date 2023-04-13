# Imports
import numpy as np
import os
import matplotlib.pyplot as plt
import cv2
import pandas as pd
import re
import argparse
# TODO: Implement warnings
# import warnings
# warnings.warn("Warning...........Message")

# Paths
parser = argparse.ArgumentParser(description="")
parser.add_argument("ImagesPath", type=str, help="Folder containing all the fern images.")
parser.add_argument("CsvPath", type=str, help="Path and name of the output csv file.")
parser.add_argument("VerifyPath", type=str, help="Folder, preferably empty, meant to contain the outputs for visual verification.")
args = parser.parse_args()

PATH = os.path.realpath(args.ImagesPath)
CSV_FILE_NAME = os.path.realpath(args.CsvPath)
VERIFY_PATH = os.path.realpath(args.VerifyPath)

# Configuration
from configuration import parameters
COLOR_LOWER = parameters["color_lower"] 
COLOR_UPPER = parameters["color_upper"]
VISUALLY_VERIFY = parameters["visually_verify"] 
COLLECTIONS = parameters["collections"]
SPECIAL_CASES = parameters["special_cases"]

data_collector = {}
for file in os.listdir(PATH):
    if file[-4:] == ".png":
        img_file = os.path.join(PATH, file)
        img_bgr = cv2.imread(img_file)

        # Transform each image to RGB and HSV types.
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
        
        # Gather the data
        for collector in COLLECTIONS:
            if collector not in data_collector:
                data_collector[collector] = []
            data_collector[collector].append(re.search(COLLECTIONS[collector], file)[1])

        # Actual thresholding + special cases
        lower = COLOR_LOWER
        upper = COLOR_UPPER
        for special_case in SPECIAL_CASES:
            if re.search(special_case[0], file)[1] == special_case[1]:
                lower = special_case[2]
                upper = special_case[3]
        green_mask = cv2.inRange(img_hsv, lower, upper)
        black_mask = cv2.inRange(img_rgb, (0,0,0), (0,0,0))

        # Calculating percent covered
        if "% Fern Coverage" not in data_collector:
            data_collector["% Fern Coverage"] = []
        data_collector["% Fern Coverage"].append(100 * np.sum(green_mask/255) / np.sum(np.invert(black_mask)/255))
        
        # Visually Verify 
        if VISUALLY_VERIFY:
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
        
        
# Convert the information into a dataframe.
data = pd.DataFrame(data_collector)
data.to_csv(CSV_FILE_NAME, index=False)
