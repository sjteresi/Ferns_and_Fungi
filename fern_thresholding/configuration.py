parameters = {}

# The lower and upper boundries for color detection
parameters["color_lower"] = (20, 40, 40)
parameters["color_upper"] = (70, 255, 255)

# Boolean for if you want to save the outputs to see what the computer sees.
parameters["visually_verify"] = True

# Regular expressions to catch file names
# TODO: Replace this with a list of arbitrary length formated like : [("label", regex)]
parameters["date_regex"] = "^([^_]*)_"
parameters["group_regex"] = "_(.*)[_-]"
parameters["replicate_regex"] = "([0-9]*)\.png"

parameters["collections"] = {
    "ID" : "^(.*)\.png",
    "Date" : "^([^_]*)_",
    "Group" : "_(.*)[_-]",
    "Replicate" : "([0-9]*)\.png"
}
# Handling for special cases
# Formatted like the following:
# if re.search(tuple[0], filename) == tuple[1]):
#      lower = tuple[2]
#      upper = tuple[3]
parameters["special_cases"] = [
    ("^([^_]*)_", "5wk", (20, 80, 60), (70, 255, 255))
]

