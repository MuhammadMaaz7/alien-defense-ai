import pygame
import pygame_gui
import os

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60

# Setup window
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Alien Defense - Space Stations")

# Load and scale layered background images
layer_images = []
for i in range(1, 4):
    img_path = os.path.join("assets", f"layer_{i}.png")
    img = pygame.image.load(img_path).convert_alpha()
    img = pygame.transform.scale(img, (WIDTH, HEIGHT))
    layer_images.append(img)

# Setup UI Manager
manager = pygame_gui.UIManager((WIDTH, HEIGHT))

# Load icons
station_img = pygame.transform.scale(pygame.image.load("assets/station_1.png"), (150, 150))
alien_img = pygame.transform.scale(pygame.image.load("assets/alien.png"), (35, 35))
military_img = pygame.transform.scale(pygame.image.load("assets/military_yellow.png"), (50, 50))

# Sample station data
stations = [
    {'name': 'Station Alpha', 'pos': (100, 150), 'population': 5000, 'has_aliens': True, 'has_military': True},
    {'name': 'Station Beta', 'pos': (300, 350), 'population': 2000, 'has_aliens': False, 'has_military': True},
    {'name': 'Station Gamma', 'pos': (450, 200), 'population': 0, 'has_aliens': True, 'has_military': False}
]

# Info panel for clicked station
info_panel = pygame_gui.elements.UITextBox(
    relative_rect=pygame.Rect((600, 50), (180, 300)),
    html_text="Click a station",
    manager=manager
)

# Clock
clock = pygame.time.Clock()

# Game loop
running = True
while running:
    time_delta = clock.tick(FPS) / 1000.0

    # Draw all background layers
    for layer in layer_images:
        window.blit(layer, (0, 0))

    # Draw stations and their indicators
    for station in stations:
        x, y = station['pos']
        window.blit(station_img, (x, y))
        if station['has_aliens']:
            window.blit(alien_img, (x + 25, y + 50))
        if station['has_military']:
            window.blit(military_img, (x + 40, y + 10))

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Mouse click on station
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            for station in stations:
                x, y = station['pos']
                if x <= mx <= x+150 and y <= my <= y+150:  # Station icon bounds
                    info_text = f"""
<b>{station['name']}</b><br>
Population: {station['population']}<br>
Aliens: {'Yes' if station['has_aliens'] else 'No'}<br>
Military: {'Yes' if station['has_military'] else 'No'}<br>
"""
                    info_panel.set_text(info_text)

        manager.process_events(event)

    # Update and draw UI
    manager.update(time_delta)
    manager.draw_ui(window)

    # Flip display
    pygame.display.flip()

pygame.quit()