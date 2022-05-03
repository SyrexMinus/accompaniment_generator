import random
from math import ceil
from typing import Callable, List, Tuple

from genetic_algorithm.mutation_strategy import get_random_candidate
from logging.logging import log
from logging.logging_constants import INFO_LEVEL
from music_interfaces.composition.composition import Composition


class GeneticAlgorithm:
    def __init__(self, melody: Composition, fitness_function: Callable[[Composition, Composition], float],
                 crossover_strategy: Callable[[Composition, Composition], Tuple[Composition, Composition]],
                 mutation_strategy: Callable[[Composition, float], Composition]):
        self.melody = melody
        self.fitness_function = fitness_function
        self.crossover_strategy = crossover_strategy
        self.mutation_strategy = mutation_strategy

    def get_init_generation(self, candidates_num: int) -> List[Composition]:
        return [get_random_candidate(self.melody) for i in range(candidates_num)]

    def get_next_generation(self, candidates_fitness_sorted: List[Tuple[Composition, float]], mutation_chance: float,
                            best_parents_num: int, random_parents_num: int, generation_size: int) -> List[Composition]:
        parents_num = best_parents_num + random_parents_num
        assert parents_num >= 2, "at least two parents should be provided to make crossover"
        assert len(candidates_fitness_sorted) >= parents_num, "parents_num can not exceed size of population"
        parents = candidates_fitness_sorted[:best_parents_num] + \
                  random.sample(candidates_fitness_sorted[best_parents_num:], random_parents_num)
        log(f"\n\tAverage parents fitness:\t"
            f"{sum([fitn for cand, fitn in parents]) / parents_num}")
        log(f"\n\tAverage best parents fitness:\t"
            f"{sum([fitn for cand, fitn in candidates_fitness_sorted[:best_parents_num]]) / best_parents_num}")
        log(f"\n\tAverage random parents fitness:\t"
            f"{sum([fitn for cand, fitn in candidates_fitness_sorted[best_parents_num:]]) / random_parents_num}")
        # crossover children
        children = []
        while len(children) < generation_size:
            parent12 = random.sample(parents, 2)
            child1, child2 = self.crossover_strategy(parent12[0][0], parent12[1][0])
            if generation_size - len(children) > 1:
                children.extend([child1, child2])
            else:
                children.append(child1)
        # mutate children
        for i, child in enumerate(children):
            children[i] = self.mutation_strategy(child, mutation_chance)
        return children

    def solve(self, generation_size: int, mutation_chance: float, best_parents_num: int, random_parents_num: int,
              target_fitness: float = None, iterations_num: int = None) -> (Composition, float):
        assert (target_fitness is None or iterations_num is None) and \
               (target_fitness is not None or iterations_num is not None), "exactly one of {target_fitness, " \
                                                                           "iterations_num} must be used"
        log(f"Genetic algorithm init", INFO_LEVEL)
        candidates_fitness = sorted(
            [
                (candidate, self.fitness_function(self.melody, candidate))
                for candidate in self.get_init_generation(generation_size)
            ],
            key=lambda candidate_fitness: candidate_fitness[1]
        )
        best_candidate, best_fitness = candidates_fitness[0]
        log(f"Init generation info:\n\tBest fitness:\t{best_fitness}\n\tAverage fitness:\t"
            f"{sum([fitn for cand, fitn in candidates_fitness]) / len(candidates_fitness)}")
        i = 0
        while (target_fitness is not None and best_fitness > target_fitness) or \
                (iterations_num is not None and i < iterations_num):
            candidates_fitness = sorted(
                [
                    (candidate, self.fitness_function(self.melody, candidate))
                    for candidate in self.get_next_generation(candidates_fitness_sorted=candidates_fitness,
                                                              mutation_chance=mutation_chance,
                                                              best_parents_num=best_parents_num,
                                                              random_parents_num=random_parents_num,
                                                              generation_size=generation_size)
                ],
                key=lambda candidate_fitness: candidate_fitness[1]
            )
            best_candidate, best_fitness = candidates_fitness[0]
            log(f"{i+1}\t generation info:\n\tBest fitness:\t{best_fitness}\n\tAverage fitness:\t"
                f"{sum([fitn for cand, fitn in candidates_fitness]) / len(candidates_fitness)}")
            i += 1
        return best_candidate, best_fitness
