import pygame
import pygame_gui
import os
import random

from station import Station
from ui import create_ui_manager, create_info_panel, update_info_panel

pygame.init()

# Constants
WIDTH, HEIGHT = 1200, 700
FPS = 60

# Init window
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Alien Defense - Random Stations")

# Backgrounds
layer_images = []
for i in range(1, 4):
    path = os.path.join("assets", f"layer_{i}.png")
    img = pygame.image.load(path).convert_alpha()
    img = pygame.transform.scale(img, (WIDTH, HEIGHT))
    layer_images.append(img)

# Load images
station_img = pygame.transform.scale(pygame.image.load("assets/station_1.png"), (150, 150))
alien_img = pygame.transform.scale(pygame.image.load("assets/alien.png"), (35, 35))
military_img = pygame.transform.scale(pygame.image.load("assets/military_yellow.png"), (50, 50))
earth_base_img = pygame.transform.scale(pygame.image.load("assets/resource.png"), (200, 200))

# Earth base position (top-right corner)
earth_base_pos = (WIDTH - 215, 20)

# Setup UI
manager = create_ui_manager((WIDTH, HEIGHT))
info_panel = create_info_panel(manager)

# Function to generate random non-overlapping station positions
def generate_station_positions(count, margin=180):
    positions = []
    max_attempts = 500

    # Define "forbidden" areas as pygame.Rects
    forbidden_zones = [
        pygame.Rect(20, 150, 180, 300),                       # Info panel
        pygame.Rect(WIDTH - 215, 20, 200, 200)               # Earth base
    ]

    while len(positions) < count and max_attempts > 0:
        x = random.randint(100, WIDTH - 200)
        y = random.randint(50, HEIGHT - 200)
        new_rect = pygame.Rect(x, y, 150, 150)  # Station size

        # Check against other stations
        too_close = False
        for px, py in positions:
            if abs(x - px) < margin and abs(y - py) < margin:
                too_close = True
                break

        # Check against UI elements
        for zone in forbidden_zones:
            if new_rect.colliderect(zone):
                too_close = True
                break

        if not too_close:
            positions.append((x, y))

        max_attempts -= 1

    return positions

# Generate stations
station_count = random.randint(5, 8)
positions = generate_station_positions(station_count)
stations = []

for i, pos in enumerate(positions):
    name = f"Station {chr(65 + i)}"
    population = random.randint(1000, 5000)
    military = random.randint(0, 200)
    aliens = random.randint(0, 30)
    stations.append(Station(name, pos, population, military, aliens))

# Clock
clock = pygame.time.Clock()
running = True

# Game loop
while running:
    dt = clock.tick(FPS) / 1000.0

    # Draw layers
    for layer in layer_images:
        window.blit(layer, (0, 0))

    # Draw Earth base
    window.blit(earth_base_img, earth_base_pos)

    # Draw stations
    for station in stations:
        x, y = station.pos
        window.blit(station_img, (x, y))
        if station.alien_count > 0:
            window.blit(alien_img, (x + 30, y + 90))
        if station.military_population > 0:
            window.blit(military_img, (x + 70, y + 20))

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            for station in stations:
                x, y, w, h = station.get_rect()
                if x <= mx <= x + w and y <= my <= y + h:
                    update_info_panel(info_panel, station.get_info_html())

        manager.process_events(event)

    manager.update(dt)
    manager.draw_ui(window)
    pygame.display.flip()

pygame.quit()
