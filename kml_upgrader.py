import xml.etree.ElementTree as ET
import requests
import geopy.distance
import numpy as np
import math


class KML_Tests:
    has_points = bool
    has_tiles = bool
    def __init__(self, has_points, has_tiles):

        self.has_points= has_points
        self.has_tiles = has_tiles

class KML:
    nom= str
    tree= ET
    assertions = KML_Tests
    def __init__(self, nom, tree, assertions):
        self.nom= nom
        self.tree = tree
        self.assertions= assertions

##
#Ce programme permet la réécriture d'un fichier kml qui est composé de tiles et dont il manque les altitudes en un fichier kml composé de points (pour le moment, le centre des tuiles) et avec les altitudes. A l'avenir, ajouter un simple test qui vérifie que le fichier dispose de ces caractéristiques ou non.

# calcul_distance détermine la distance réelle entre deux points, étant donné leur latitude et longtitude
def calcul_distance(long1, lat1, long2, lat2):
    coords_1 = (lat1,long1)
    coords_2 = (lat2,long2)
    return(geopy.distance.geodesic(coords_1, coords_2).m)

# replace_string_in_xml_file permet d'écrire la requête d'altitudes à partir du template alt_request_template.xml
def replace_string_in_xml_file(filename, longs, lats):
    with open(filename, 'r') as f:
        xml_data = f.read()

    new_xml_data = xml_data.replace("LONG_STRING", longs)
    new_xml_data = new_xml_data.replace("LAT_STRING", lats)

    with open(f"alt_request.xml", 'w') as f:
        f.write(new_xml_data)

#kml_parser détermine quels types d'éléments se trouvent dans le fichier kml
def kml_parser(kml_name):
    kml_tree = ET.parse(kml_name) #lecture du fichier kml simpliste
    kml_root = kml_tree.getroot()
    ET.register_namespace("","http://www.opengis.net/kml/2.2")
    print(f"La racine du fichier est de type {kml_root}")
    print(f"Il y a {len(kml_root[0])} éléments, dont la racine.")

    has_points = kml_tree.findall(".//{http://www.opengis.net/kml/2.2}Points")
    if has_points:
        print("Le fichier KML contient des éléments de type Points")
        has_points = True
    else:
        print("Le fichier KML ne contient pas d'éléments de type Points")
        has_points = False
    has_tiles = kml_tree.findall(".//{http://www.opengis.net/kml/2.2}GroundOverlay")
    if has_tiles:
        print("Le fichier KML contient des éléments de type GroundOverlay")
        has_tiles = True
    else:
        print("Le fichier KML ne contient pas d'éléments de type GroundOverlay")
        has_tiles = False
    tests = KML_Tests(has_points, has_tiles)
    kml_file = KML("kml_name", kml_tree, tests)
    return (kml_file, tests)

#kml_upgrader modifie le kml en question suivant les résultats de kml_parser, pour n'obtenir que des points
def kml_upgrader(kml_file, tests, lats, longs, precision):
    i = 0 #Compteur de points
    if (tests.has_tiles and not tests.has_points): # Si pas de points, conversion nécessaire
        folder = kml_file.tree.findall(".//{http://www.opengis.net/kml/2.2}Folder")
        hasFolder = (len(folder)>0)
        if (not hasFolder):
            folder = ET.Element("Folder")
        kml_root = kml_file.tree.getroot()
        # Trouver tous les éléments "GroundOverlay"
        list_ground_overlays = kml_root.findall(".//{http://www.opengis.net/kml/2.2}GroundOverlay")
        print(len(list_ground_overlays))
        for ground_overlay in list_ground_overlays:

            # Récupérer les coordonnées du coin nord-est et du coin sud-ouest de l'image
            north = float(ground_overlay.findtext(".//{http://www.opengis.net/kml/2.2}north"))
            south = float(ground_overlay.findtext(".//{http://www.opengis.net/kml/2.2}south"))
            east = float(ground_overlay.findtext(".//{http://www.opengis.net/kml/2.2}east"))
            west = float(ground_overlay.findtext(".//{http://www.opengis.net/kml/2.2}west"))

            if (len(list_ground_overlays)==1):
                lats.append(south)
                lats.append(north)
                longs.append(west)
                longs.append(east)
            else:
                # Calculer la latitude et la longitude du centre de l'image
                latitude = (north + south) / 2
                longitude = (east + west) / 2

                if (not longitude in longs):
                    longs.append(longitude)
                if (not latitude in lats):
                    lats.append(latitude)



        #Test précision longitudinale
        #Si ce test n'est pas vérifié, un linspace est effectué pour obtenir la précision désirée (en argument)
        print(f"longs[0],lats[0],longs[1],lats[0] : {longs[0]},{lats[0]},{longs[1]},{lats[0]}")
        dist = calcul_distance(longs[0],lats[0],longs[1],lats[0])
        if (dist > precision):
            long_len_multiplier = math.floor(dist/precision) + 1
            new_long_len = long_len_multiplier*len(longs)
            new_longs = np.linspace(longs[0],longs[-1],new_long_len)
        else:
            new_longs = longs
        #Test précision latitudinale
        #De même ici
        dist = calcul_distance(longs[0],lats[0],longs[0],lats[1])
        if (dist > precision):
            lat_len_multiplier = math.floor(dist/precision) + 1
            new_lat_len = lat_len_multiplier*len(lats)
            new_lats = np.linspace(lats[0],lats[-1],new_lat_len)
        else:
            new_lats = lats

        # Créer un nouvel élément "Point" avec les coordonnées de latitude, de longitude et d'altitude
        for latitude in new_lats:
            for longitude in new_longs:
                point = ET.Element("Point")
                coord = ET.Element("coordinates")

                coord.text = f"{longitude},{latitude}"
                tile = ET.Element("Icon")
                href = ET.Element("href")
                href.text = ground_overlay.findtext(".//{http://www.opengis.net/kml/2.2}href")

                tile.insert(0,href)
                point.insert(9,coord)
                point.insert(1,tile)

            # Insérer l'élément "Point" dans l'arbre de l'objet ElementTree
                if (not hasFolder):
                    folder.append(point)
                else:
                    folder[0].append(point)
                i += 1
        kml_root.append(folder)
        for ground_overlay in kml_root.findall(".//{http://www.opengis.net/kml/2.2}GroundOverlay"):
            # Retirer l'élément "GroundOverlay" de l'arbre
            if (ground_overlay in folder[0]):
                folder[0].remove(ground_overlay)

        print(f"Vérification du nombre de points lus : {i}")
        return convert_lists(new_lats, new_longs)

#Convertit les listes des longitudes et latitudes uniques en listes contenant le nombre actuels de longitudes et latitudes nécessaires pour la requête
def convert_lists(old_longs, old_lats):
    final_longs = []
    final_lats = []
    for lat in old_lats:
        for long in old_longs:
            final_longs.append(long)
            final_lats.append(lat)
    return final_longs, final_lats

#Envoie la requête d'altitudes à partir des listes d'altitude et de longitude, retourne la liste des altitudes correspondantes
#La méthode POST de l'API REST de l'IGN est utilisée ici
def request_heights(longs_list, lats_list):
    lat_string = f"{lats_list[0]}"
    long_string = f"{longs_list[0]}"
    for i in range(1,len(lats_list)):
        lat_string += "|" + f"{lats_list[i]}"
        long_string += "|" + f"{longs_list[i]}"

    replace_string_in_xml_file("request_template.xml", long_string, lat_string)

    # URL de requête de l'API
    url = "https://wxs.ign.fr/calcul/alti/wps?service=WPS&version=1.0.0"

    #Chargement du template
    with open("alt_request_template.xml", "r") as f:
        xml_data = f.read()

    headers = {"Content-type": "text/xml"}

    # Envoi de la requête POST
    response = requests.post(url, data=xml_data, headers=headers)
    if response.status_code == 200:
        print("Requête POST : succès")
    else:
        print(f"Requête POST : échec. Code {response.status_code}")

    root = ET.fromstring(response.content)

    # On extrait les valeurs d'altitudes
    altitudes = []
    for elevation in root.findall("./elevation"):
        altitudes.append(float(elevation.find("z").text))


    return altitudes

#write_kml réécrit le fichier kml avec le bon format.
def write_kml(kml_file, lats, longs, alts):
    ET.indent(kml_file.tree, space='  ', level=0)
    kml_file.tree.write("fichier_converti.kml",encoding='utf-8', xml_declaration=True, default_namespace=False, method='xml', short_empty_elements=True) #écriture dans le fichier converti
    kml_tree2 = ET.parse("fichier_converti.kml")
    kml_root2 = kml_tree2.getroot()
    folder2 = kml_tree2.findall(".//{http://www.opengis.net/kml/2.2}Folder")
    i=0
    for point in kml_root2.findall(".//{http://www.opengis.net/kml/2.2}Point"):
        folder2[0].remove(point)
    for i in range(len(alts)):
        new_point = ET.Element("Point")
        coord = ET.Element("coordinates")
        coord.text = f"{longs[i]},{lats[i]},{alts[i]}"
        new_point.append(coord)

    #étant donné qu'il est impossible de remplacer des valeurs directement avec ce module, il nous a fallu tout resupprimer et tout rajouter pour que les altitudes soient dans le fichier kml. Il y a sûrement bien mieux à faire

        folder2[0].insert(i,new_point)

    ET.indent(kml_tree2, space='  ', level=0)
    kml_tree2.write("fichier_converti.kml",encoding='us-ascii', xml_declaration=True, default_namespace=False, method='xml', short_empty_elements=False) #écriture dans le fichier converti
