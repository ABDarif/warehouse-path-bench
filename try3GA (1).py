"""
Warehouse Package Picking Simulation with Genetic Algorithm Optimization
=======================================================================

Features:
1. Grid-based warehouse with shelves as obstacles
2. Bots with GA-optimized package assignment
3. One-way aisles with alternating up/down directions
4. Collision avoidance between bots
5. Package pickup and delivery with time stamps
6. Real-time visualization with GA optimization progress graph
7. Time vs Iteration graph showing optimization progress

Run this script and follow the prompts to start the simulation.
"""

import numpy as np
import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation
import heapq
from collections import defaultdict
import time

class GeneticAlgorithm:
    """Genetic Algorithm optimizer for package assignment"""
    
    def __init__(self, num_bots, num_packages, warehouse, pop_size=50, generations=100):
        self.num_bots = num_bots
        self.num_packages = num_packages
        self.warehouse = warehouse
        self.pop_size = pop_size
        self.generations = generations
        self.population = []
        self.fitness_history = []
        self.time_history = []
        self.best_chromosome = None
        self.best_fitness = -float('inf')
        
        # GA parameters
        self.crossover_rate = 0.8
        self.mutation_rate = 0.1
        self.tournament_size = 3
        self.elite_size = 2
        
        # Initialize population
        self.initialize_population()
    
    def initialize_population(self):
        """Initialize population with random chromosomes"""
        self.population = []
        
        for _ in range(self.pop_size):
            # Chromosome: list of bot assignments for each package
            chromosome = []
            
            # Random assignment strategy
            for _ in range(self.num_packages):
                chromosome.append(random.randint(0, self.num_bots - 1))
            
            # Add priority ordering (shuffled package IDs)
            priority = list(range(self.num_packages))
            random.shuffle(priority)
            chromosome.extend(priority)
            
            self.population.append(chromosome)
    
    def evaluate_chromosome(self, chromosome):
        """Evaluate fitness of a chromosome by simulating its assignment"""
        # Split chromosome into assignments and priorities
        assignments = chromosome[:self.num_packages]
        priorities = chromosome[self.num_packages:]
        
        # Create package assignment dictionary
        bot_assignments = defaultdict(list)
        for pkg_id, bot_id in enumerate(assignments):
            bot_assignments[bot_id].append(pkg_id)
        
        # Reorder packages based on priorities
        for bot_id in bot_assignments:
            packages = bot_assignments[bot_id]
            packages.sort(key=lambda x: priorities[x])
            bot_assignments[bot_id] = packages
        
        # Calculate fitness based on estimated metrics
        fitness = 0
        
        # 1. Load balancing score
        package_counts = [len(bot_assignments[bot_id]) for bot_id in range(self.num_bots)]
        if package_counts:
            load_balance = 1.0 / (1.0 + np.std(package_counts))
            fitness += 0.3 * load_balance
        
        # 2. Estimated distance score (simplified)
        total_estimated_distance = 0
        for bot_id in range(self.num_bots):
            if bot_id < len(self.warehouse.bot_stations):
                bot_pos = self.warehouse.bot_stations[bot_id]
                packages = bot_assignments[bot_id]
                
                # Sort packages by proximity (estimated)
                if packages:
                    # Simplified distance estimation
                    last_pos = bot_pos
                    for pkg_id in packages:
                        if pkg_id in self.warehouse.packages:
                            pkg_pos = self.warehouse.packages[pkg_id]['cell']
                            # Manhattan distance as estimate
                            dist = abs(pkg_pos[0] - last_pos[0]) + abs(pkg_pos[1] - last_pos[1])
                            total_estimated_distance += dist
                            last_pos = pkg_pos
                    
                    # Add distance to destination
                    dest_pos = self.warehouse.destination
                    dist_to_dest = abs(dest_pos[0] - last_pos[0]) + abs(dest_pos[1] - last_pos[1])
                    total_estimated_distance += dist_to_dest
        
        if total_estimated_distance > 0:
            distance_score = 1.0 / (1.0 + total_estimated_distance / 100.0)
            fitness += 0.7 * distance_score
        
        return fitness, bot_assignments
    
    def tournament_selection(self):
        """Select parent using tournament selection"""
        tournament = random.sample(range(len(self.population)), self.tournament_size)
        tournament_fitness = [self.evaluate_chromosome(self.population[i])[0] for i in tournament]
        winner_index = tournament[np.argmax(tournament_fitness)]
        return self.population[winner_index]
    
    def ordered_crossover(self, parent1, parent2):
        """Ordered crossover for assignment part"""
        child1 = parent1.copy()
        child2 = parent2.copy()
        
        if random.random() < self.crossover_rate:
            # Crossover for assignment part
            crossover_point = random.randint(1, self.num_packages - 2)
            child1[:crossover_point] = parent2[:crossover_point]
            child2[:crossover_point] = parent1[:crossover_point]
            
            # Crossover for priority part
            priority_crossover = random.randint(self.num_packages + 1, len(parent1) - 2)
            child1[self.num_packages:priority_crossover] = parent2[self.num_packages:priority_crossover]
            child2[self.num_packages:priority_crossover] = parent1[self.num_packages:priority_crossover]
        
        return child1, child2
    
    def mutate(self, chromosome):
        """Apply mutation to chromosome"""
        mutated = chromosome.copy()
        
        if random.random() < self.mutation_rate:
            # Mutation for assignment: change bot for a random package
            mutation_point = random.randint(0, self.num_packages - 1)
            mutated[mutation_point] = random.randint(0, self.num_bots - 1)
        
        if random.random() < self.mutation_rate:
            # Mutation for priority: swap two priorities
            idx1 = random.randint(self.num_packages, len(chromosome) - 1)
            idx2 = random.randint(self.num_packages, len(chromosome) - 1)
            mutated[idx1], mutated[idx2] = mutated[idx2], mutated[idx1]
        
        return mutated
    
    def evolve(self):
        """Run one generation of evolution"""
        # Evaluate current population
        fitness_scores = []
        best_in_gen = -float('inf')
        best_chromosome_in_gen = None
        best_assignment_in_gen = None
        
        for i, chromosome in enumerate(self.population):
            fitness, assignments = self.evaluate_chromosome(chromosome)
            fitness_scores.append(fitness)
            
            if fitness > best_in_gen:
                best_in_gen = fitness
                best_chromosome_in_gen = chromosome
                best_assignment_in_gen = assignments
        
        # Record statistics
        avg_fitness = np.mean(fitness_scores)
        max_fitness = np.max(fitness_scores)
        self.fitness_history.append((avg_fitness, max_fitness))
        
        # Update best overall
        if max_fitness > self.best_fitness:
            self.best_fitness = max_fitness
            self.best_chromosome = best_chromosome_in_gen
        
        # Create new population with elitism
        new_population = []
        
        # Select elites
        elite_indices = np.argsort(fitness_scores)[-self.elite_size:]
        for idx in elite_indices:
            new_population.append(self.population[idx])
        
        # Fill rest of population
        while len(new_population) < self.pop_size:
            # Selection
            parent1 = self.tournament_selection()
            parent2 = self.tournament_selection()
            
            # Crossover
            child1, child2 = self.ordered_crossover(parent1, parent2)
            
            # Mutation
            child1 = self.mutate(child1)
            child2 = self.mutate(child2)
            
            new_population.extend([child1, child2])
        
        # Trim if we have too many
        self.population = new_population[:self.pop_size]
        
        return best_in_gen, best_assignment_in_gen
    
    def run_optimization(self):
        """Run full GA optimization"""
        print(f"Starting GA optimization for {self.generations} generations...")
        start_time = time.time()
        
        for gen in range(self.generations):
            best_fitness, best_assignment = self.evolve()
            elapsed_time = time.time() - start_time
            self.time_history.append(elapsed_time)
            
            if gen % 10 == 0:
                print(f"Generation {gen}: Best fitness = {best_fitness:.4f}, Time = {elapsed_time:.2f}s")
        
        print(f"Optimization completed in {time.time() - start_time:.2f} seconds")
        print(f"Best fitness: {self.best_fitness:.4f}")
        
        return self.get_best_assignment()
    
    def get_best_assignment(self):
        """Get the best package assignment from best chromosome"""
        if self.best_chromosome is None:
            return None
        
        assignments = self.best_chromosome[:self.num_packages]
        priorities = self.best_chromosome[self.num_packages:]
        
        bot_assignments = defaultdict(list)
        for pkg_id, bot_id in enumerate(assignments):
            bot_assignments[bot_id].append(pkg_id)
        
        # Sort packages by priority for each bot
        for bot_id in bot_assignments:
            packages = bot_assignments[bot_id]
            packages.sort(key=lambda x: priorities[x])
            bot_assignments[bot_id] = packages
        
        return bot_assignments

class Warehouse:
    """Main warehouse class managing grid, shelves, packages, and bots"""
    
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.grid = np.zeros((rows, cols), dtype=int)
        self.shelves = []
        self.bot_stations = []
        self.packages = {}
        self.bots = []
        self.aisle_directions = {}
        self.time_stamp = 0
        self.completed_packages = 0
        self.total_packages = 0
        
        # Collision avoidance
        self.bot_positions = {}
        self.reserved_cells = set()
        
        # GA optimization
        self.ga_optimizer = None
        self.optimized_assignments = None
        
    def generate_shelves(self, min_shelf_len=2, max_shelf_len=4, min_shelf_gap=2):
        """Generate shelves with alternating one-way aisles between them"""
        col = 1  # Start from column 1, leave column 0 for bot stations
        
        while col < self.cols - 2:
            shelf_len = random.randint(min_shelf_len, min(max_shelf_len, self.rows - 4))
            start_row = random.randint(1, self.rows - shelf_len - 2)
            
            # Create shelf
            shelf_cells = []
            for r in range(start_row, start_row + shelf_len):
                self.grid[r, col] = 1
                shelf_cells.append((r, col))
            
            shelf_id = len(self.shelves)
            self.shelves.append({
                'id': shelf_id,
                'cells': shelf_cells,
                'col': col,
                'start_row': start_row,
                'length': shelf_len,
                'sections': [None] * shelf_len
            })
            
            # Create one-way aisles between shelves
            if col > 1:
                aisle_col = col - 1
                for r in range(self.rows):
                    if r < start_row or r >= start_row + shelf_len:
                        # Alternating directions
                        if (aisle_col // min_shelf_gap) % 2 == 0:
                            direction = 'up'
                        else:
                            direction = 'down'
                        self.aisle_directions[(r, aisle_col)] = direction
            
            col += min_shelf_gap + 1
            
            if col >= self.cols - 2:
                break
        
        # Add final aisle after last shelf
        if self.shelves:
            last_shelf_col = max(shelf['col'] for shelf in self.shelves)
            final_aisle_col = last_shelf_col + 1
            if final_aisle_col < self.cols - 1:
                for r in range(self.rows):
                    if (final_aisle_col // min_shelf_gap) % 2 == 0:
                        direction = 'up'
                    else:
                        direction = 'down'
                    self.aisle_directions[(r, final_aisle_col)] = direction
    
    def generate_bot_stations(self, num_bots):
        """Generate bot stations in first column with gaps"""
        available_rows = list(range(1, self.rows - 1))
        random.shuffle(available_rows)
        
        self.bot_stations = []
        for i in range(min(num_bots, len(available_rows))):
            row = available_rows[i]
            self.grid[row, 0] = 2
            self.bot_stations.append((row, 0))
    
    def set_destination(self):
        """Set destination at last column, last row"""
        self.destination = (self.rows - 1, self.cols - 1)
        self.grid[self.destination[0], self.destination[1]] = 3
        return self.destination
    
    def place_packages(self, num_packages):
        """Place packages randomly on shelves"""
        package_id = 0
        self.packages = {}
        
        for _ in range(num_packages):
            if not self.shelves:
                break
                
            shelf = random.choice(self.shelves)
            available_sections = [i for i, pkg in enumerate(shelf['sections']) if pkg is None]
            
            if available_sections:
                section_idx = random.choice(available_sections)
                cell = shelf['cells'][section_idx]
                
                self.packages[package_id] = {
                    'id': package_id,
                    'cell': cell,
                    'shelf_id': shelf['id'],
                    'section_idx': section_idx,
                    'status': 'on_shelf',
                    'assigned_to': None,
                    'pickup_time': None,
                    'delivery_time': None,
                    'pickup_cell': None
                }
                
                shelf['sections'][section_idx] = package_id
                package_id += 1
        
        self.total_packages = len(self.packages)
        return self.packages
    
    def optimize_with_ga(self, pop_size=30, generations=50):
        """Use GA to optimize package assignment"""
        print("Starting Genetic Algorithm optimization...")
        self.ga_optimizer = GeneticAlgorithm(
            num_bots=len(self.bot_stations),
            num_packages=self.total_packages,
            warehouse=self,
            pop_size=pop_size,
            generations=generations
        )
        
        self.optimized_assignments = self.ga_optimizer.run_optimization()
        return self.optimized_assignments
    
    def is_valid_move(self, from_pos, to_pos, bot_id, ignore_reserved=False):
        """Check if move is valid considering obstacles, aisle directions, and other bots"""
        fr, fc = from_pos
        tr, tc = to_pos
        
        # Check bounds
        if tr < 0 or tr >= self.rows or tc < 0 or tc >= self.cols:
            return False
        
        # Cannot enter shelf cells
        if self.grid[tr, tc] == 1:
            return False
        
        # Check for other bots
        for other_bot_id, other_pos in self.bot_positions.items():
            if other_bot_id != bot_id and other_pos == to_pos:
                if to_pos == self.destination:
                    for bot in self.bots:
                        if bot.id == other_bot_id and bot.status == 'delivering':
                            return False
                else:
                    return False
        
        # Check reservations
        if not ignore_reserved and to_pos in self.reserved_cells:
            return False
        
        # Enforce one-way aisle rules
        # Check moving TO aisle cell
        if (tr, tc) in self.aisle_directions:
            direction = self.aisle_directions[(tr, tc)]
            if fc == tc:  # Vertical movement
                if direction == 'up' and tr > fr:
                    return False  # Can't move down in up aisle
                elif direction == 'down' and tr < fr:
                    return False  # Can't move up in down aisle
        
        # Check moving FROM aisle cell
        if (fr, fc) in self.aisle_directions:
            direction = self.aisle_directions[(fr, fc)]
            if fc == tc:  # Vertical movement
                if direction == 'up' and tr > fr:
                    return False
                elif direction == 'down' and tr < fr:
                    return False
        
        return True
    
    def get_adjacent_cells(self, pos, bot_id):
        """Get valid adjacent cells for movement"""
        r, c = pos
        adjacent = []
        
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            new_pos = (r + dr, c + dc)
            if self.is_valid_move(pos, new_pos, bot_id):
                adjacent.append(new_pos)
        
        return adjacent
    
    def get_adjacent_to_package(self, package_cell, bot_id=None):
        """Get cells adjacent to a package that are valid for pickup"""
        r, c = package_cell
        adjacent_cells = []
        
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            adj_r, adj_c = r + dr, c + dc
            
            if 0 <= adj_r < self.rows and 0 <= adj_c < self.cols:
                if self.grid[adj_r, adj_c] != 1:
                    if bot_id is None or self.is_valid_move((adj_r, adj_c), (adj_r, adj_c), bot_id, ignore_reserved=True):
                        adjacent_cells.append((adj_r, adj_c))
        
        return adjacent_cells
    
    def reserve_cell(self, cell, bot_id):
        """Reserve a cell for a bot's next move"""
        self.reserved_cells.add(cell)
    
    def clear_reservations(self):
        """Clear all cell reservations"""
        self.reserved_cells.clear()
    
    def update_bot_position(self, bot_id, new_pos):
        """Update a bot's position"""
        self.bot_positions[bot_id] = new_pos
    
    def a_star_search(self, start, goal, bot_id):
        """A* pathfinding algorithm with one-way aisle constraints"""
        def heuristic(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])
        
        # Handle package pickup (goal is shelf cell)
        if self.grid[goal[0], goal[1]] == 1:
            adj_cells = self.get_adjacent_to_package(goal, bot_id)
            if not adj_cells:
                return None
            
            best_path = None
            best_cost = float('inf')
            
            for adj_cell in adj_cells:
                path = self.a_star_search(start, adj_cell, bot_id)
                if path and len(path) < best_cost:
                    best_path = path
                    best_cost = len(path)
            
            return best_path
        
        frontier = []
        heapq.heappush(frontier, (0, start))
        came_from = {start: None}
        cost_so_far = {start: 0}
        
        while frontier:
            current = heapq.heappop(frontier)[1]
            
            if current == goal:
                break
            
            for next_cell in self.get_adjacent_cells(current, bot_id):
                new_cost = cost_so_far[current] + 1
                
                if next_cell not in cost_so_far or new_cost < cost_so_far[next_cell]:
                    cost_so_far[next_cell] = new_cost
                    priority = new_cost + heuristic(goal, next_cell)
                    heapq.heappush(frontier, (priority, next_cell))
                    came_from[next_cell] = current
        
        # Reconstruct path
        if goal not in came_from:
            return None
        
        path = []
        current = goal
        while current != start:
            path.append(current)
            current = came_from[current]
        path.reverse()
        
        return path
    
    def find_nearest_package_for_bot(self, bot_pos, bot_id, available_packages):
        """Find nearest package for a bot considering aisle constraints"""
        min_distance = float('inf')
        nearest_package = None
        nearest_path = None
        pickup_cell = None
        
        for pkg_id in available_packages:
            pkg_cell = self.packages[pkg_id]['cell']
            adj_cells = self.get_adjacent_to_package(pkg_cell, bot_id)
            
            for adj_cell in adj_cells:
                path = self.a_star_search(bot_pos, adj_cell, bot_id)
                if path and len(path) < min_distance:
                    min_distance = len(path)
                    nearest_package = pkg_id
                    nearest_path = path
                    pickup_cell = adj_cell
        
        return nearest_package, nearest_path, pickup_cell

class Bot:
    """Bot class representing individual warehouse robots"""
    
    def __init__(self, bot_id, start_pos, warehouse):
        self.id = bot_id
        self.pos = start_pos
        self.warehouse = warehouse
        self.packages = []
        self.assigned_packages = []
        self.status = 'idle'
        self.current_path = None
        self.current_target = None
        self.pickup_cell = None
        self.wait_time = 0
        self.pickup_wait = 0
        self.delivery_wait = 0
        self.steps_taken = 0
        self.packages_delivered = 0
        self.blocked_time = 0
        self.next_pos = None
        self.path_history = []
        self.current_direction = None
        
        self.warehouse.update_bot_position(self.id, self.pos)
        
    def assign_packages(self, package_ids):
        """Assign packages to this bot"""
        self.assigned_packages = package_ids.copy()
    
    def plan_next_move(self):
        """Plan the next move considering aisle directions and collisions"""
        if self.status in ['picking', 'delivering', 'idle']:
            self.next_pos = self.pos
            self.update_direction(self.pos, self.pos)
            return
        
        if self.status == 'moving_to_package' and self.current_path:
            if len(self.current_path) > 0:
                next_cell = self.current_path[0]
                
                if self.warehouse.is_valid_move(self.pos, next_cell, self.id):
                    self.next_pos = next_cell
                    self.update_direction(self.pos, next_cell)
                    self.warehouse.reserve_cell(next_cell, self.id)
                else:
                    self.next_pos = self.pos
                    self.update_direction(self.pos, self.pos)
                    self.blocked_time += 1
                    
                    # Find alternative path if blocked too long
                    if self.blocked_time > 3 and self.current_target is not None:
                        available_packages = [self.current_target]
                        _, new_path, new_pickup = self.warehouse.find_nearest_package_for_bot(
                            self.pos, self.id, available_packages
                        )
                        if new_path:
                            self.current_path = new_path
                            self.pickup_cell = new_pickup
                            if self.current_target in self.warehouse.packages:
                                self.warehouse.packages[self.current_target]['pickup_cell'] = new_pickup
                            self.blocked_time = 0
            else:
                self.next_pos = self.pos
                self.update_direction(self.pos, self.pos)
        
        elif self.status == 'moving_to_destination' and self.current_path:
            if len(self.current_path) > 0:
                next_cell = self.current_path[0]
                
                if next_cell == self.warehouse.destination:
                    # Destination queuing
                    bots_at_dest = 0
                    delivering_at_dest = False
                    for bot in self.warehouse.bots:
                        if bot.id != self.id and bot.pos == self.warehouse.destination:
                            bots_at_dest += 1
                            if bot.status == 'delivering':
                                delivering_at_dest = True
                    
                    if bots_at_dest == 0 or not delivering_at_dest:
                        self.next_pos = next_cell
                        self.update_direction(self.pos, next_cell)
                        self.warehouse.reserve_cell(next_cell, self.id)
                    else:
                        self.next_pos = self.pos
                        self.update_direction(self.pos, self.pos)
                        self.blocked_time += 1
                else:
                    if self.warehouse.is_valid_move(self.pos, next_cell, self.id):
                        self.next_pos = next_cell
                        self.update_direction(self.pos, next_cell)
                        self.warehouse.reserve_cell(next_cell, self.id)
                    else:
                        self.next_pos = self.pos
                        self.update_direction(self.pos, self.pos)
                        self.blocked_time += 1
            else:
                self.next_pos = self.pos
                self.update_direction(self.pos, self.pos)
    
    def update_direction(self, from_pos, to_pos):
        """Update the bot's current movement direction"""
        if from_pos == to_pos:
            self.current_direction = None
        else:
            fr, fc = from_pos
            tr, tc = to_pos
            if tr < fr:
                self.current_direction = 'up'
            elif tr > fr:
                self.current_direction = 'down'
            elif tc < fc:
                self.current_direction = 'left'
            elif tc > fc:
                self.current_direction = 'right'
    
    def execute_move(self):
        """Execute the planned move"""
        if self.next_pos != self.pos:
            # Update path history
            if len(self.path_history) < 20:
                self.path_history.append(self.pos)
            else:
                self.path_history.pop(0)
                self.path_history.append(self.pos)
            
            self.pos = self.next_pos
            self.steps_taken += 1
            self.warehouse.update_bot_position(self.id, self.pos)
            
            # Update current path
            if self.current_path and self.status in ['moving_to_package', 'moving_to_destination']:
                if len(self.current_path) > 0 and self.current_path[0] == self.pos:
                    self.current_path.pop(0)
        
        if self.next_pos != self.pos:
            self.blocked_time = 0
    
    def update_status(self):
        """Update bot status after movement"""
        if self.status == 'idle':
            if self.assigned_packages:
                available_packages = [pkg_id for pkg_id in self.assigned_packages 
                                    if self.warehouse.packages[pkg_id]['status'] == 'on_shelf']
                
                if available_packages:
                    nearest_package, nearest_path, pickup_cell = self.warehouse.find_nearest_package_for_bot(
                        self.pos, self.id, available_packages
                    )
                    
                    if nearest_package is not None:
                        self.current_target = nearest_package
                        self.current_path = nearest_path
                        self.pickup_cell = pickup_cell
                        self.status = 'moving_to_package'
                        self.warehouse.packages[nearest_package]['status'] = 'assigned'
                        self.warehouse.packages[nearest_package]['assigned_to'] = self.id
                        self.warehouse.packages[nearest_package]['pickup_cell'] = pickup_cell
        
        elif self.status == 'moving_to_package':
            if self.current_path is None or len(self.current_path) == 0:
                if self.pos == self.pickup_cell:
                    self.status = 'picking'
                    self.pickup_wait = 2
                    self.warehouse.packages[self.current_target]['pickup_time'] = self.warehouse.time_stamp
        
        elif self.status == 'picking':
            self.pickup_wait -= 1
            if self.pickup_wait <= 0:
                if self.current_target is not None:
                    self.packages.append(self.current_target)
                    if self.current_target in self.warehouse.packages:
                        self.warehouse.packages[self.current_target]['status'] = 'picked_up'
                    
                    if self.current_target in self.assigned_packages:
                        self.assigned_packages.remove(self.current_target)
                    
                    path = self.warehouse.a_star_search(self.pos, self.warehouse.destination, self.id)
                    if path:
                        self.current_path = path
                        self.status = 'moving_to_destination'
                        self.pickup_cell = None
                        self.current_target = None
        
        elif self.status == 'moving_to_destination':
            if self.current_path is None or len(self.current_path) == 0:
                if self.pos == self.warehouse.destination:
                    self.status = 'delivering'
                    self.delivery_wait = 2
        
        elif self.status == 'delivering':
            self.delivery_wait -= 1
            if self.delivery_wait <= 0:
                delivered_ids = []
                for pkg_id in self.packages[:]:
                    if pkg_id in self.warehouse.packages:
                        self.warehouse.packages[pkg_id]['status'] = 'delivered'
                        self.warehouse.packages[pkg_id]['delivery_time'] = self.warehouse.time_stamp
                        self.warehouse.completed_packages += 1
                        self.packages_delivered += 1
                        delivered_ids.append(pkg_id)
                
                for pkg_id in delivered_ids:
                    if pkg_id in self.packages:
                        self.packages.remove(pkg_id)
                
                if self.assigned_packages:
                    self.status = 'idle'
                else:
                    self.status = 'idle'
    
    def update(self):
        """Update bot state"""
        self.plan_next_move()

class WarehouseSimulation:
    """Main simulation controller"""
    
    def __init__(self, rows=15, cols=20, num_bots=3, num_packages=10, use_ga=True):
        self.rows = rows
        self.cols = cols
        self.num_bots = num_bots
        self.num_packages = num_packages
        self.use_ga = use_ga
        
        self.warehouse = Warehouse(rows, cols)
        self.warehouse.generate_shelves()
        self.warehouse.generate_bot_stations(num_bots)
        self.warehouse.set_destination()
        self.warehouse.place_packages(num_packages)
        
        # Initialize bots
        for i in range(num_bots):
            if i < len(self.warehouse.bot_stations):
                bot = Bot(i, self.warehouse.bot_stations[i], self.warehouse)
                self.warehouse.bots.append(bot)
        
        # Use GA for optimization if requested
        if self.use_ga and self.warehouse.total_packages > 0:
            self.optimize_with_ga()
        else:
            self.assign_packages_randomly()
        
        self.history = []
        self.simulation_running = True
        self.collisions = 0
        self.aisle_violations = 0
        self.ga_optimization_time = 0
    
    def optimize_with_ga(self):
        """Optimize package assignment using Genetic Algorithm"""
        print("Using GA to optimize package assignments...")
        start_time = time.time()
        
        # Run GA optimization
        optimized_assignments = self.warehouse.optimize_with_ga(
            pop_size=min(30, 5 * self.num_bots * self.num_packages),
            generations=min(50, 10 * self.num_packages)
        )
        
        self.ga_optimization_time = time.time() - start_time
        
        if optimized_assignments:
            # Assign packages based on GA optimization
            for bot_id, package_ids in optimized_assignments.items():
                if bot_id < len(self.warehouse.bots):
                    self.warehouse.bots[bot_id].assign_packages(package_ids)
            print(f"GA optimization completed in {self.ga_optimization_time:.2f} seconds")
        else:
            print("GA optimization failed, using random assignment")
            self.assign_packages_randomly()
    
    def assign_packages_randomly(self):
        """Randomly assign packages to bots"""
        package_ids = list(self.warehouse.packages.keys())
        random.shuffle(package_ids)
        
        packages_per_bot = len(package_ids) // self.num_bots
        remainder = len(package_ids) % self.num_bots
        
        start_idx = 0
        for i, bot in enumerate(self.warehouse.bots):
            end_idx = start_idx + packages_per_bot + (1 if i < remainder else 0)
            bot.assign_packages(package_ids[start_idx:end_idx])
            start_idx = end_idx
    
    def check_collisions(self):
        """Check for collisions between bots"""
        positions = {}
        collisions = 0
        
        for bot in self.warehouse.bots:
            if bot.pos in positions:
                collisions += 1
            positions[bot.pos] = bot.id
        
        return collisions
    
    def check_aisle_violations(self):
        """Check if bots are violating aisle directions"""
        violations = 0
        for bot in self.warehouse.bots:
            if bot.current_direction and (bot.pos in self.warehouse.aisle_directions):
                aisle_dir = self.warehouse.aisle_directions[bot.pos]
                bot_dir = bot.current_direction
                
                if aisle_dir == 'up' and bot_dir == 'down':
                    violations += 1
                elif aisle_dir == 'down' and bot_dir == 'up':
                    violations += 1
        
        return violations
    
    def update(self):
        """Update simulation for one time stamp"""
        if not self.simulation_running:
            return False
        
        self.warehouse.time_stamp += 1
        
        # Clear reservations
        self.warehouse.clear_reservations()
        
        # Three-phase update
        for bot in self.warehouse.bots:
            bot.plan_next_move()
        
        for bot in self.warehouse.bots:
            bot.execute_move()
        
        for bot in self.warehouse.bots:
            bot.update_status()
        
        # Check statistics
        current_collisions = self.check_collisions()
        if current_collisions > 0:
            self.collisions += current_collisions
        
        current_violations = self.check_aisle_violations()
        if current_violations > 0:
            self.aisle_violations += current_violations
        
        # Record history
        stats = {
            'time': self.warehouse.time_stamp,
            'completed': self.warehouse.completed_packages,
            'total': self.warehouse.total_packages,
            'bot_statuses': [bot.status for bot in self.warehouse.bots],
            'bot_positions': [bot.pos for bot in self.warehouse.bots],
            'collisions': current_collisions,
            'aisle_violations': current_violations
        }
        self.history.append(stats)
        
        # Check completion
        if self.warehouse.completed_packages >= self.warehouse.total_packages:
            self.simulation_running = False
            self.print_summary()
        
        return True
    
    def print_summary(self):
        """Print simulation summary"""
        print("\n" + "="*60)
        print("SIMULATION COMPLETE - SUMMARY")
        print("="*60)
        print(f"Total time: {self.warehouse.time_stamp} ticks")
        print(f"Packages: {self.warehouse.completed_packages}/{self.warehouse.total_packages}")
        print(f"Success rate: {100 * self.warehouse.completed_packages / max(1, self.warehouse.total_packages):.1f}%")
        print(f"Collisions: {self.collisions}")
        print(f"Aisle violations: {self.aisle_violations}")
        
        if self.use_ga and hasattr(self.warehouse.ga_optimizer, 'best_fitness'):
            print(f"GA Best Fitness: {self.warehouse.ga_optimizer.best_fitness:.4f}")
            print(f"GA Optimization Time: {self.ga_optimization_time:.2f}s")
        
        print("\nBot Performance:")
        total_steps = 0
        for i, bot in enumerate(self.warehouse.bots):
            print(f"  Bot {i}: {bot.packages_delivered} packages, {bot.steps_taken} steps")
            total_steps += bot.steps_taken
        
        if total_steps > 0:
            compliance = 100 - (self.aisle_violations / max(1, total_steps) * 100)
            print(f"\nAisle direction compliance: {compliance:.1f}%")
        
        print("="*60)

class WarehouseVisualizer:
    """Visualization handler for the simulation with GA progress graph"""
    
    def __init__(self, simulation):
        self.simulation = simulation
        self.warehouse = simulation.warehouse
        
        # Create figure with 3 subplots: warehouse, status, GA progress
        self.fig = plt.figure(figsize=(22, 10))
        self.gs = self.fig.add_gridspec(2, 3, height_ratios=[3, 1], width_ratios=[2, 1, 1])
        
        self.ax = self.fig.add_subplot(self.gs[0, 0])  # Warehouse visualization
        self.ax_status = self.fig.add_subplot(self.gs[0, 1])  # Status panel
        self.ax_ga = self.fig.add_subplot(self.gs[0, 2])  # GA optimization graph
        self.ax_summary = self.fig.add_subplot(self.gs[1, :])  # Summary stats
        
        # Color scheme
        self.colors = {
            0: 'white',
            1: 'saddlebrown',
            2: 'lightblue',
            3: 'limegreen',
            'bot': 'red',
            'package': 'orange',
            'aisle_up': '#E8F4F8',
            'aisle_down': '#F8E8E8',
            'pickup_cell': 'lightyellow',
            'collision': 'magenta',
            'picking': 'orange',
            'delivering': 'red',
            'path': 'lightgreen',
            'ga_avg': 'blue',
            'ga_best': 'red'
        }
        
        # Initialize GA progress graph if GA was used
        if self.simulation.use_ga and hasattr(self.warehouse, 'ga_optimizer'):
            self.init_ga_graph()
    
    def init_ga_graph(self):
        """Initialize the GA progress graph"""
        self.ax_ga.clear()
        self.ax_ga.set_title('GA Optimization Progress', fontsize=14, fontweight='bold')
        self.ax_ga.set_xlabel('Generation')
        self.ax_ga.set_ylabel('Fitness Score')
        self.ax_ga.grid(True, alpha=0.3)
        
        if self.warehouse.ga_optimizer and hasattr(self.warehouse.ga_optimizer, 'fitness_history'):
            gens = range(len(self.warehouse.ga_optimizer.fitness_history))
            avg_fitness = [fh[0] for fh in self.warehouse.ga_optimizer.fitness_history]
            best_fitness = [fh[1] for fh in self.warehouse.ga_optimizer.fitness_history]
            
            self.ax_ga.plot(gens, avg_fitness, 'b-', label='Average Fitness', alpha=0.7, linewidth=2)
            self.ax_ga.plot(gens, best_fitness, 'r-', label='Best Fitness', alpha=0.9, linewidth=2)
            self.ax_ga.legend(loc='lower right')
            self.ax_ga.set_xlim(0, len(gens))
            
            # Add text box with GA info
            ga_info = f"GA Parameters:\n"
            ga_info += f"Population: {self.warehouse.ga_optimizer.pop_size}\n"
            ga_info += f"Generations: {self.warehouse.ga_optimizer.generations}\n"
            ga_info += f"Best Fitness: {self.warehouse.ga_optimizer.best_fitness:.4f}"
            
            self.ax_ga.text(0.02, 0.98, ga_info, transform=self.ax_ga.transAxes,
                          verticalalignment='top', fontsize=9,
                          bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
    
    def draw_grid(self):
        """Draw the warehouse grid"""
        self.ax.clear()
        
        # Draw cells
        for r in range(self.warehouse.rows):
            for c in range(self.warehouse.cols):
                cell_value = self.warehouse.grid[r, c]
                
                if (r, c) in self.warehouse.aisle_directions:
                    direction = self.warehouse.aisle_directions[(r, c)]
                    color = self.colors['aisle_up'] if direction == 'up' else self.colors['aisle_down']
                    
                    rect = patches.Rectangle((c, self.warehouse.rows - r - 1), 1, 1,
                                           linewidth=1, edgecolor='black',
                                           facecolor=color, alpha=0.9)
                    self.ax.add_patch(rect)
                    
                    # Direction arrow
                    arrow = '↑' if direction == 'up' else '↓'
                    arrow_color = 'blue' if direction == 'up' else 'red'
                    self.ax.text(c + 0.5, self.warehouse.rows - r - 0.5, arrow,
                               ha='center', va='center', fontsize=14, fontweight='bold',
                               color=arrow_color, alpha=0.8)
                else:
                    color = self.colors.get(cell_value, 'white')
                    rect = patches.Rectangle((c, self.warehouse.rows - r - 1), 1, 1,
                                           linewidth=1, edgecolor='black',
                                           facecolor=color, alpha=0.8)
                    self.ax.add_patch(rect)
        
        # Draw bot paths
        for bot in self.warehouse.bots:
            if len(bot.path_history) > 1:
                for i in range(1, len(bot.path_history)):
                    r1, c1 = bot.path_history[i-1]
                    r2, c2 = bot.path_history[i]
                    y1 = self.warehouse.rows - r1 - 0.5
                    y2 = self.warehouse.rows - r2 - 0.5
                    x1 = c1 + 0.5
                    x2 = c2 + 0.5
                    
                    self.ax.plot([x1, x2], [y1, y2], color=self.colors['path'], 
                               alpha=0.3, linewidth=2, zorder=1)
        
        # Draw pickup cells
        for pkg_id, pkg_info in self.warehouse.packages.items():
            if pkg_info.get('pickup_cell') and pkg_info['status'] in ['assigned', 'on_shelf']:
                r, c = pkg_info['pickup_cell']
                y = self.warehouse.rows - r - 1
                x = c
                
                rect = patches.Rectangle((x, y), 1, 1,
                                       linewidth=2, edgecolor='gold',
                                       facecolor=self.colors['pickup_cell'], alpha=0.5)
                self.ax.add_patch(rect)
        
        # Check collisions
        positions = {}
        collision_cells = []
        for bot in self.warehouse.bots:
            if bot.pos in positions:
                collision_cells.append(bot.pos)
            positions[bot.pos] = bot.id
        
        # Highlight collisions
        for cell in collision_cells:
            r, c = cell
            y = self.warehouse.rows - r - 1
            x = c
            
            rect = patches.Rectangle((x, y), 1, 1,
                                   linewidth=3, edgecolor='magenta',
                                   facecolor='none', alpha=0.8)
            self.ax.add_patch(rect)
        
        # Draw bots
        for bot in self.warehouse.bots:
            r, c = bot.pos
            y = self.warehouse.rows - r - 0.5
            x = c + 0.5
            
            # Bot color based on status
            circle_color = self.colors['bot']
            if bot.status == 'picking':
                circle_color = self.colors['picking']
            elif bot.status == 'delivering':
                circle_color = self.colors['delivering']
            elif bot.pos in collision_cells:
                circle_color = 'magenta'
            
            circle = patches.Circle((x, y), 0.4, facecolor=circle_color, 
                                  edgecolor='black', linewidth=2, zorder=3)
            self.ax.add_patch(circle)
            
            # Bot ID
            self.ax.text(x, y, f'B{bot.id}', ha='center', va='center',
                       fontsize=12, fontweight='bold', color='white', zorder=4)
            
            # Packages carried
            if bot.packages:
                packages_text = f"[{len(bot.packages)}]"
                self.ax.text(x - 0.4, y + 0.4, packages_text, 
                           ha='center', va='center', fontsize=9, fontweight='bold',
                           color='darkgreen', 
                           bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7),
                           zorder=4)
            
            # Direction indicator
            if bot.current_direction:
                dir_symbol = {'up': '↑', 'down': '↓', 'left': '←', 'right': '→'}.get(bot.current_direction, '•')
                self.ax.text(x + 0.4, y - 0.4, dir_symbol, 
                           ha='center', va='center', fontsize=10, fontweight='bold',
                           color='darkblue', zorder=4)
        
        # Draw packages
        for pkg_id, pkg_info in self.warehouse.packages.items():
            r, c = pkg_info['cell']
            
            if pkg_info['status'] in ['on_shelf', 'assigned']:
                y = self.warehouse.rows - r - 0.5
                x = c + 0.5
                
                marker_color = 'orange' if pkg_info['status'] == 'on_shelf' else 'blue'
                circle = patches.Circle((x, y), 0.3, 
                                       facecolor=marker_color, edgecolor='black',
                                       alpha=0.8, zorder=2)
                self.ax.add_patch(circle)
                
                self.ax.text(x, y, f'P{pkg_id}', ha='center', va='center',
                           fontsize=9, fontweight='bold', color='white', zorder=3)
        
        # Draw delivered count
        delivered_count = 0
        for pkg_info in self.warehouse.packages.values():
            if pkg_info['status'] == 'delivered':
                delivered_count += 1
        
        if delivered_count > 0:
            dest_r, dest_c = self.warehouse.destination
            y = self.warehouse.rows - dest_r - 0.5
            x = dest_c + 0.5
            
            self.ax.text(x, y - 0.3, f'✓{delivered_count}', 
                       ha='center', va='center', fontsize=12, fontweight='bold',
                       color='darkgreen', 
                       bbox=dict(boxstyle='circle', facecolor='lightgreen', alpha=0.8),
                       zorder=4)
        
        # Configure plot
        self.ax.set_xlim(-1, self.warehouse.cols)
        self.ax.set_ylim(-1, self.warehouse.rows)
        self.ax.set_aspect('equal')
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        
        # Title
        time_stamp = self.warehouse.time_stamp
        completed = self.warehouse.completed_packages
        total = self.warehouse.total_packages
        
        title = f"Warehouse Package Picking Simulation - Time: {time_stamp}"
        if self.simulation.use_ga:
            title += " (GA Optimized)"
        self.ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        
        # Draw status panel and summary
        self.draw_status_panel()
        self.draw_summary_panel()
    
    def draw_status_panel(self):
        """Draw the status panel"""
        self.ax_status.clear()
        self.ax_status.axis('off')
        
        time_stamp = self.warehouse.time_stamp
        completed = self.warehouse.completed_packages
        total = self.warehouse.total_packages
        
        # Build status text
        status_text = f"TIME: {time_stamp}\n"
        status_text += f"PACKAGES: {completed}/{total}\n"
        
        if total > 0:
            progress = completed / total * 100
            status_text += f"PROGRESS: {progress:.1f}%\n"
        
        status_text += f"COLLISIONS: {self.simulation.collisions}\n"
        status_text += f"AISLE VIOLATIONS: {self.simulation.aisle_violations}\n"
        
        if self.simulation.use_ga and hasattr(self.warehouse.ga_optimizer, 'best_fitness'):
            status_text += f"GA BEST FITNESS: {self.warehouse.ga_optimizer.best_fitness:.4f}\n"
        
        status_text += "-" * 40 + "\n"
        
        status_text += "BOT STATUS:\n"
        for i, bot in enumerate(self.warehouse.bots):
            status_display = {
                'idle': 'IDLE',
                'moving_to_package': '→ PACKAGE',
                'picking': f'PICKING ({bot.pickup_wait}/2)',
                'moving_to_destination': '→ DEST',
                'delivering': f'DELIVERING ({bot.delivery_wait}/2)'
            }
            status = status_display.get(bot.status, bot.status)
            
            dir_info = ""
            if bot.current_direction:
                dir_symbol = {'up': '↑', 'down': '↓', 'left': '←', 'right': '→'}.get(bot.current_direction, '•')
                dir_info = f"Dir: {dir_symbol} "
            
            packages_info = f"Carrying: {len(bot.packages)}"
            if bot.assigned_packages:
                packages_info += f", Assigned: {len(bot.assigned_packages)}"
            
            if bot.blocked_time > 0:
                packages_info += f", Blocked: {bot.blocked_time}"
            
            status_text += f"\nBot {i}:\n"
            status_text += f"  Status: {status}\n"
            status_text += f"  {dir_info}\n"
            status_text += f"  {packages_info}\n"
            status_text += f"  Steps: {bot.steps_taken}\n"
        
        # Display text
        self.ax_status.text(0, 1, status_text, transform=self.ax_status.transAxes,
                          verticalalignment='top', fontsize=9, fontfamily='monospace',
                          bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.9))
    
    def draw_summary_panel(self):
        """Draw the summary statistics panel"""
        self.ax_summary.clear()
        self.ax_summary.axis('off')
        
        summary_text = "PERFORMANCE METRICS:\n"
        summary_text += "-" * 80 + "\n"
        
        # Calculate metrics
        total_steps = sum(bot.steps_taken for bot in self.warehouse.bots)
        total_packages_delivered = sum(bot.packages_delivered for bot in self.warehouse.bots)
        
        # Efficiency metrics
        if total_steps > 0:
            steps_per_package = total_steps / max(1, total_packages_delivered)
            summary_text += f"Steps per package: {steps_per_package:.2f}\n"
        
        if self.warehouse.time_stamp > 0:
            packages_per_tick = total_packages_delivered / max(1, self.warehouse.time_stamp)
            summary_text += f"Packages per tick: {packages_per_tick:.3f}\n"
        
        # Bot utilization
        idle_bots = sum(1 for bot in self.warehouse.bots if bot.status == 'idle' and not bot.assigned_packages)
        busy_bots = len(self.warehouse.bots) - idle_bots
        utilization = busy_bots / max(1, len(self.warehouse.bots)) * 100
        summary_text += f"Bot utilization: {utilization:.1f}% ({busy_bots}/{len(self.warehouse.bots)} bots busy)\n"
        
        # GA info if used
        if self.simulation.use_ga and hasattr(self.warehouse.ga_optimizer, 'fitness_history'):
            if self.warehouse.ga_optimizer.fitness_history:
                initial_avg = self.warehouse.ga_optimizer.fitness_history[0][0]
                final_avg = self.warehouse.ga_optimizer.fitness_history[-1][0]
                improvement = ((final_avg - initial_avg) / max(0.001, initial_avg)) * 100
                summary_text += f"GA Improvement: {improvement:.1f}%\n"
        
        # Display text
        self.ax_summary.text(0, 1, summary_text, transform=self.ax_summary.transAxes,
                           verticalalignment='top', fontsize=10, fontfamily='monospace',
                           bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.9))
    
    def animate(self, frame):
        """Animation update function"""
        if self.simulation.update():
            self.draw_grid()
            # Update GA graph if needed
            if self.simulation.use_ga and hasattr(self.warehouse, 'ga_optimizer'):
                self.init_ga_graph()
        else:
            self.draw_grid()
            plt.figtext(0.5, 0.02, "SIMULATION COMPLETE!", ha='center', 
                       fontsize=14, fontweight='bold', color='green')
        
        return []
    
    def run_animation(self, interval=500):
        """Run the animation"""
        anim = FuncAnimation(self.fig, self.animate, frames=None,
                           interval=interval, blit=False, repeat=False)
        plt.tight_layout()
        plt.show()

def main():
    """Main function to run the simulation"""
    print("="*60)
    print("WAREHOUSE PACKAGE PICKING SIMULATION WITH GA OPTIMIZATION")
    print("="*60)
    print("Features:")
    print("- Grid-based warehouse with shelves as obstacles")
    print("- Bots cannot enter shelf cells")
    print("- One-way aisles (alternating up/down)")
    print("- Collision avoidance between bots")
    print("- Genetic Algorithm optimization of package assignment")
    print("- Real-time visualization with GA progress graph")
    print("="*60)
    
    # Get parameters
    try:
        rows = int(input("Rows (10-30, default 15): ") or 15)
        cols = int(input("Columns (15-40, default 20): ") or 20)
        num_bots = int(input("Bots (1-10, default 3): ") or 3)
        num_packages = int(input("Packages (1-30, default 10): ") or 10)
        
        use_ga_input = input("Use Genetic Algorithm optimization? (y/n, default y): ") or 'y'
        use_ga = use_ga_input.lower() in ['y', 'yes']
        
        # Validate
        rows = max(10, min(30, rows))
        cols = max(15, min(40, cols))
        num_bots = max(1, min(10, num_bots))
        num_packages = max(1, min(30, num_packages))
        
    except ValueError:
        print("Invalid input! Using defaults.")
        rows, cols, num_bots, num_packages = 15, 20, 3, 10
        use_ga = True
    
    print("\n" + "="*60)
    print(f"Warehouse: {rows}x{cols}")
    print(f"Bots: {num_bots}, Packages: {num_packages}")
    print(f"GA Optimization: {'ENABLED' if use_ga else 'DISABLED'}")
    print("="*60)
    print("Starting simulation...")
    print("Close window to see final statistics.")
    
    # Run simulation
    simulation = WarehouseSimulation(rows, cols, num_bots, num_packages, use_ga)
    visualizer = WarehouseVisualizer(simulation)
    visualizer.run_animation(interval=400)

if __name__ == "__main__":
    main()