import random
from numpy import average, ones
import pandas as pd
import os
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import matplotlib.ticker as ticker

# Delcaring variables:
angle_data = pd.DataFrame(columns=['WELL','AVG','AAC','MAX','MIN'])
angle_dict = {}
angle_cutoff = 5

# Declaring data folder path:
workfold = 'C:\\Well Data'

for folder, subfolder, files in os.walk(workfold):
    # Accessing well survey data:
    if 'Well Survey Data.csv' in files:
        filePath = os.path.join(folder, 'Well Survey Data.csv')                        
        survey = pd.read_csv(filePath)
        with open(filePath,'r') as f:
            content = f.read()

        if not survey.empty:
            try:

                if max(abs(survey[' Inc'])) >= 90 - angle_cutoff: # Verifying existence of horizontal section
                    
                    well = survey.loc[0,'File No']
                    sections = set(survey['Leg'])
                    sections.remove('VERT') # Removing vertical section of well

                    for section in sections:
                        inclination = survey[survey[' Leg'] == section][' Inc']
                        measured_depth = survey[survey[' Leg'] == section][' MD']

                        print('Reading ' + str(well))

                        for i, angle in enumerate(inclination): 
                            if abs(angle) >= 90 - angle_cutoff: # Scanning for end of build-up
                                
                                # Declaring and converting inclination:
                                inc = list(inclination[i:] - 90)
                                angle_dict[well] = inc    

                                # Skipping sections with 1 survey nodes:
                                if len(inc) < 2:
                                    break

                                MD = list(measured_depth[i:])
                                average_angle = []
                                AAC = 0
                                
                                # Skipping lateral sections with less than 5000ft length:
                                if MD[-1] - MD[0] < 5000:
                                    break
                                    
                                # Calculating Average Angle Change:
                                for i, a1 in enumerate(inc):
                                    if i == 0:
                                        a0 = a1
                                        continue
                                    else:
                                        AAC += (a1 + a0)*(float(MD[i]) - float(MD[i-1]))

                                AAC /= float(MD[-1]) - float(MD[0])

                                # Reporting Results
                                angle_data.loc[len(angle_data.index)] = [str(well), average(inc), AAC, max(inc), min(inc)]
                                break
            except KeyError:
                continue

angle_data = angle_data[abs(angle_data['AVG']) < 10]

# Plotting angle distribution for 5 random wells:
for i in range(5):
    entry = random.choice(list(angle_dict.items()))
    inc = entry[1]    
    Title = 'Distribution of Angle Variation (%) - Well ' + str(entry[0])

    plt.figure(i)
    plt.hist(inc, weights=ones(len(inc)) / len(inc), bins=20)
    plt.gca().set(title=Title, ylabel='Frequency')
    plt.gca().yaxis.set_major_formatter(PercentFormatter(1))
    plt.yscale("log")
    plt.savefig(Title + '.png', format='png')

#Plotting Average Angle Change and Arithmetic Average Angle distributions:
plt.figure(5)
plt.hist(angle_data['AVG'], weights=ones(len(angle_data['AVG'])) / len(angle_data['AVG']),bins=20)
plt.gca().set(title='Aggregate Distribution of Average Angles', ylabel='Frequency (%)')
plt.gca().yaxis.set_major_formatter(PercentFormatter(1))
plt.savefig('Aggregate Distribution of Average Angles.png', format='png')

plt.figure(6)
plt.hist(angle_data['AAC'], weights=ones(len(angle_data['AAC'])) / len(angle_data['AAC']),bins=20)
plt.gca().set(title='Aggregate Distribution of Average Angles', ylabel='Frequency (%)')
plt.gca().yaxis.set_major_formatter(PercentFormatter(1))
plt.savefig('Aggregate Distribution of AAC.png', format='png')

# Exporting output data to a CSV file:
angle_data.to_csv('Results.csv')
