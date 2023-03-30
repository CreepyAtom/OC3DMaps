import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET
import plotly.offline as go_offline
import plotly.graph_objects as go
import matplotlib
from mpl_toolkits.mplot3d import axes3d
from pylab import *
from mpl_toolkits.mplot3d import Axes3D

import shutil
import requests
import os
import geopy.distance
import numpy as np
import math
from zipfile import ZipFile
new_directory = 'C:\\Users\\picart\\Documents\\GitHub\\OC3DMaps'
os.chdir(new_directory)


kmz = ZipFile('Plateau-de-Jarrie.kmz', 'r')
kmz.extractall( path=None, pwd=None)
kml_file, tests = up.kml_parser("doc.kml")
i = 0
lats = []
longs = []
print(f"Test tile :{tests.has_tiles}, Test points : {tests.has_points}")
lats, longs = up.kml_upgrader(kml_file, tests, lats, longs, 100)

limite_req = 180
print("Nb boucles à effectuer =" + f"{len(lats)//limite_req+1}")
alts = up.request_heights(limite_req, longs, lats)
up.write_kml(kml_file, lats, longs, alts)
shutil.rmtree('files')
os.remove("doc.kml")

lat_data=lats
lon_data=longs
alts=alts


terrain_cmap = matplotlib.cm.get_cmap('terrain')
def matplotlib_to_plotly(cmap, pl_entries):
    h = 1.0/(pl_entries-1)
    pl_colorscale = []
    for k in range(pl_entries):
        C = list(map(np.uint8, np.array(cmap(k*h)[:3])*255))
        pl_colorscale.append([k*h, 'rgb'+str((C[0], C[1], C[2]))])
    return pl_colorscale

terrain = matplotlib_to_plotly(terrain_cmap, 255)

# CREATING 3D TERRAIN
lat_min=min(lat_data)
lat_max=max(lat_data)
lon_min=min(lon_data)
lon_max=max(lon_data)


stretch_factor = 8
alts_data = np.array(alts).reshape(55, 48)
lon_data = np.linspace(lon_min, lon_max, alts_data.shape[1])
lat_data = np.linspace(lat_min, lat_max, alts_data.shape[0])

X, Y = np.meshgrid(lon_data, lat_data)

fig = go.Figure(data=[go.Surface(colorscale=terrain,z=alts_data, x=X, y=Y)])
fig.update_layout(title='Elevation Plot', autosize=True,
                  margin=dict(l=65, r=50, b=65, t=90))

go_offline.plot(fig, filename='test.html')
