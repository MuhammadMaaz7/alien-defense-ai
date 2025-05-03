import pygame
import pygame_gui
import os
import random
import time
import math
from datetime import datetime, timedelta
from station import Station
from ui import create_ui_manager, create_info_panel, update_info_panel
from game_logic import alien_attack, player_defend
from ai import minimax, evaluate_station
pygame.init()

# Constants
WIDTH, HEIGHT = 1200, 700
FPS = 60
GAME_DURATION = 300  # 5 minutes in seconds
MAX_AI_MEMORY = 3  # Remember last 3 attacks

# Initialize window
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Alien Defense - Strategic Stations")

# Load background layers
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

# Earth base position and representation
earth_base_pos = (WIDTH - 215, 20)
earth_base = type('EarthBase', (), {'pos': earth_base_pos})()  # Simple object to represent base

# Setup UI
manager = create_ui_manager((WIDTH, HEIGHT))
info_panel = create_info_panel(manager)
status_panel = pygame_gui.elements.UITextBox(
    relative_rect=pygame.Rect((20, 470), (250, 100)),
    html_text="Player's Turn<br>Select a station to defend",
    manager=manager
)
base_status_panel = pygame_gui.elements.UITextBox(
    relative_rect=pygame.Rect((WIDTH - 250, 250), (230, 100)),
    html_text="Base Resources:<br>Troops: 2000",
    manager=manager
)
ai_suggestion_panel = pygame_gui.elements.UITextBox(
    relative_rect=pygame.Rect((WIDTH - 250, 370), (230, 100)),
    html_text="AI Suggestion:<br>None",
    manager=manager
)
timer_panel = pygame_gui.elements.UITextBox(
    relative_rect=pygame.Rect((WIDTH - 250, 150), (230, 80)),
    html_text="Time Remaining: 05:00",
    manager=manager
)
troop_input = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect((WIDTH - 250, 480), (100, 30)),
    manager=manager
)
troop_input.set_text("0")
send_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((WIDTH - 140, 480), (120, 30)),
    text="Send Troops",
    manager=manager
)

# Generate station positions with minimum distances
def generate_station_positions(count, margin=180):
    positions = []
    max_attempts = 500
    forbidden_zones = [
        pygame.Rect(20, 150, 180, 300),  # Info panel area
        pygame.Rect(WIDTH - 215, 20, 200, 200)  # Earth base area
    ]

    while len(positions) < count and max_attempts > 0:
        x = random.randint(100, WIDTH - 200)
        y = random.randint(50, HEIGHT - 200)
        new_rect = pygame.Rect(x, y, 150, 150)

        # Check distance from existing stations and UI elements
        too_close = any(math.sqrt((x - px)**2 + (y - py)**2) < margin for px, py in positions) or \
                    any(new_rect.colliderect(zone) for zone in forbidden_zones)

        if not too_close:
            positions.append((x, y))
        max_attempts -= 1

    return positions

# Create stations with balanced initial values
station_count = random.randint(6, 9)
positions = generate_station_positions(station_count)
stations = []

for i, pos in enumerate(positions):
    name = f"Station {chr(65 + i)}"
    population = random.randint(2000, 5000)
    military = random.randint(100, 300) if random.random() < 0.7 else random.randint(0, 50)
    aliens = random.randint(15, 40) if random.random() < 0.7 else random.randint(0, 10)
    stations.append(Station(name, pos, population, military, aliens))
    stations[-1].update_damage()

# Initialize base resources
base_troops = 2000

# Game state
game_start_time = datetime.now()
game_over = False
player_won = None
last_ai_attacks = []  # Track last few attacks for AI memory

# Clock
clock = pygame.time.Clock()
running = True

# Game loop state
turn = "player"
selected_station = None
ai_delay_timer = 0
last_ai_attack_station = None

def check_game_over():
    global game_over, player_won
    
    # Check if all human stations are destroyed
    if all(s.population <= 0 for s in stations):
        game_over = True
        player_won = False
        return True
    
    # Check if all aliens are defeated
    if all(s.alien_count <= 0 for s in stations):
        game_over = True
        player_won = True
        return True
    
    # Check if base troops exhausted and no military left
    if base_troops <= 0 and all(s.military_population <= 0 for s in stations):
        game_over = True
        player_won = False
        return True
    
    # Check time expiration
    time_elapsed = (datetime.now() - game_start_time).total_seconds()
    if time_elapsed >= GAME_DURATION:
        game_over = True
        # Determine winner by comparing remaining forces
        total_humans = sum(s.population for s in stations)
        total_aliens = sum(s.alien_count for s in stations)
        original_pop = sum(s.original_population for s in stations)
        
        # Player wins if they have significant population advantage
        player_won = (total_humans > total_aliens * 3) or (total_aliens == 0)
        return True
    
    return False

def format_time(seconds):
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"

def draw_station_connections():
    """Draw lines showing station connections (for visualization)"""
    for station in stations:
        if station.alien_count > 0:
            pygame.draw.line(window, (255, 100, 100, 150), 
                           (station.pos[0] + 75, station.pos[1] + 75),
                           (earth_base_pos[0] + 100, earth_base_pos[1] + 100), 2)

# Game Loop
while running:
    dt = clock.tick(FPS) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        manager.process_events(event)

        if event.type == pygame.MOUSEBUTTONDOWN and turn == "player" and not game_over:
            mx, my = pygame.mouse.get_pos()
            for station in stations:
                x, y, w, h = station.get_rect()
                if x <= mx <= x + w and y <= my <= y + h:
                    selected_station = station
                    update_info_panel(info_panel, selected_station.get_info_html())
                    break

        if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == send_button and turn == "player" and not game_over:
            if selected_station:
                try:
                    reinforcements = int(troop_input.get_text())
                    if reinforcements > base_troops:
                        status_panel.set_text("Not enough troops at base.")
                    elif reinforcements <= 0:
                        status_panel.set_text("Enter a positive number of troops.")
                    else:
                        if player_defend(selected_station, reinforcements, earth_base):
                            base_troops -= reinforcements
                            update_info_panel(info_panel, selected_station.get_info_html())
                            status_panel.set_text(f"Sent {reinforcements} troops to {selected_station.name}")
                            turn = "ai"
                            ai_delay_timer = time.time() + 1  # 1 second delay for AI turn
                        else:
                            status_panel.set_text("Defense failed - no aliens at station")
                except ValueError:
                    status_panel.set_text("Enter a valid number of troops.")

    manager.update(dt)

    # Update timer
    time_elapsed = (datetime.now() - game_start_time).total_seconds()
    time_remaining = max(0, GAME_DURATION - time_elapsed)
    timer_panel.set_text(f"Time Remaining: {format_time(time_remaining)}")

    # Check game over conditions
    if not game_over and check_game_over():
        if player_won:
            status_panel.set_text("VICTORY! You successfully defended Earth!")
        else:
            status_panel.set_text("DEFEAT! The aliens have overrun our stations!")
        continue

    # AI Turn
    if turn == "ai" and time.time() > ai_delay_timer and not game_over:
        # Reset attack flags
        for s in stations:
            s.under_attack = False
            
        # Get AI decision with memory of last attacks
        ai_station, _ = minimax(stations, 4, False, float('-inf'), float('inf'), earth_base, last_ai_attacks)
        
        if ai_station and ai_station.population > 0 and ai_station.alien_count > 0:
            if alien_attack(ai_station, earth_base):
                # Record this attack for AI memory
                last_ai_attacks.append(ai_station)
                if len(last_ai_attacks) > MAX_AI_MEMORY:
                    last_ai_attacks.pop(0)
                
                update_info_panel(info_panel, ai_station.get_info_html())
                status_panel.set_text(f"AI attacked {ai_station.name}")
                last_ai_attack_station = ai_station
            else:
                status_panel.set_text("AI attack failed")
        else:
            status_panel.set_text("AI is regrouping forces")
        
        turn = "player"

    # Update base status
    base_status_panel.set_text(f"Base Resources:<br>Troops: {base_troops}")

    # Update AI suggestion for player
    suggested_station, _ = minimax(stations, 4, True, float('-inf'), float('inf'), earth_base, last_ai_attacks)
    if suggested_station:
        ai_suggestion_panel.set_text(f"AI Suggestion:<br>Defend {suggested_station.name}<br>Score: {evaluate_station(suggested_station, True, earth_base, last_ai_attacks):.1f}")

    # Draw background
    for layer in layer_images:
        window.blit(layer, (0, 0))

    window.blit(earth_base_img, earth_base_pos)

    # Draw station connections (visualization)
    draw_station_connections()

    # Draw stations
    for station in stations:
        x, y = station.pos
        window.blit(station_img, (x, y))
        
        # Draw attack indicator
        if station == last_ai_attack_station:
            pygame.draw.rect(window, (255, 0, 0, 150), (x, y, Station.WIDTH, 5))
        
        # Draw units
        if station.alien_count > 0:
            window.blit(alien_img, (x + 30, y + 90))
        if station.military_population > 0:
            window.blit(military_img, (x + 70, y + 20))
        
        # Draw damage indicator
        if station.damage > 0:
            damage_width = int(Station.WIDTH * (station.damage / 100))
            pygame.draw.rect(window, (255, 165, 0), (x, y + Station.HEIGHT - 10, damage_width, 5))
        
        # Draw distance indicator (faint line)
        pygame.draw.line(window, (100, 100, 255, 50),
                       (x + 75, y + 75),
                       (earth_base_pos[0] + 100, earth_base_pos[1] + 100), 1)

    # Draw game over screen
    if game_over:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        window.blit(overlay, (0, 0))
        
        font = pygame.font.SysFont('Arial', 72)
        if player_won:
            text = font.render("VICTORY!", True, (0, 255, 0))
        else:
            text = font.render("DEFEAT", True, (255, 0, 0))
        
        text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2))
        window.blit(text, text_rect)

        # Show summary
        font_sm = pygame.font.SysFont('Arial', 24)
        humans = sum(s.population for s in stations)
        aliens = sum(s.alien_count for s in stations)
        summary = font_sm.render(f"Humans: {humans} | Aliens: {aliens}", True, (255, 255, 255))
        window.blit(summary, (WIDTH//2 - 100, HEIGHT//2 + 50))

    manager.draw_ui(window)
    pygame.display.flip()

pygame.quit()
print("Game closed.")