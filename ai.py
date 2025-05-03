import math


def evaluate_station(station, is_player, base_station, last_attacks=[]):
    # Distance penalty (0-1 normalized)
    distance_penalty = station.distance_from_base / 1500
    
    if is_player:
        # Defense heuristic
        score = (
            (station.population / 1000) +            # Population value
            (station.alien_count * 3) -              # Alien threat
            (station.military_population * 0.7) +    # Existing defense
            (station.damage * 0.8) -                # Urgency
            (distance_penalty * 2) -                # Distance cost
            (50 if station in last_attacks else 0)  # Recent attack penalty
        )
    else:
        # Attack heuristic
        score = (
            (station.population / 800) -            # Target value
            (station.military_population * 2) +      # Defense resistance
            (station.alien_count * 1.5) -           # Existing forces
            (station.damage * 0.5) -                # Already damaged
            (distance_penalty * 1.5) +             # Distance cost
            (30 if station in last_attacks else 0)  # Recent attack bonus
        )
    return score

def minimax(stations, depth, is_maximizing, alpha, beta, base_station, last_attacks):
    if depth == 0 or all(s.population <= 0 for s in stations) or all(s.alien_count <= 0 for s in stations):
        candidates = [s for s in stations if (is_maximizing and s.alien_count > 0) or 
                                          (not is_maximizing and s.population > 0)]
        if not candidates:
            return None, 0
        best = max(candidates, key=lambda s: evaluate_station(s, is_maximizing, base_station, last_attacks))
        return best, evaluate_station(best, is_maximizing, base_station, last_attacks)

    if is_maximizing:
        max_eval = float('-inf')
        best_station = None
        candidates = [s for s in stations if s.alien_count > 0 and s.population > 0]
        
        for station in candidates:
            eval = evaluate_station(station, True, base_station, last_attacks)
            if eval > max_eval:
                max_eval = eval
                best_station = station
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return best_station, max_eval
    else:
        min_eval = float('inf')
        best_station = None
        candidates = [s for s in stations if s.population > 0]
        
        for station in candidates:
            eval = evaluate_station(station, False, base_station, last_attacks)
            if eval < min_eval:
                min_eval = eval
                best_station = station
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return best_station, min_eval