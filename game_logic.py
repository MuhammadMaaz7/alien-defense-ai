import random
import math

def alien_attack(station,base_station):
    """
    Aliens attack the station with decisive outcomes
    Returns True if attack was successful, False otherwise
    """
    if station.alien_count <= 0:
        return False  # No aliens to attack
    
    station.under_attack = True
    
    # Determine if aliens can completely overrun the station
    if station.military_population > 0:
        # Military engagement - decisive battle
        military_ratio = station.military_population / (station.alien_count + 1)
        
        if random.random() < 0.7 * (1 - math.exp(-military_ratio)):
            # Military holds - eliminate all aliens
            station.alien_count = 0
            # Military takes 30-50% losses
            station.military_population = int(station.military_population * random.uniform(0.5, 0.7))
            # 10-20% civilian casualties
            station.population = int(station.population * random.uniform(0.8, 0.9))
        else:
            # Military overrun - eliminate all military
            station.military_population = 0
            # Aliens take 30-50% losses
            station.alien_count = int(station.alien_count * random.uniform(0.5, 0.7))
            # 50-70% civilian casualties
            station.population = int(station.population * random.uniform(0.3, 0.5))
    else:
        # No military - check if civilians can resist
        if random.random() < 0.1:  # Small chance civilians resist
            # Civilians fight back - eliminate all aliens
            station.alien_count = 0
            # Heavy civilian losses (70-90%)
            station.population = int(station.population * random.uniform(0.1, 0.3))
        else:
            # Complete civilian massacre
            station.population = 0
    
    station.update_damage()
    return True

def player_defend(station, reinforcements, base_station):
    """
    Player sends reinforcements for decisive defense
    Returns True if defense was successful, False otherwise
    """
    if reinforcements <= 0 or station.alien_count <= 0:
        return False
    
    # Distance factor (farther = less effective, min 40% effectiveness)
    distance_factor = max(0.4, 1 - (station.distance_from_base / 2000))
    effective_reinforcements = int(reinforcements * distance_factor)
    
    total_military = station.military_population + effective_reinforcements
    
    # Determine if defense can completely eliminate aliens
    defense_ratio = total_military / (station.alien_count + 1)
    
    if random.random() < 0.8 * (1 - math.exp(-defense_ratio)):
        # Successful defense - eliminate all aliens
        station.alien_count = 0
        # Military takes 20-40% losses
        station.military_population = int(total_military * random.uniform(0.6, 0.8))
        # Civilians protected (5-15% growth)
        station.population = int(station.population * random.uniform(1.05, 1.15))
    else:
        # Failed defense - aliens remain
        # Aliens take 50-70% losses
        station.alien_count = int(station.alien_count * random.uniform(0.3, 0.5))
        # Military takes 40-60% losses
        station.military_population = int(total_military * random.uniform(0.4, 0.6))
        # Civilians take 10-20% losses
        station.population = int(station.population * random.uniform(0.8, 0.9))
    
    station.update_damage()
    return True