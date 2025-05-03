import random

def calculate_path_cost(station1, station2):
    """Calculate distance between two stations"""
    return ((station1.pos[0]-station2.pos[0])**2 + (station1.pos[1]-station2.pos[1])**2)**0.5

def alien_attack(station, base_station):
    if station.alien_count <= 0:
        return False
    
    # Scale attack effectiveness by distance (farther = weaker)
    distance_factor = min(1, station.distance_from_base / 1000)
    
    if station.military_population > 0:
        # Military engagement
        military_loss = int(station.military_population * random.uniform(0.3, 0.5) * distance_factor)
        alien_loss = int(station.alien_count * random.uniform(0.25, 0.4))
        
        station.military_population = max(0, station.military_population - military_loss)
        station.alien_count = max(0, station.alien_count - alien_loss)
        
        # Collateral damage
        pop_loss = int(station.population * random.uniform(0.1, 0.2) * distance_factor)
    else:
        # Civilian massacre
        pop_loss = int(station.population * random.uniform(0.5, 0.7) * (1.5 - distance_factor))
    
    station.population = max(0, station.population - pop_loss)
    station.update_damage()
    return True

def player_defend(station, reinforcements, base_station):
    if reinforcements <= 0:
        return False
    
    # Distance factor (farther = less effective)
    distance_factor = max(0.5, 1 - (station.distance_from_base / 1500))
    effective_reinforcements = int(reinforcements * distance_factor)
    
    total_military = station.military_population + effective_reinforcements
    
    alien_loss = int(station.alien_count * random.uniform(0.6, 0.8) * distance_factor)
    military_loss = int(total_military * random.uniform(0.2, 0.35))
    
    station.alien_count = max(0, station.alien_count - alien_loss)
    station.military_population = max(0, total_military - military_loss)
    
    station.update_damage()
    return True