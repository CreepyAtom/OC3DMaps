from PIL import Image
import os

##
# Ce programme permet la fusion de toutes les tuiles afin d'obtenir une seule et même image, que l'on peut ensuite afficher sur le site.
SIZE = 128
NB_COL = 28
NB_LIN = 16
    # Ouverture de toutes les images. Pour le moment, elles sont dans le dossier files de l'archive kmz, à généraliser
def tiles_merger():
    images = []
    for j in range(NB_COL):
        for i in range(NB_LIN):
            images.append(Image.open(f"files/tile_{j}_{i}.jpg").resize((SIZE, SIZE)))
            #print(f"files/tile_{j}_{i}.jpg")

    #Création de l'image vide 'grille'
    grid_image = Image.new(mode='RGB', size=(NB_COL*SIZE,NB_LIN*SIZE), color=(255, 255, 255))

    # Itération à travers toutes les images, sachant que la première image de la liste est en bas à gauche MAIS que d'après la convention de Genève, la coordonnée (0,0) correspond au coin supérieur gauche
    x = 0
    y = (NB_LIN-1)*SIZE
    for image in images:
        grid_image.paste(image, (x, y))
        y -= SIZE
        if y < 0:
            y = (NB_LIN-1)*SIZE
            x += SIZE

    # Sauvegarde de l'image finale
    grid_image.save("./output/grid.png")

if __name__ == '__main__':
    tiles_merger()
