import random
from math import ceil
from typing import Callable, List, Tuple

from composition.composition import Composition


class GeneticAlgorithm:
    def __init__(self, melody: Composition, fitness_function: Callable[[Composition, Composition], float],
                 reproduction_function: Callable[[Composition, int], List[Composition]],
                 crossover_strategy: Callable[[Composition, Composition], (Composition, Composition)],
                 mutation_strategy: Callable[[Composition], Composition]):
        self.melody = melody
        self.fitness_function = fitness_function
        self.reproduction_function = reproduction_function
        self.crossover_strategy = crossover_strategy
        self.mutation_strategy = mutation_strategy

    def get_init_generation(self, candidates_num: int) -> List[Composition]:
        raise NotImplementedError  # TODO

    def get_next_generation(self, candidates_fitness_sorted: List[Tuple[Composition, float]], children_num: int,
                            mutation_chance: float, best_parents_percent: float) -> List[Composition]:
        assert children_num % 2 == 0, "children_num must be even"
        assert 0 <= mutation_chance <= 1, "mutation_chance must belong to [0:1] interval"
        assert 0 <= best_parents_percent <= 1, "best_parents_percent must belong to [0:1] interval"
        parents_num = children_num
        best_parents_num = ceil(children_num * best_parents_percent)
        random_parents_num = parents_num - best_parents_num
        parents = candidates_fitness_sorted[:best_parents_num] + \
                  [
                      candidates_fitness_sorted[i]
                      for i in random.sample(range(best_parents_num, parents_num), random_parents_num)
                  ]
        # crossover children
        children = []
        parent_pairs = random.sample(range(parents_num), parents_num)
        for i in range(int(parents_num / 2)):
            parent1, parent2 = parents[i][0], parents[i * 2][0]
            child1, child2 = self.crossover_strategy(parent1, parent2)
            children.extend([child1, child2])
        # mutate children
        for i, child in enumerate(children):
            if random.random() < mutation_chance:
                children[i] = self.mutation_strategy(child)
        return children

    def solve(self, candidates_num: int, mutation_chance: float, best_parents_percent: float,
              target_fitness: float = None, iterations_num: int = None) -> (Composition, float):
        assert (target_fitness is None or iterations_num is None) and \
               (target_fitness is not None or iterations_num is not None), "exactly one of {target_fitness, " \
                                                                           "iterations_num} must be used"
        candidates_fitness = sorted(
            [
                (candidate, self.fitness_function(self.melody, candidate))
                for candidate in self.get_init_generation(candidates_num)
            ],
            key=lambda candidate_fitness: candidate_fitness[1]
        )
        best_candidate, best_fitness = candidates_fitness[0]
        i = 0
        while (target_fitness is not None and best_fitness > target_fitness) or \
                (iterations_num is not None and i < iterations_num):
            candidates_fitness = sorted(
                [
                    (candidate, self.fitness_function(self.melody, candidate))
                    for candidate in self.get_next_generation(candidates_fitness_sorted=candidates_fitness,
                                                              children_num=candidates_num,
                                                              mutation_chance=mutation_chance,
                                                              best_parents_percent=best_parents_percent)
                ],
                key=lambda candidate_fitness: candidate_fitness[1]
            )
            best_candidate, best_fitness = candidates_fitness[0]
            i += 1
        return best_candidate, best_fitness
