# Imports
import numpy as np
import os
import matplotlib.pyplot as plt
import cv2
import pandas as pd
import re

# To Arparse
PATH = "C:/Users/alder/Documents/College/Job/Ferns_and_Fungi/data"  # Data Directory
CSV_FILE_NAME = "C:/Users/alder/Documents/College/Job/Ferns_and_Fungi/results/fern_data.csv"  # Output for dataframe
VERIFY_PATH =   "C:/Users/alder/Documents/College/Job/Ferns_and_Fungi/results/verify"  # Output Verification

PATH = os.path.realpath(PATH)
CSV_FILE_NAME = os.path.realpath(CSV_FILE_NAME)
VERIFY_PATH = os.path.realpath(VERIFY_PATH)

# Configuration
from configuration import parameters
COLOR_LOWER = parameters["color_lower"] 
COLOR_UPPER = parameters["color_upper"]

VISUALLY_VERIFY = parameters["visually_verify"] 

DATE_REGEX = parameters["date_regex"]
GROUP_REGEX = parameters["group_regex"]
REPLICATE_REGEX = parameters["replicate_regex"]

ID, Date, Group, Replicate, coverage_percent = [], [], [], [], []
for file in os.listdir(PATH):
    if file[-4:] == ".png":
        img_file = os.path.join(PATH, file)
        img_bgr = cv2.imread(img_file)

        # Transform each image to RGB and HSV types.
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
        
        # Gather the data
        ID.append(file)
        Date.append(re.search(DATE_REGEX, file)[1])
        Group.append(re.search(GROUP_REGEX, file)[1])
        Replicate.append(re.search(REPLICATE_REGEX, file)[1])

        # Actual thresholding + special cases
        lower = COLOR_LOWER
        upper = COLOR_UPPER
        for special_case in parameters["special_cases"]:
            if re.search(special_case[0], file)[1] == special_case[1]:
                lower = special_case[2]
                upper = special_case[3]
        green_mask = cv2.inRange(img_hsv, lower, upper)
        black_mask = cv2.inRange(img_rgb, (0,0,0), (0,0,0))

        # Calculating percent covered
        coverage_percent.append(100 * np.sum(green_mask/255) / np.sum(np.invert(black_mask)/255))
        
        # Visually Verify 
        if VISUALLY_VERIFY:
            new_file_name = file[:-4] + "_verify" + file[-4:]
            new_file_path = os.path.join(VERIFY_PATH, new_file_name)

            # This code generates three side by side pictures 
            # demonstrating what the computer sees.

            temp_img = img_rgb.copy()
            result1 = cv2.bitwise_and(temp_img, temp_img, mask=np.invert(green_mask))

            temp_img = img_rgb.copy()
            result2 = cv2.bitwise_and(temp_img, temp_img, mask=green_mask)

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
data = pd.DataFrame({"ID":ID,
                      "Date":Date,
                      "Group":Group,
                      "Replicate":Replicate,
                      "% Fern Coverage":coverage_percent})
data.to_csv(CSV_FILE_NAME, index=False)
