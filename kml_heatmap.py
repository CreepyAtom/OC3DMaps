import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET
import os
new_directory = 'C:\\Users\\picart\\Documents\\GitHub\\OC3DMaps'
os.chdir(new_directory)

LINE_LEN = 28
##
#Ce programme permet la lecture des altitudes du fichier kml et la génération de la heatmap correspondante. A plus long terme, il faudra appliquer un masque précis sur la course d'orientation initiale / s'en servir sur Blender pour générer la 3D
def create_heatmap(kml_filename):
    kml_tree = ET.parse(kml_filename)
    kml_root = kml_tree.getroot()
    altitudes = [[]]
    tab_coords = [[]]
    i = 0 #permet "le changement de ligne"
    max, min = -999, 999
    for point in kml_root.findall(".//{http://www.opengis.net/kml/2.2}Point"):
        coords = point.findtext(".//{http://www.opengis.net/kml/2.2}coordinates")
        if coords:
            if (i==LINE_LEN):
                altitudes.append([])
                tab_coords.append([])
                i=0
            new_coords = coords.split(",")
            tab_coords[-1].append([float(new_coords[0]),float(new_coords[1]), float(new_coords[2])])
            altitudes[-1].append(float(new_coords[2]))
            if (float(new_coords[-1]) < min):
                min = float(new_coords[-1])
            if (float(new_coords[-1]) > max):
                max = float(new_coords[-1])
            i+=1
        else:
            print("Shouldn't be here.")
    return altitudes, tab_coords, max, min


##Lecture de toutes les altitudes des points, sachant que le premier point est en bas à gauche.
if __name__ == '__main__':
    filename = "fichier_converti.kml"
    altitudes, tab_coords, max, min = create_heatmap(filename) # tab_coords pas encore utilisé
    ax = sns.heatmap(altitudes, linewidth=0, square = True, annot = False, cmap="hot", vmin = min, vmax = max)
    plt.savefig('./output/foo.png')

    ax2 = sns.heatmap(altitudes, linewidth=0, square = True, annot = False, cmap="hot", vmin = min, vmax = max, cbar = False)
    ax2.set_axis_off()

    plt.savefig('./output/alt_map.png', bbox_inches='tight', pad_inches=0)
    plt.show()