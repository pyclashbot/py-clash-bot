from os.path import dirname, join
import random


from client import get_file_count, screenshot
from image_rec import check_for_location, find_references


#Method to get an array of images of the 4 cards
def get_card_images():
    card_screenshots=[
        screenshot(region=[124,571,60,74]),
        screenshot(region=[193,571,59,74]),
        screenshot(region=[261,571,60,74]),
        screenshot(region=[330,571,60,74]),
    ]
    return card_screenshots


#Method to check for a card in a given image 
#intended for use during the battle but may work elsewhere??
def check_for_card(image=None,card_name=""):
    folder_str="check_if_card_is_"+card_name
    
    references= make_reference_image_list(get_file_count(join(dirname(__file__), "reference_images","check_if_card_is_"+card_name)))


    locations = find_references(
        screenshot=image,
        folder=folder_str,
        names=references,
        tolerance=0.97
    )

    return check_for_location(locations)


#Method to make a reference array of a given size
def make_reference_image_list(size):
    reference_image_list=[]
    
    for n in range(size):
        n=n+1
        image_name= str(n)+'.png'
        reference_image_list.append(image_name)
    
    return reference_image_list
        
        
#Method to return an list of 4 identified cards
def identify_cards():
    #make return array
    card_list=[]
    
    #get card images
    card_images=get_card_images()
    
    #fill out return array
    for image in card_images:
        card_list.append(identify_card(image))
    
    return card_list
    
    
#Method to identify a card given an image
def identify_card(image):
    #make a list of cards the bot knows about
    card_list=[
        "arrows",
        "barbbarrel",
        "wallbreakers",
        "princess",
        "miner",
        "skeletonbarrel",
        "goblinbarrel",
        "hog",
        "battleram",
        "bombtower",
        "cannon",
        "clone",
        "earthquake",
        "goblindrill",
        "goblincage",
        "ramrider",
        "royalhogs",
        "graveyard",
        "elixerpump",
        "furnace",
        "barbhut",
        "fireball",
        "freeze",
        "tombstone",
        "goblinhut",
        "infernotower",
        "lightning",
        "log",
        "mortar",
        "poison",
        "rage",
        "rocket",
        "snowball",
        "tesla",
        "tornado",
        "xbow",
        "zap",
    ]
    
    for card in card_list:
        if check_for_card(image,card):
            return card
    return "unknown"




    
#Method to identify the card group of the given card
def get_card_group(card_identification):
    #make lists of card groups
    turret_cards=[
        "turret_cards",
        "bombtower",
        "cannon",
        "infernotower",
        "tesla",
        "goblincage",
    ]
    
    spell_cards=[
        "spell_cards",
        "arrows",
        "earthquake",
        "fireball",
        "freeze",
        "lightning",
        "poison",
        "rocket",
        "snowball",
        "tornado",
        "zap",
        "freeze",
    ]
    
    hog_cards=[
        "hog_cards",
        "hog",
        "battleram",
        "ramrider",
        "royalhogs",
    ]
    
    spawner_cards=[
        "spawner_cards",
        "goblinhut",
        "tombstone",
        "barbhut",
        "furnace",
        
        
    ]
    
    princess_cards=[
        "princess_cards",
        "skeletonbarrel",
        "princess",
        "barbbarrel",
        "log",
    ]
    
    miner_cards=[
        "miner_cards",
        "miner",
        "goblindrill",
    ]
    
    goblin_barrel_cards=[
        "goblin_barrel_cards",
        "goblinbarrel",
        "graveyard",
    ]
    
    wall_breaker_cards=[
        "wall_breaker_cards",
        "wallbreakers",
    ]
    
    friendly_spell_cards=[
        "friendly_spell_cards",
        "clone",
        "rage",
    ]
    
    xbow_cards=[
        "xbow_cards",
        "xbow",
    ]
    
    mortar_cards=[
        "mortar_cards",
        "mortar",
    ]
    
    elixer_pump_cards=[
        "elixer_pump_cards",
        "elixerpump",
    ]
    
    card_list_list=[
        turret_cards,
        spell_cards,
        hog_cards,
        spawner_cards,
        princess_cards,
        miner_cards,
        goblin_barrel_cards,
        wall_breaker_cards,
        friendly_spell_cards,
        xbow_cards,
        mortar_cards,
        elixer_pump_cards,
    ]
    
    for card_list in card_list_list:
        if card_identification in card_list:
            return card_list[0]
    return "regular"



#Method to get a list of play coords for a given card group
def get_play_coords(card_group):
    turret_cards_coords=[
        [217,371],
        [236,383]
    ]
    
    spell_cards_coords=[
        [132,210],
        [136,161],
        [314,173],
        [312,210],
    ]
    
    hog_cards_coords=[
        [94,335],
        [147,339],
        [293,334],
        [344,330],
    ]
    
    spawner_cards_coords=[
        [303,485],
        [375,491],
        [147,485],
        [87,479],
    ]
    
    princess_cards_coords=[
        [94,335],
        [147,339],
        [293,334],
        [344,330],
    ]
    
    miner_cards_coords=[
        [94,190],
        [140,210],
        [155,184],
        [310,210],
        [342,188],
        [285,188],
    ]
    
    goblin_barrel_cards_coords=[
        [135,192],
        [308,192],
    ]
    
    wall_breaker_cards_coords=[
        [221,330],
        [221,330],
        [221,330],
        [138,328],
        [306,332],
    ]
    
    friendly_spell_cards_coords=[
        [134,398],
        [315,405],
    ]
    
    xbow_cards_coords=[
        [191,328],
        [289,335],
    ]
    
    mortar_cards_coords=[
        [289,335],
        [179,332],
    ]
    
    elixer_pump_cards_coords=[
        [303,485],
        [375,491],
        [147,485],
        [87,479],
    ]

    if card_group=="turret_cards":
        #print("Returning turret card coords")
        return turret_cards_coords
    
    if card_group=="spell_cards":
        #print("Returning spell card coords")
        return spell_cards_coords
    
    if card_group=="hog_cards":
        #print("Returning hog card coords")
        return hog_cards_coords
    
    if card_group=="spawner_cards":
        #print("Returning spawner card coords")
        return spawner_cards_coords
    
    if card_group=="princess_cards":
        #print("Returning princess card coords")
        return princess_cards_coords
    
    if card_group=="miner_cards":
        #print("Returning miner card coords")
        return miner_cards_coords
    
    if card_group=="goblin_barrel_cards":
        #print("Returning goblin barrel card coords")
        return goblin_barrel_cards_coords
    
    if card_group=="wall_breaker_cards":
        #print("Returning wall breaker card coords")
        return wall_breaker_cards_coords
    
    if card_group=="friendly_spell_cards":
        #print("Returning friendly spell card coords")
        return friendly_spell_cards_coords
    
    if card_group=="xbow_cards":
        #print("Returning xbow card coords")
        return xbow_cards_coords
    
    if card_group=="mortar_cards":
        #print("Returning mortar card coords")
        return mortar_cards_coords
    
    if card_group=="elixer_pump_cards":
        #print("Returning elixer pump card coords")
        return elixer_pump_cards_coords

    return [
        [94,335],
        [147,339],
        [293,334],
        [344,330],
        [303,485],
        [375,491],
        [147,485],
        [87,479],
    ]