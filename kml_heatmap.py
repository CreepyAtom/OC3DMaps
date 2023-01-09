import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET
import os
new_directory = 'C:\\Users\\picart\\Desktop\\Projet2AInfo'
os.chdir(new_directory)
##
#Ce programme permet la lecture des altitudes du fichier kml et la génération de la heatmap correspondante. A plus long terme, il faudra appliquer un masque précis sur la course d'orientation initiale / s'en servir sur Blender pour générer la 3D
kml_tree = ET.parse("fichier_converti.kml")
kml_root = kml_tree.getroot()
LINE_LEN = 28
altitudes = [[]]
i = 0 #permet "le changement de ligne"
max, min = -999, 999
for point in kml_root.findall(".//{http://www.opengis.net/kml/2.2}Point"):
    coords = point.findtext(".//{http://www.opengis.net/kml/2.2}coordinates")
    if coords:
        if (i==LINE_LEN):
            altitudes.append([])
            i=0
        new_coords = coords.split(",")
        altitudes[-1].append(float(new_coords[-1]))
        if (float(new_coords[-1]) < min):
            min = float(new_coords[-1])
        if (float(new_coords[-1]) > max):
            max = float(new_coords[-1])
        i+=1
    else:
        print("oh nonnnn :(")

#Lecture de toutes les altitudes des points, sachant que le premier point est en bas à gauche.

ax = sns.heatmap(altitudes, linewidth=0, square = True, annot = False, cmap="hot", vmin = min, vmax = max)
plt.savefig('./output/foo.png')
##
ax2 = sns.heatmap(altitudes, linewidth=0, square = True, annot = False, cmap="hot", vmin = min, vmax = max, cbar = False)
ax2.set_axis_off()

plt.savefig('./output/alt_map.png', bbox_inches='tight', pad_inches=0)
plt.show()