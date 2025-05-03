import random

class Station:
    WIDTH = 150
    HEIGHT = 150

    def __init__(self, name, pos, population, military_population, alien_count):
        self.name = name
        self.pos = pos
        self.population = population
        self.military_population = military_population
        self.alien_count = alien_count
        self.damage = 0

    def get_rect(self):
        x, y = self.pos
        return (x, y, self.WIDTH, self.HEIGHT)

    def get_info_html(self):
        return f"""
<b>{self.name}</b><br>
Population: {self.population}<br>
Military: {self.military_population}<br>
Aliens: {self.alien_count}<br>
Damage: {self.damage}%
"""