import math
from typing import List, Tuple, Optional
from station import Station

# Global variables to maintain state between function calls
last_attacks = []
MAX_AI_MEMORY = 3

def evaluate_station(station: Station, is_player: bool, base_station, memory_attacks=None) -> int:
    """Priority evaluation function that always returns a positive integer (≥1)."""
    global last_attacks

    # Use provided memory if available, otherwise use global
    recent_attacks = memory_attacks if memory_attacks is not None else last_attacks

    # Calculate distance penalty (normalized between 0 and 1)
    if not hasattr(station, 'distance_from_base') or station.distance_from_base == 0:
        dx = station.pos[0] - base_station.pos[0]
        dy = station.pos[1] - base_station.pos[1]
        distance = math.sqrt(dx * dx + dy * dy)
        distance_penalty = distance / 1500
    else:
        distance_penalty = station.distance_from_base / 1500

    distance_penalty = min(max(distance_penalty, 0), 1)

    # Evaluation score before clamping
    if is_player:
        raw_score = (
            (station.population / 800) * 5.0 +
            (station.alien_count * 3.0) +
            (station.damage * 1.5) -
            (station.military_population * 0.3) -
            (distance_penalty * 2.0) -
            (30 if station in recent_attacks else 0)
        )
    else:
        raw_score = (
            (station.population / 600) * 5.0 -
            (station.military_population * 2.5) +
            (station.alien_count * 2.0) -
            (station.damage * 0.8) -
            (distance_penalty * 1.5) +
            (20 if station in recent_attacks else 0)
        )

    # Ensure result is a positive integer ≥ 1
    priority_score = max(1, round(raw_score))

    return priority_score


def minimax(stations: List[Station], depth: int, is_maximizing: bool,
           alpha: float, beta: float, base_station, memory_attacks=None) -> Tuple[Optional[Station], float]:
    """Minimax algorithm with alpha-beta pruning
    
    Args:
        stations: List of all stations in the game
        depth: Maximum search depth
        is_maximizing: True if maximizing player's turn, False if minimizing
        alpha: Alpha value for pruning
        beta: Beta value for pruning
        base_station: Reference to the base station
        memory_attacks: List of recently attacked stations (optional)
    
    Returns:
        Tuple with (best_station, best_value)
    """
    global last_attacks
    
    # Use provided memory if available, otherwise use global
    recent_attacks = memory_attacks if memory_attacks is not None else last_attacks
    
    # Base case: terminal node or depth limit
    if depth == 0 or is_terminal_state(stations):
        return evaluate_terminal(stations, is_maximizing, base_station, recent_attacks)
        
    best_station = None
    
    # Initialize best value based on maximizing/minimizing player
    best_value = float('-inf') if is_maximizing else float('inf')
    
    # Get valid candidates (stations that can be attacked/defended)
    candidates = get_valid_candidates(stations, is_maximizing)
    
    # If no valid candidates, return a neutral evaluation
    if not candidates:
        return None, 0
    
    for station in candidates:
        # Save original state before simulation
        original_state = {
            'aliens': station.alien_count,
            'military': station.military_population,
            'population': station.population,
            'damage': station.damage
        }
        
        # Simulate the move
        simulate_attack(station, is_maximizing)
        
        # Recursive call with alternating players
        _, current_value = minimax(
            stations, depth-1, not is_maximizing, alpha, beta, base_station, recent_attacks
        )
        
        # Undo simulation to restore state
        undo_simulation(station, original_state)
        
        # Update best value and station
        if is_maximizing:
            if current_value > best_value:
                best_value = current_value
                best_station = station
            alpha = max(alpha, best_value)
        else:
            if current_value < best_value:
                best_value = current_value
                best_station = station
            beta = min(beta, best_value)
        
        # Alpha-beta pruning
        if beta <= alpha:
            break
            
    return best_station, best_value

def is_terminal_state(stations: List[Station]) -> bool:
    """Check if game ending condition reached"""
    # Game ends if all stations are destroyed or all aliens eliminated
    return (all(s.population <= 0 for s in stations) or
            all(s.alien_count <= 0 for s in stations))

def evaluate_terminal(stations: List[Station], 
                    is_player: bool, base_station, memory_attacks=None) -> Tuple[Optional[Station], float]:
    """Evaluate terminal node with win/loss considerations"""
    # Check for game over conditions with proper win/loss values
    if all(s.population <= 0 for s in stations):
        # All stations destroyed - bad for player
        return None, float('-inf') if is_player else float('inf')
    
    if all(s.alien_count <= 0 for s in stations):
        # All aliens eliminated - good for player
        return None, float('inf') if is_player else float('-inf')
    
    # Not a terminal state, evaluate best station
    candidates = [s for s in stations 
                 if (is_player and s.population > 0) or 
                 (not is_player and s.alien_count > 0)]
    
    if not candidates:
        return None, 0
        
    best_station = max(candidates, 
                      key=lambda s: evaluate_station(s, is_player, base_station, memory_attacks))
    return best_station, evaluate_station(best_station, is_player, base_station, memory_attacks)

def get_valid_candidates(stations: List[Station], 
                       is_player: bool) -> List[Station]:
    """Get stations that can be attacked/defended"""
    if is_player:
        # Player defends stations with population remaining and alien threat
        return [s for s in stations if s.population > 0 and s.alien_count > 0]
    else:
        # Aliens attack stations with population remaining
        return [s for s in stations if s.population > 0]

def simulate_attack(station: Station, is_player: bool):
    """Simulate an attack or defense outcome with more realistic impact"""
    if not is_player:
        # Simulate alien attack
        military_reduction = int(station.military_population * 0.3)
        population_reduction = int(station.population * 0.2)
        
        station.military_population = max(0, station.military_population - military_reduction)
        station.population = max(0, station.population - population_reduction)
        station.damage += 10  # Increase damage when attacked
    else:
        # Simulate player defense
        alien_reduction = int(station.alien_count * 0.4)
        station.alien_count = max(0, station.alien_count - alien_reduction)

def undo_simulation(station: Station, original_state: dict):
    """Revert simulation changes"""
    station.alien_count = original_state['aliens']
    station.military_population = original_state['military']
    station.population = original_state['population']
    station.damage = original_state['damage']

def get_ai_decision(stations: List[Station], 
                   base_station, is_player_turn: bool) -> Station:
    """Get AI decision with proper depth scaling
    
    Args:
        stations: List of all stations in the game
        base_station: Reference to the base station
        is_player_turn: True if player's turn, False if AI's turn
    
    Returns:
        The station chosen for attack/defense
    """
    global last_attacks
    
    # Adjust depth based on number of stations for performance
    depth = min(4, max(2, len(stations) // 2))
    
    # In minimax, the AI wants to minimize when it's the player's turn,
    # and maximize when it's the AI's turn
    best_station, _ = minimax(
        stations, depth, not is_player_turn, 
        float('-inf'), float('inf'), base_station, last_attacks
    )
    
    # Record AI attacks for memory-based decisions
    if not is_player_turn and best_station:
        last_attacks.append(best_station)
        if len(last_attacks) > MAX_AI_MEMORY:
            last_attacks.pop(0)
            
    return best_station