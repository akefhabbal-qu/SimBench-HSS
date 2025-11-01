import random

from ..AlgorithmBase import AlgorithmBase

class GeneticAlgorithm(AlgorithmBase):
    # TODO:
        # Optimize Greedy with Genetic Algorithm
        # Threshold Algorithm (using Genatic Algorithm) we can call it Genetic
        # write a disscussion about the online vs offline algorithms and experiments showing the adaptation
        # of change of the access pattern

    def apply(self, file):
        """Genetic algorithm for optimizing file placement."""
        population_size = 10
        generations = 10
        mutation_rate = 0.1

        # Initialize population with random chromosomes (random tier assignment)
        population = [self.random_chromosome() for _ in range(population_size)]

        for _ in range(generations):
            # Evaluate fitness of the population (sorted based on fitness)
            population = sorted(population, key=lambda x: self.fitness_function(x))

            # Selection: Keep the top 50% of the population
            population = population[:population_size // 2]

            # Crossover: Produce children by crossover between parents
            children = []
            while len(children) < population_size // 2:
                parent1, parent2 = random.sample(population, 2)
                child = self.crossover(parent1, parent2)
                children.append(child)

            # Mutation: Randomly mutate some children
            population += [self.mutate(child, mutation_rate) for child in children]

        # Choose the best solution from the final population and apply it
        best_chromosome = population[0]
        self.apply_chromosome(best_chromosome)

    def random_chromosome(self):
        """Generate a random chromosome (random tier assignments for files)."""
        return [random.choice(self.sys.storage_tiers) for _ in range(self.sys.num_files)]

    def crossover(self, parent1, parent2):
        """Perform crossover between two parent chromosomes."""
        crossover_point = random.randint(0, self.sys.num_files - 1)
        return parent1[:crossover_point] + parent2[crossover_point:]

    def mutate(self, chromosome, mutation_rate=0.1):
        """Mutate a chromosome with the given mutation rate."""
        for i in range(len(chromosome)):
            if random.random() < mutation_rate:
                chromosome[i] = random.choice(self.sys.storage_tiers)
        return chromosome

    def apply_chromosome(self, chromosome):
        """Apply the tier assignments from the best chromosome to the system."""
        for i, tier in enumerate(chromosome):
            for replica in self.sys.files[i].replicas:
                replica.storage_tier = tier

    def fitness_function(self, chromosome):
        """Fitness function based on the optimization metrics."""
        total_cost = 0
        total_response_time = 0
        total_replicas = 0
        total_unavailability = 0

        for i, file in enumerate(self.sys.files):
            tier = chromosome[i]
            total_cost += file.size * tier.cost
            total_replicas += len(file.replicas)

            try:
                total_response_time += file.accesses * tier.get_response_time()
            except Exception as e:
                # Assign a default high response time if the tier is unavailable
                total_response_time += file.accesses * 100  # Arbitrary high response time
                total_unavailability += 1
                continue

        # Normalize values by the number of files
        normalized_cost = total_cost / self.sys.num_files
        normalized_response_time = total_response_time / self.sys.num_files
        normalized_replicas = total_replicas / self.sys.num_files
        normalized_unavailability = total_unavailability / self.sys.num_files

        # Optimization function to minimize
        O = (self.sys.alpha * normalized_cost) + \
            (self.sys.beta * normalized_response_time) + \
            (self.sys.gamma * normalized_replicas) - \
            (self.sys.delta * normalized_unavailability)

        return O
    
    def name(self):
        return "GeneticAlgorithm"