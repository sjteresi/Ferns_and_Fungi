# Readme

## Fern Thresholding

### Running the code

Code format:

`python fern_image_thresholding.py datapath csv_output_path.csv verify_path configuration_path.ini`

* `fern_image_thresholding.py`: Python file that runs the code.
* `datapath`: The folder containing the images. The code runs on every file in the folder ending with `Input.file_extension` from the configuration file.
* `csv_output_path.csv`: This is the path and filename of the csv file to save the results in.
* `verify_path`: This is the folder where verification images will be saved. The purpose is to add a manual check to make sure the code is doing what it is supposed to. Each image the code runs on the image four times with different filters on it.
    * The original image. This is mainly to compare with the other the other filters.
    * The capturing region. The capturing region here is shown as black in the image.
        * Anything that was already black will still be black. That doesn't mean it will be captured.
        * The purpose is to look for what isn't captured (aka isn't black) but should be. If there is more than a little that should be captured that isn't, consider lower the lower threshold in the configuration file or increasing the upper bound.
    * The capturing region again - but inverted.
        * Anything that isn't captured will show as black.
        * The purpose is to look specifically for what is captured that shouldn't be. If there is a substantial amount of the captured region that isn't what you wanted, you should either raise the lower threshold or lower the upper threshold.
    * The normalizing region. This is the region of known area. It is used to calculate the area of the captured region.
        * In this case, the normalizing region is the entire petri dish, so the area is set to 100 and the units are set to %.
* `configuration_path.ini`: This is the path to the configuration file. This file contains a lot more parameters for how the code will run, and can account for any number of cases.

### Configuration File

#### Cases

The most vital part of the configuration file is the cases section. In this section, all of the area based and color detection parameters are stored.
* **The Default Case**
    * The default case is the very first case in the configuration file, regardless of name. If you have case1 = {...} as the first line, that will be considered the default case.
    * The default case uses the "regex" or "equals" dictionary keys.
* **Increasing Priority**
    * Each case you go down in the configuration file has a higher priority than the one before it. That means that if the cases are ordered default, case1, case2, case3, then case1 will overwrite default, case2 will overwrite case1, etc.
    * The final case that is chosen will be the lowest one in the configuration file where the search equals the string.
* **color_lower, color_upper**
    * The two arguments to find the capturing region for any case is the color_lower and the color_upper arguments.
        * A larger range in between these two values corresponds with an increased region picked out of the picture.
        * The colors are in HSV. The first value, Hue, roughly corresponds with the family of color (green, yellow, etc.) The Saturation roughly corresponds with the intensity or purity of that color. The Value is the brightness of that color.
        * In my experience, when it comes to tuning the these thresholds the lower threshold has a lot more importance than the upper threshold.
* **normalize_lower, normalize_upper**
    * These are the upper and lower HSV values for the normalizing region. They are interpreted the same as the color_lower and color_upper values, and if they are exactly the same values as those, the normalizing region will be the same as the capturing region.
    * In my case, the normalizing region was the entire petri dish. This meant all colors taht are not black, hence the range (0,0,1) to (255, 255, 255)
* **normalize_area**
    * This is the area of the normalizing region. The measurement of the captured region is determined by the following:
        * Pixels captured region / pixels normalized region * area normalized region = area captured region
        
#### Inputs

* **file_extension**: This is the file extension of all the files you want to use.

#### Outputs

* **visually_verify**: If you want to check by eye that your thresholds are good and the code is working as intended, this should be set to `True`. It is recommended you leave it on True because there will often be minor details that can mess up the thresholds. One such problem that I have run into frequently is the lighting being different for a different day. If you don't have this set as true, you may miss something important. 
* **capturing_name**: This is the name of the column in the dataframe that stores the important data. In this case, it is Fern Coverage
* **normalize_unit** = This is the unit for the normalizing area. It will be put in parenthese at the end of the column name.
    * Not % is a special character in configuration files, so it needs to be escaped by typing %%.
    
#### Collections
These are all of the columns that the dataframe will store. You can create any number of these. They take different parts of the file name of each image in the data folder and store them in the column with name equal to the key in the configuration file.
* Note that the regex must match with every file name. Naming conventions don't need to be fully consistent with each other, but difference must be within the capability of regex to account for.


### Regex

* **Pitfall**: $.*_(.{4})
    * The intention of this regex expression is simple. After the first occurence of '_', grab the next four characters. However, this intention can be wrong because '.*' can also match with '_', meaning you can end up with the first four characters after the second, third, etc. '_'
    * The best way to fix this, in my opinion, is to be more explicit with your wild cards. Instead of '.*', use '[^_]*'
    * Another way that kinda works is '.?+' What this literally translates to is "1 or more of 1 or none of anything." What this practically does is the "The shortest amount of any amount of anything."
        * This method is definitely more convuluted. Regex is hard enough as is.
* Always check your .csv file afterward and your regular expressions before hand. You will get RegEx wrong, a lot. 
* All regex in this code requires the use of a single capturing group.

Examples:
* ^(.*).png
    * Captures everything from the start of the filename all the way to just before the extension.
    * The regex will break the code if it sees a filename that does not have .png in it.
    * This gives the ID. This is a column for the soul purpose of having the filename on hand to help the user find the file in case that datapoint is particular interesting.
*  ^([^_]*)_
    * Captures everything from the start of a filename to just before the first underscore.
    * In the example code this is the date.
