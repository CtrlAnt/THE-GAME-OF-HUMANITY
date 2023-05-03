#🧱 - Importation des modules :

from Map.generation import *
from Map.display import *
from Environment.case_occupe import *
from Environment.gestion import *
import random
import time



#🏃‍♂️ - Fonctions de déplacements

def fuite_perso(identifiant):
    """> Contrôle la fuite du personnage.
    Entrée: L'identifiant du personnage.
    Sortie: Null / False si le personnage a nulle part ou aller."""
    old_position = [key for key, value in map.items() if value['IDENTIFIANT'] == identifiant][0]  #Trouve position à partir de l'identifiant
    liste_pos = next_to(old_position)
    response,liste_pos = filtre(liste_pos.copy(),param=solid+["food","player_blue","player_red"])

    #Permet de ne pas bloquer le programme quand un personnage à nulle part ou aller.
    if not response:
        return False
    
    #Prend une nouvelle position aléatoire dans la liste des cases disponibles.
    new_pos = random.choice(liste_pos)
    val = val_inter(old_position,new_pos)   #Pour réaliser un déplacement fluide de l'ancienne case du personnage à sa nouvelle.
    
    #Déplacement du personnage.
    map[new_pos] = map[old_position].copy()    #On assigne à la clé (position) une nouvelle valeur (nouvelle position du personnage).
    map[new_pos]["MOVE"] = val
    map[old_position] = {"objet":"grass","IDENTIFIANT":"grass"+str(id(map[old_position]))}  #Met de l'herbe à la place de l'ancienne position du personnage.

    
    
def move(identifiant):
    """> Cette fonction bouge un personnage à partir de son identifiant.
    Entrée: L'identifiant du personnage.
    Sortie: Null / False si le personnage est mort ou si il a nulle part ou aller."""
    mort = False

    #Récupération de la position actuelle du personnage à partir de son identifiant.
    try:
        old_position = [key for key, value in map.items() if value['IDENTIFIANT'] == identifiant][0]
    except:
        #Si le personnage n'a pas de position : cela veut dire qu'il est mort donc la fonction se termine en retournant False pour ne pas bloquer le programme.
        return False
    
    map[old_position]["ENERGY"] = map[old_position]["ENERGY"] + parametre["ENERGY_LIFE"]

    if map[old_position]["objet"] == "player_red":
        attaque = "player_blue"

    if map[old_position]["objet"] == "player_blue":
        attaque = "player_red"     

    #Liste des cases ou le déplacement est possible (les 8 cases autour du personnage ou il n'y a pas de solide/entité).
    liste_pos = next_to(old_position)

    #Enleve les rochers et arbres.
    response,liste_pos = filtre(liste_pos,param=solid)

    #Si le personnage n'a nulle part ou aller : la fonction se termine en retournant False pour ne pas bloquer le programme.
    if not response:
        return False
 
    #Prend une position au hasard dans la liste des cases ou le déplacement est possible.
    new_pos = random.choice(liste_pos)   

    response_attaque,liste_attaque = filtre_cible(liste_pos.copy(),param=[attaque])
    response_food,liste_food = filtre_cible(liste_pos.copy(),param=["food"])
    response_repr,liste_repr = filtre_cible(liste_pos.copy(),param=[map[old_position]["objet"]])

    # --- ATTAQUE --- #
    #Si il y a un perso d'un clan opposé à coté de lui, il l'attaque.
    if response_attaque:
        liste_pos = liste_attaque
        
        #Prend une position au hasard dans la liste des cases ou le déplacement est possible.
        new_pos = random.choice(liste_pos)        
        rand_num = random.randint(0,100)
        
        #Si l'attaquant réussi son attaque, l'attaqué meurt. (puissance du personnage > rand_num)
        if map[old_position]["POWER"] > rand_num:

            #Attaque
            map[old_position]["ENERGY"] = map[old_position]["ENERGY"] + parametre["ENERGY_FIGHT"]
            mort = {new_pos:map[new_pos]["objet"]}
            
        #Sinon l'attaqué prend la fuite.
        else:
            new_pos = old_position
            fuite_perso(map[new_pos]["IDENTIFIANT"])
            new_pos = old_position
        
        mise_a_jour(old_position,new_pos)
        return mort
    


    #Si il y a un poulet a coté de lui, il le personnage l'attaque.
    elif response_food:
        liste_pos = liste_food
        
        new_pos = random.choice(liste_pos)
        rand_num = random.randint(0,100)
        
        #Si le personnage réussi son attaque : le poulet meurt. (agilité du personnage > rand_num)
        if map[old_position]["AGILITY"] > rand_num:
            mort = {new_pos:map[new_pos]["objet"]}
            map[old_position]["ENERGY"] =   map[old_position]["ENERGY"] + parametre["ENERGY_FOOD"]
            map[old_position]["FOOD"] =   map[old_position]["FOOD"] + 1
            #map[old_position]["ENERGY"] =   map[old_position]["ENERGY"] + parametre["ENERGY_CATCH"]
        
        #Sinon il s'enfuit.
        else:
            fuite_perso(map[new_pos]["IDENTIFIANT"])

        mise_a_jour(old_position,new_pos)
        return mort
    

    # --- REPRODUCTION --- #
    elif response_repr :
        new_pos = random.choice(liste_repr)
        rand_num = random.randint(0,100)
        #Deux personnages peuvent se reproduire si il sont assez fertile.
        #Effectue la reproduction que si les personnages ne se sont jamais reproduits ensemble ou que le personnage avec lequel ils sont sur le point de se reproduire...
        #...n'est pas leur enfant.
        if map[new_pos]["IDENTIFIANT"] not in map[old_position]["REPRODUCTION"] and map[old_position]["FERTILITE"] > rand_num:

            map[new_pos]["ENERGY"] = map[new_pos]["ENERGY"] + parametre["ENERGY_REPRODUCTION"]
            map[old_position]["ENERGY"] = map[new_pos]["ENERGY"] + parametre["ENERGY_REPRODUCTION"]

            # Les personnages font un enfant.
            rand_num = random.randint(1,2)

            #Permet de faire en sorte que 2 personnages ne se reproduisent plus ensemble une fois qu'ils l'ont déja fait.
            map[old_position]["REPRODUCTION"].append(map[new_pos]["IDENTIFIANT"])
            map[new_pos]["REPRODUCTION"].append(map[old_position]["IDENTIFIANT"])

            #Mutation génétique aléatoire avec distribution gaussienne qui détermine les caractéristiques de l'enfant.
            vitesse_enfant = (0.5 * map[old_position]["SPEED"]) + (0.5 * map[new_pos]["SPEED"])
            variance = 0.1 * vitesse_enfant
            mutation = random.gauss(0, variance)
            vitesse_enfant += mutation

            force_enfant = (0.5 * map[old_position]["POWER"]) + (0.5 * map[new_pos]["POWER"])
            variance = 0.1 * force_enfant
            mutation = random.gauss(0, variance)
            force_enfant += mutation

            agilité_enfant = (0.5 * map[old_position]["AGILITY"]) + (0.5 * map[new_pos]["AGILITY"])
            variance = 0.1 * agilité_enfant
            mutation = random.gauss(0, variance)
            agilité_enfant += mutation

            fertilité_enfant = (0.5 * map[old_position]["FERTILITE"]) + (0.5 * map[new_pos]["FERTILITE"])
            variance = 0.1 * fertilité_enfant
            mutation = random.gauss(0, variance)
            fertilité_enfant += mutation

            vitesse_enfant = (0.5 * map[old_position]["SPEED"]) + (0.5 * map[new_pos]["SPEED"])
            variance = 0.1 * vitesse_enfant
            mutation = random.gauss(0, variance)
            vitesse_enfant += mutation      

            id_enfant = random.randint(0,100000000000000000000000000)

            #Prend une position de tente a l'endroit ou l'enfant est né.
            position_campement = hasard_camp()

            #Création d'un nouveau campement que cela soit pour un enfant ou un personnage.
            campement[f"{map[old_position]['objet']}{id_enfant}"] = {"position":position_campement,
                                                                        "objet":map[old_position]["objet"],
                                                                        "active":False,
                                                                        "parent": map[old_position]["IDENTIFIANT"],
                                                                        "baby":
                                                                                {"objet":map[old_position]["objet"],
                                                                                "IDENTIFIANT":f"{map[old_position]['objet']}{id_enfant}",
                                                                                "SPEED":vitesse_enfant,
                                                                                "POWER":force_enfant,
                                                                                "AGILITY":agilité_enfant,
                                                                                "FERTILITE":fertilité_enfant,
                                                                                "FOOD":1,
                                                                                "ENERGY":100,
                                                                                "MOVE":val_inter(position_campement,position_campement),
                                                                                "CAMP":position_campement,
                                                                                "REPRODUCTION": [map[old_position]["IDENTIFIANT"],map[new_pos]["IDENTIFIANT"]]
                                                                            }}
            #Caracteristiques de l'enfant.

            #Fait en sorte que les parents ne puissent pas se reproduire avec l'enfant. :O
            #map[old_position]["BABY"].append(data)
            map[old_position]["REPRODUCTION"].append(f"{map[old_position]['objet']}{id_enfant}")
            map[new_pos]["REPRODUCTION"].append(f"{map[old_position]['objet']}{id_enfant}")

            new_pos = old_position
            mise_a_jour(old_position,new_pos)
            return mort
        
        #Si ils se dont deja reproduit ensemble ou qu'ils sont sur le point de se reproduire avec leur enfant, continue le programme.
        else:
            response,liste_pos = filtre(next_to(old_position),param=solid+["player_red","player_blue"])
            if not response:
                return False
            new_pos = random.choice(liste_pos)
            
            

    # --- VITESSE --- #
    rand_num = random.randint(0,100)
    #Si sa variable speed est trop faible le personnage ne se déplace pas lors de ce tour.

    if map[old_position]["SPEED"] < rand_num and map[new_pos]["objet"] not in ["player_red","player_blue","food"]:
        new_pos = old_position
        mise_a_jour(old_position,new_pos)
        return mort



    mise_a_jour(old_position,new_pos)
    return mort



def move_pouleto(identifiant):
    """> Gère le déplacemeent des poulets.
    Entrée: identifiant
    Sortie: mort / False si le personnage est mort ou qu'il a nulle part ou aller."""
    mort = False

    #Récupération de la position actuelle du personnage à partir de son identifiant.
    try:
        old_position = [key for key, value in map.items() if value['IDENTIFIANT'] == identifiant][0]
    except:
        #Si le personnage n'a pas de position : cela veut dire qu'il est mort donc la fonction se termine en retournant False pour ne pas bloquer le programme.
        return False
    
    #Liste des cases disponibles
    liste_pos = next_to(old_position)
    response,liste_pos = filtre(liste_pos,param=solid+["player_red","player_blue","food"])

    #Permet de ne pas bloquer le programme quand un personnage à nulle part ou aller.
    if not response:
        return False

    #Prend une position au hasard parmis les positions ou le personnage peut se déplacer.
    new_pos = random.choice(liste_pos)    
    rand_num = random.randint(0,100)
    if map[old_position]["SPEED"] < rand_num:
        new_pos = old_position
    mise_a_jour(old_position,new_pos)
    return mort



def energy_compteur():
    mort = []
    """#Remet l'énergie à 100 (au max)."""
    for pos in map:
        if map[pos]["objet"] in ["player_red","player_blue"] and map[pos]["ENERGY"] > 1000:
            map[pos]["ENERGY"] = 100
        #Tue les personnages qui ont moins de 0 d'énergie.
        if map[pos]["objet"] in ["player_red","player_blue"] and map[pos]["ENERGY"] < 0:
            mort.append({pos:map[pos]["objet"]})
            map[pos] = {"objet":"grass","IDENTIFIANT":"grass"+str(id(map[pos]))}
    return mort



def restart(val=100):
    """> Remet à 100 l'energie des personnages qui sont rentrés à leur camp."""
    for pos in map:
        if map[pos]["objet"] in ["player_red","player_blue"] and pos == map[pos]["CAMP"]:
            map[pos]["ENERGY"] = val
    #Les personnages qui n'ont pas mangé au moins 1 poulet ne survivent pas.
    """for pos in map:
        if map[pos]["objet"] in ["player_red","player_blue"]:
            if map[pos]["FOOD"] == 0:
                map[pos] = {"objet":"grass","IDENTIFIANT":"grass"+str(id(map[pos]))}
            else:
                map[pos]["FOOD"] = 0"""

    
    
def mise_a_jour(old_position,new_pos):
    """> Transition fluide du personnage entre son déplacement d'une position à une autre.
    Entrée: old_position, new_pos
    Sortie: Null """
    val = val_inter(old_position,new_pos)

    #Mise a jour des coordonées.
    map[new_pos] = map[old_position].copy()
    map[new_pos]["MOVE"] = val

    #Si le personnage à bougé (evite que la case ou il se trouve se transforme en herbe).
    if new_pos != old_position:
        map[old_position] = {"objet":"grass","IDENTIFIANT":"grass"+str(id(map[old_position]))}
        map[new_pos]["ENERGY"] = map[new_pos]["ENERGY"] + parametre["ENERGY_MOVE"]
