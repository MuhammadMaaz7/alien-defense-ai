import math

class Station:
    WIDTH = 150
    HEIGHT = 150
    
    def __init__(self, name, pos, population, military_population, alien_count):
        self.name = name
        self.pos = pos
        self.original_population = population
        self.population = population
        self.military_population = military_population
        self.alien_count = alien_count
        self.damage = 0
        self.under_attack = False
        self.distance_from_base = math.sqrt((pos[0]-1000)**2 + (pos[1]-100)**2)  # Distance from resource base

    def get_rect(self):
        return (*self.pos, self.WIDTH, self.HEIGHT)

    def get_info_html(self):
        return f"""<b>{self.name}</b><br>
Population: {self.population}<br>
Military: {self.military_population}<br>
Aliens: {self.alien_count}<br>
Damage: {self.damage}%<br>
Distance: {int(self.distance_from_base)}px"""

    def update_damage(self):
        """Calculate damage based on population loss"""
        if self.original_population == 0:
            self.damage = 0
        else:
            pop_lost = self.original_population - self.population
            self.damage = min(100, int((pop_lost / self.original_population) * 100))