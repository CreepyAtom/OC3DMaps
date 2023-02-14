import xml.etree.ElementTree as ET
import requests
import os
new_directory = 'C:\\Users\\picart\\Documents\\GitHub\\OC3DMaps'
os.chdir(new_directory)

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

# Charger le fichier KML en mémoire

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

def kml_upgrader(kml_file, tests):
    i = 0 #Compteur de points
    if (tests.has_tiles and not tests.has_points): # Si pas de points, conversion nécessaire
        folder = kml_file.tree.findall(".//{http://www.opengis.net/kml/2.2}Folder")
        kml_root = kml_file.tree.getroot()
        # Trouver tous les éléments "GroundOverlay"
        for ground_overlay in kml_root.findall(".//{http://www.opengis.net/kml/2.2}GroundOverlay"):
            # Récupérer les coordonnées du coin nord-est et du coin sud-ouest de l'image
            north = float(ground_overlay.findtext(".//{http://www.opengis.net/kml/2.2}north"))
            south = float(ground_overlay.findtext(".//{http://www.opengis.net/kml/2.2}south"))
            east = float(ground_overlay.findtext(".//{http://www.opengis.net/kml/2.2}east"))
            west = float(ground_overlay.findtext(".//{http://www.opengis.net/kml/2.2}west"))


            # Calculer la latitude et la longitude du centre de l'image
            latitude = (north + south) / 2
            longitude = (east + west) / 2

            longs.append(longitude)
            lats.append(latitude)


            # Créer un nouvel élément "Point" avec les coordonnées de latitude, de longitude et d'altitude
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
            folder[0].insert(i,point)
            i += 1
            # Retirer l'élément "GroundOverlay" de l'arbre
            folder[0].remove(ground_overlay)

        print(f"Vérification du nombre de points lus : {i}")


def request_heights(limite_req, longs, lats):
    for i in range(0,len(lats)//limite_req):
        lat_string = f"{lats[limite_req*i]}"
        long_string = f"{longs[limite_req*i]}"
        for j in range (limite_req*i,limite_req*(i+1)):
            lat_string += "|" + f"{lats[j]}"
            long_string += "|" + f"{longs[j]}"

        response = requests.get("https://wxs.ign.fr/calcul/alti/rest/elevation.json?lon=" + long_string + "&lat=" + lat_string + "&zonly=true")

        if response.status_code == 200:
        # Traitement de la réponse
            data = response.json()["elevations"][0]
            print(f"Altitude du premier point de la liste : {data} mètres")
            responses.append(response)
        else:
            print("Erreur lors de la récupération de l'altitude")


    lat_string = f"{lats[(len(lats)//limite_req)*limite_req]}"
    long_string = f"{longs[(len(lats)//limite_req)*limite_req]}"
    for j in range((len(lats)//limite_req)*limite_req+1, len(lats)):
        lat_string += "|" + f"{lats[j]}"
        long_string += "|" + f"{longs[j]}"

    response = requests.get("https://wxs.ign.fr/calcul/alti/rest/elevation.json?lon=" + long_string + "&lat=" + lat_string + "&zonly=true")

    if response.status_code == 200:
        # Traitement de la réponse, 200 = valide
        data = response.json()["elevations"][0]
        print(f"Altitude du premier point de la liste : {data} mètres")
        responses.append(response)
    else:
        print("Erreur lors de la récupération de l'altitude")
    data_totale = []
    for response in responses:
        data = response.json()["elevations"]
        for valeur in data:
            data_totale.append(valeur) #on vide toute la liste de requêtes ici
    return data_totale



# Enregistrer le fichier KML modifié

def write_kml(kml_file, data_totale):
    ET.indent(kml_file.tree, space='  ', level=0)
    kml_file.tree.write("fichier_converti.kml",encoding='utf-8', xml_declaration=True, default_namespace=False, method='xml', short_empty_elements=True) #écriture dans le fichier converti
    kml_tree2 = ET.parse("fichier_converti.kml")
    kml_root2 = kml_tree2.getroot()
    folder2 = kml_tree2.findall(".//{http://www.opengis.net/kml/2.2}Folder")
    i=0
    for point in kml_root2.findall(".//{http://www.opengis.net/kml/2.2}Point"):
        coords = point.findtext(".//{http://www.opengis.net/kml/2.2}coordinates")
        if coords:
            new_point = ET.Element("Point")
            coord = ET.Element("coordinates")
            old_coords = coords.split(",")
            coord.text = f"{old_coords[0]},{old_coords[1]},{data_totale[i]}"
            is_href = point.findtext(".//{http://www.opengis.net/kml/2.2}href")
            if is_href:
                new_tile = ET.Element("Icon")
                href = ET.Element("href")
                href.text = is_href
                new_tile.insert(0,href)
            else:
                print("Isn't href. Shouldn't happen.'")
            new_point.append(coord)
            new_point.append(new_tile)

    #étant donné qu'il est impossible de remplacer des valeurs directement avec ce module, il m'a fallu tout resupprimer et tout rajouter pour que les altitudes soient dans le fichier kml. Il y a sûrement bien mieux à faire

            folder2[0].insert(i,new_point)
            folder2[0].remove(point)
        else:
            print("No coords found.")
        #print(coords)
        i+=1

    ET.indent(kml_tree2, space='  ', level=0)
    kml_tree2.write("fichier_converti.kml",encoding='us-ascii', xml_declaration=True, default_namespace=False, method='xml', short_empty_elements=False) #écriture dans le fichier converti
##
if __name__ == '__main__':
    kml_file, tests = kml_parser("doc.kml")
    i = 0
    lats = []
    longs = []
    print(f"Test tile :{tests.has_tiles}, Test points : {tests.has_points}")
    kml_upgrader(kml_file, tests)
    responses = [] #liste des réponses aux requêtes, sur mon PC, chaque requête est limitée à env. 190 points, d'où la manip suivante
    limite_req = 190
    print("Nb boucles à effectuer =" + f"{len(lats)//limite_req+1}")
    data_totale = request_heights(limite_req, longs, lats)
    write_kml(kml_file, data_totale)