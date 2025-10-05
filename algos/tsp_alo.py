from __future__ import annotations
from typing import List, Tuple, Callable
import random
import numpy as np
import time

class AntLionOptimization:
    """Ant Lion Optimization for TSP with adaptive search behavior."""
    
    def __init__(self, dist_func, n_cities, start_city=0, n_ants=30, n_iterations=100, 
                 seed=42):
        self.dist_func = dist_func
        self.n_cities = n_cities
        self.start_city = start_city
        self.n_ants = n_ants
        self.n_iterations = n_iterations
        
        self.rng = random.Random(seed)
        np.random.seed(seed)
        
        # Initialize ant lions (elite positions)
        self.ant_lions = []
        self.ant_lion_fitness = []
        
        # Initialize ants (search agents)
        self.ants = []
        self.ant_fitness = []
        
    def generate_random_tour(self):
        """Generate a random tour starting from start_city."""
        cities = list(range(self.n_cities))
        cities.remove(self.start_city)
        self.rng.shuffle(cities)
        return [self.start_city] + cities
    
    def calculate_tour_length(self, tour):
        """Calculate total length of a tour."""
        total_length = 0.0
        for i in range(len(tour) - 1):
            total_length += self.dist_func(tour[i], tour[i+1])
        # Add return to start
        total_length += self.dist_func(tour[-1], tour[0])
        return total_length
    
    def initialize_population(self):
        """Initialize ant lions and ants populations."""
        # Initialize ant lions
        for _ in range(self.n_ants):
            tour = self.generate_random_tour()
            fitness = self.calculate_tour_length(tour)
            self.ant_lions.append(tour.copy())
            self.ant_lion_fitness.append(fitness)
        
        # Initialize ants
        for _ in range(self.n_ants):
            tour = self.generate_random_tour()
            fitness = self.calculate_tour_length(tour)
            self.ants.append(tour.copy())
            self.ant_fitness.append(fitness)
    
    def tournament_selection(self, k=3):
        """Tournament selection to choose ant lion."""
        candidates = self.rng.sample(range(self.n_ants), min(k, self.n_ants))
        best_idx = min(candidates, key=lambda i: self.ant_lion_fitness[i])
        return best_idx
    
    def roulette_wheel_selection(self):
        """Roulette wheel selection based on fitness."""
        # Convert fitness to selection probability (lower fitness = higher probability)
        max_fitness = max(self.ant_lion_fitness)
        probabilities = [max_fitness - fitness + 1e-6 for fitness in self.ant_lion_fitness]
        total_prob = sum(probabilities)
        probabilities = [p / total_prob for p in probabilities]
        
        return np.random.choice(range(self.n_ants), p=probabilities)
    
    def adaptive_walk(self, ant_idx, iteration):
        """Perform adaptive random walk around selected ant lion."""
        # Select ant lion using tournament or roulette wheel
        if self.rng.random() < 0.5:
            ant_lion_idx = self.tournament_selection()
        else:
            ant_lion_idx = self.roulette_wheel_selection()
        
        ant_lion = self.ant_lions[ant_lion_idx]
        
        # Calculate adaptive bounds based on iteration
        I = 1 if iteration <= 0.1 * self.n_iterations else 1 + 100 * (iteration / self.n_iterations)
        
        # Perform random walk with adaptive bounds
        new_ant = ant_lion.copy()
        
        # Apply mutations based on iteration progress
        mutation_rate = 0.3 * (1 - iteration / self.n_iterations)  # Decrease over time
        
        for i in range(1, len(new_ant)):  # Skip start city
            if self.rng.random() < mutation_rate:
                # Swap with random position
                j = self.rng.randint(1, len(new_ant) - 1)
                new_ant[i], new_ant[j] = new_ant[j], new_ant[i]
        
        # Additional local search
        if self.rng.random() < 0.2:
            new_ant = self.two_opt_improve(new_ant)
        
        return new_ant
    
    def two_opt_improve(self, tour):
        """Apply 2-opt improvement."""
        best_tour = tour.copy()
        best_length = self.calculate_tour_length(best_tour)
        improved = True
        
        while improved:
            improved = False
            for i in range(1, len(best_tour) - 1):
                for j in range(i + 1, len(best_tour)):
                    # Create new tour by reversing segment
                    new_tour = best_tour[:i] + best_tour[i:j+1][::-1] + best_tour[j+1:]
                    new_length = self.calculate_tour_length(new_tour)
                    
                    if new_length < best_length:
                        best_tour = new_tour
                        best_length = new_length
                        improved = True
                        break
                if improved:
                    break
        
        return best_tour
    
    def update_ant_lions(self):
        """Update ant lions based on ant performance."""
        for i in range(self.n_ants):
            if self.ant_fitness[i] < self.ant_lion_fitness[i]:
                self.ant_lions[i] = self.ants[i].copy()
                self.ant_lion_fitness[i] = self.ant_fitness[i]
    
    def solve(self, time_budget_ms=None):
        """Run the ALO algorithm."""
        start_time = time.time()
        
        # Initialize population
        self.initialize_population()
        
        best_tour = None
        best_fitness = float('inf')
        
        for iteration in range(self.n_iterations):
            # Check time budget
            if time_budget_ms and (time.time() - start_time) * 1000 > time_budget_ms:
                break
            
            # Update ants using adaptive walk
            for i in range(self.n_ants):
                self.ants[i] = self.adaptive_walk(i, iteration)
                self.ant_fitness[i] = self.calculate_tour_length(self.ants[i])
            
            # Update ant lions
            self.update_ant_lions()
            
            # Track best solution
            current_best_idx = min(range(self.n_ants), key=lambda i: self.ant_lion_fitness[i])
            if self.ant_lion_fitness[current_best_idx] < best_fitness:
                best_fitness = self.ant_lion_fitness[current_best_idx]
                best_tour = self.ant_lions[current_best_idx].copy()
        
        return best_tour, best_fitness

def alo_tsp(dist_func, n_cities, start_city=0, n_ants=30, n_iterations=100, 
            time_budget_ms=None, seed=42):
    """Ant Lion Optimization for TSP."""
    alo = AntLionOptimization(
        dist_func=dist_func,
        n_cities=n_cities,
        start_city=start_city,
        n_ants=n_ants,
        n_iterations=n_iterations,
        seed=seed
    )
    
    best_tour, best_fitness = alo.solve(time_budget_ms=time_budget_ms)
    return best_tour, best_fitness
