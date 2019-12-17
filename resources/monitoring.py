import serial
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import time
import os
import sys

from os import listdir
from os.path import isfile, join

#mypath = "monitoring"
mypath = os.path.join('monitoring','')
print(mypath)

onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

print("all files: " , onlyfiles)

fb_names = []
alg_names = []

## Check all files
for file in onlyfiles:
    temp = file.split("__")

    if len(temp) == 1:
        continue

    alg_temp_name = temp[1].split(".")[0]

    if temp[0] not in fb_names: fb_names += [temp[0]]
    if alg_temp_name not in alg_names: alg_names += [alg_temp_name]

if len(alg_names) == 0 or len(fb_names) == 0:
    print("No files available yet! Try in a few seconds...")
    exit()

## Graphs for how many alerts in a row
name_hist = "Health Monitoring"
hist_alg = 0
reps = 5
alg_names += [name_hist]

## Graphs showing number of input and output events per fb
name_events = "Events"
alg_names += [name_events]

## max samples to plot
max_samples = 50


print(fb_names)
print(alg_names)

fig, axs = plt.subplots(len(alg_names), len(fb_names))

def animate(i):
    for x in np.arange(len(fb_names)):
        for y in np.arange(len(alg_names)):

            if (alg_names[y] is name_events):

                f = open(mypath + "{0}.txt".format(fb_names[x]), "r").read()
                lines = f.split('\n')
                events = np.array([])

                if len(lines) < reps: continue

                ## if at least the number of results is higher than reps
                if len(lines) > max_samples:
                    lines = lines[-max_samples:]

                for line in lines[-max_samples:]:

                    if line == "": continue

                    data = line.split(',')
                    if len(events) == 0:
                        events = data
                    else:
                        events = np.vstack((events,data))

                if len(fb_names) == 1:
                    axs[y].clear()
                    axs[y].set_title('{0}'.format(fb_names[x]))
                    axs[y].plot(events[:,0])
                    axs[y].plot(events[:,1])
                    axs[y].legend(("Input","Output"),loc='lower left')

                    ## Write the label for the algorithm
                    if x == 0:
                        axs[y].set_ylabel(alg_names[y])
                else:
                    axs[y, x].clear()
                    axs[y, x].set_title('{0}'.format(fb_names[x]))
                    axs[y, x].plot(events[:, 0])
                    axs[y, x].plot(events[:, 1])
                    axs[y, x].legend(("Input", "Output"), loc='lower left')
                    axs[y, x].set_ylim(bottom=0)

                    ## Write the label for the algorithm
                    if x == 0:
                        axs[y, x].set_ylabel(alg_names[y])

            elif (alg_names[y] is name_hist):

                f = open(mypath + "{0}__{1}.txt".format(fb_names[x], alg_names[hist_alg]), "r").read()
                lines = f.split('\n')
                label = []

                if len(lines) < reps: continue

                ## if at least the number of results is higher than reps
                if len(lines) > max_samples:
                    lines = lines[-max_samples:]

                for line in lines[-max_samples:]:
                    if line == "": continue

                    label.append(line.split(',')[-1])

                label = np.array(label).astype(int)
                label = [i if i == -1 else 1 for i in label]

                if len(fb_names) == 1:
                    axs[y].clear()
                    axs[y].set_title('{0}'.format(fb_names[x]))
                    axs[y].set_ylim([-3,3])
                    #axs[y].set_xlim([0,4])
                    axs[y].plot(label)


                    ## Write the label for the algorithm
                    if x == 0:
                        axs[y].set_ylabel(alg_names[y])
                else:
                    axs[y, x].clear()
                    axs[y, x].set_title('{0}'.format(fb_names[x]))
                    axs[y, x].set_ylim([-3, 3])
                    #axs[y, x].set_xlim([0, 4])
                    axs[y, x].plot(label)

                    ## Write the label for the algorithm
                    if x == 0:
                        axs[y, x].set_ylabel(alg_names[y])

            else:
                f = open(mypath + "{0}__{1}.txt".format(fb_names[x],alg_names[y]), "r").read()
                lines = f.split('\n')
                xs = np.array([])
                label = []

                if len(lines) < reps: continue

                if len(lines) > max_samples: lines = lines[-max_samples:]

                for line in lines[-max_samples:]:
                    if line == "":
                        continue

                    data = line.split(',')
                    if len(xs) == 0:
                        xs = data[0:-1]
                    else:
                        xs = np.vstack((xs,data[0:-1]))

                    label.append(data[-1])

                if len(xs) == 0: continue

                color = ['red' if l == "-1" else 'green' for l in label]

                if len(alg_names) == 1:
                    axs[x].clear()
                    axs[x].set_title('{0}'.format(fb_names[x]))
                    axs[x].scatter(xs[:, 0], xs[:, 1], color=color)

                    ## Write the label for the algorithm
                    if x == 0:
                        axs[x].set_ylabel(alg_names[y])

                elif len(fb_names) == 1:
                    axs[y].clear()
                    axs[y].set_title('{0}'.format(fb_names[x]))
                    axs[y].scatter(xs[:, 0], xs[:, 1], color=color)

                    ## Write the label for the algorithm
                    if x == 0:
                        axs[y].set_ylabel(alg_names[y])
                else:
                    axs[y, x].clear()
                    axs[y, x].set_title('{0}'.format(fb_names[x]))
                    axs[y, x].scatter(xs[:, 0], xs[:, 1], color=color)

                    ## Write the label for the algorithm
                    if x == 0:
                        axs[y, x].set_ylabel(alg_names[y])

print('Plotting...')

# Set up plot to call animate() function periodically

ani = animation.FuncAnimation(fig, animate, interval=4000, frames=10)
plt.show()
