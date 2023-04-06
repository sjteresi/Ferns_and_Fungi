# Imports
import numpy as np
import os
import matplotlib.pyplot as plt
import cv2
import pandas as pd
import re

# Globals
PATH = "C:/Users/alder/Documents/Coding/New Fern Code/MariaFernPhotos"  # Data Directory
COLOR_LOWER = (20, 40, 40)  # Lower hsv threshold
COLOR_UPPER = (70, 255, 255) # Upper hsv threshold
VISUALLY_VERIFY = True  # If you want to verify the code is working
VERIFY_PATH = "C:/Users/alder/Documents/Coding/New Fern Code/Verify"  # Output Verification
CSV_FILE_NAME = "fern_data.csv"  # Output for dataframe
COLOR_LOWER2 = (20, 80, 60)  # Threshold that is HARD CODED for the 5wk set.

# The code uses the first captured section of regex 
DATE_REGEX = "^([^_]*)_"
GROUP_REGEX = "_(.*)[_-]"
REPLICATE_REGEX = "([0-9]*)\.png"

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

        # Hardcoded Special Case
        if Date[-1] == "5wk":
            green_mask = cv2.inRange(img_hsv, COLOR_LOWER2, COLOR_UPPER)
        else:
            green_mask = cv2.inRange(img_hsv, COLOR_LOWER, COLOR_UPPER)
        black_mask = cv2.inRange(img_rgb, (0,0,0), (0,0,0))

        
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