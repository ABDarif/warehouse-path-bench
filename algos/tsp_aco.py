from __future__ import annotations
from typing import List, Tuple, Callable, Dict
import random
import numpy as np
import time

class AntColonyOptimization:
    """Ant Colony Optimization for TSP with pheromone trail updates."""
    
    def __init__(self, dist_func, n_cities, start_city=0, n_ants=20, n_iterations=100, 
                 alpha=1.0, beta=2.0, evaporation_rate=0.5, q0=0.9, seed=42):
        self.dist_func = dist_func
        self.n_cities = n_cities
        self.start_city = start_city
        self.n_ants = n_ants
        self.n_iterations = n_iterations
        self.alpha = alpha  # pheromone importance
        self.beta = beta    # heuristic importance
        self.evaporation_rate = evaporation_rate
        self.q0 = q0        # exploitation probability
        
        # Initialize pheromone matrix
        self.pheromones = np.ones((n_cities, n_cities))
        
        # Initialize heuristic matrix (inverse of distance)
        self.heuristics = np.zeros((n_cities, n_cities))
        for i in range(n_cities):
            for j in range(n_cities):
                if i != j:
                    self.heuristics[i, j] = 1.0 / max(0.001, dist_func(i, j))
        
        self.rng = random.Random(seed)
        np.random.seed(seed)
        
    def construct_solution(self, ant_id):
        """Construct a solution for one ant using probabilistic selection."""
        tour = [self.start_city]
        unvisited = set(range(self.n_cities)) - {self.start_city}
        current = self.start_city
        
        while unvisited:
            if self.rng.random() < self.q0:
                # Exploitation: choose best city
                best_city = max(unvisited, key=lambda city: 
                    self.pheromones[current, city] ** self.alpha * 
                    self.heuristics[current, city] ** self.beta)
                next_city = best_city
            else:
                # Exploration: probabilistic selection
                probabilities = []
                for city in unvisited:
                    prob = (self.pheromones[current, city] ** self.alpha * 
                           self.heuristics[current, city] ** self.beta)
                    probabilities.append(prob)
                
                # Normalize probabilities
                total_prob = sum(probabilities)
                if total_prob > 0:
                    probabilities = [p / total_prob for p in probabilities]
                    next_city = np.random.choice(list(unvisited), p=probabilities)
                else:
                    next_city = self.rng.choice(list(unvisited))
            
            tour.append(next_city)
            unvisited.remove(next_city)
            current = next_city
        
        return tour
    
    def calculate_tour_length(self, tour):
        """Calculate total length of a tour."""
        total_length = 0.0
        for i in range(len(tour) - 1):
            total_length += self.dist_func(tour[i], tour[i+1])
        # Add return to start
        total_length += self.dist_func(tour[-1], tour[0])
        return total_length
    
    def update_pheromones(self, solutions, best_solution):
        """Update pheromone trails."""
        # Evaporate existing pheromones
        self.pheromones *= (1.0 - self.evaporation_rate)
        
        # Add pheromones for each solution
        for tour in solutions:
            tour_length = self.calculate_tour_length(tour)
            pheromone_deposit = 1.0 / max(0.001, tour_length)
            
            for i in range(len(tour) - 1):
                city1, city2 = tour[i], tour[i+1]
                self.pheromones[city1, city2] += pheromone_deposit
                self.pheromones[city2, city1] += pheromone_deposit
            
            # Return to start
            self.pheromones[tour[-1], tour[0]] += pheromone_deposit
            self.pheromones[tour[0], tour[-1]] += pheromone_deposit
        
        # Additional pheromone for best solution
        if best_solution:
            best_length = self.calculate_tour_length(best_solution)
            best_pheromone = 1.0 / max(0.001, best_length)
            
            for i in range(len(best_solution) - 1):
                city1, city2 = best_solution[i], best_solution[i+1]
                self.pheromones[city1, city2] += best_pheromone
                self.pheromones[city2, city1] += best_pheromone
            
            self.pheromones[best_solution[-1], best_solution[0]] += best_pheromone
            self.pheromones[best_solution[0], best_solution[-1]] += best_pheromone
    
    def solve(self, time_budget_ms=None):
        """Run the ACO algorithm."""
        start_time = time.time()
        best_tour = None
        best_length = float('inf')
        
        for iteration in range(self.n_iterations):
            # Check time budget
            if time_budget_ms and (time.time() - start_time) * 1000 > time_budget_ms:
                break
            
            # Construct solutions for all ants
            solutions = []
            for ant in range(self.n_ants):
                tour = self.construct_solution(ant)
                solutions.append(tour)
                
                # Update best solution
                tour_length = self.calculate_tour_length(tour)
                if tour_length < best_length:
                    best_length = tour_length
                    best_tour = tour.copy()
            
            # Update pheromones
            self.update_pheromones(solutions, best_tour)
        
        return best_tour, best_length

def aco_tsp(dist_func, n_cities, start_city=0, n_ants=20, n_iterations=100, 
            alpha=1.0, beta=2.0, evaporation_rate=0.5, time_budget_ms=None, seed=42):
    """Ant Colony Optimization for TSP."""
    aco = AntColonyOptimization(
        dist_func=dist_func,
        n_cities=n_cities,
        start_city=start_city,
        n_ants=n_ants,
        n_iterations=n_iterations,
        alpha=alpha,
        beta=beta,
        evaporation_rate=evaporation_rate,
        seed=seed
    )
    
    best_tour, best_length = aco.solve(time_budget_ms=time_budget_ms)
    return best_tour, best_length
