data = {
    "Female": {
        "18-19": [10, 11, 12.9, 14.9],
        "20-29": [8, 9.9, 11.4, 14.2],
        "30-39": [7.7, 9.3, 10.8, 13.6],
        "40-49": [7.4, 8.9, 10.3, 13.2],
        "50-59": [7, 8, 9.9, 12.9],
        "60-69": [6, 6.9, 8.4, 11],
        "70-79": [5, 5.9, 6.9, 9.9],
        "80-80": [4.4, 5.4, 6.2, 8.3],
    },
    "Male": {
        "18-19": [10.8, 12.9, 13.9, 16.2],
        "20-29": [10.3, 11.9, 13.6, 15.6],
        "30-39": [10, 11.1, 12.9, 14.9],
        "40-49": [9.8, 10.9, 12.4, 14.6],
        "50-59": [8.2, 9.9, 11.3, 13.9],
        "60-69": [7, 8.4, 9.9, 12.9],
        "70-79": [6, 6.9, 8.4, 11.4],
        "80-80": [5.1, 6.2, 7.2, 9.9],
    }
}

groups = ["Low", "Below Average", "Above Average", "High", "Elite"]
group_comparison = {
    "Low vs Elite": (5.04, 4.10, 6.20),
    "Low vs High": (3.90, 3.67, 4.14),
    "Low vs Above Average": (2.75, 2.61, 2.89),
    "Low vs Below Average": (1.95, 1.86, 2.04),
    "Below Average vs Elite": (2.59, 2.10, 3.19),
    "Below Average vs High": (2.00, 1.88, 2.14),
    "Below Average vs Above Average": (1.41, 1.34, 1.49),
    "Above Average vs Elite": (1.84, 1.49, 2.26),
    "Above Average vs High": (1.42, 1.33, 1.52),
    "High vs Elite": (1.29, 1.05, 1.60),
}

full_data = dict()
for s in ["Male", "Female"]:
    data_dict = data[s]
    full_data[s] = dict()
    for k, v in data_dict.items():
        start, end = [int(x) for x in k.split("-")]
        full_data[s].update({age: v for age in range(start, end + 1)})

other_hazard_ratios = [
    [1.21, "Hypertension", "medical condition", 1.16, 1.25],
    [1.40, "Diabetes", "medical condition", 1.34, 1.46],
    [1.41, "Smoking", "medical condition", 1.36, 1.46],
    [2.80, "Kidney Failure", "medical condition", 2.53, 3.05],
    [1.16, "Too much sugar", "dietary", 0.9, 1.5],
    [1.45, "Too much saturated fat", "dietary", 1.3, 1.7],
    [1.50, "Too little fibre", "dietary", 1.3, 1.7]

]
