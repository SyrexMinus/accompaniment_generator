import random
from typing import Callable, List, Tuple

from genetic_algorithm.mutation_strategy import get_random_candidate
from logging.logging import log
from logging.logging_constants import INFO_LEVEL
from music_interfaces.composition.composition import Composition


class GeneticAlgorithm:
    """Implementation of genetic algorithm for generating accompaniment for a given melody."""
    def __init__(self, melody: Composition, fitness_function: Callable[[Composition, Composition], float],
                 crossover_strategy: Callable[[Composition, Composition, float], Tuple[Composition, Composition]],
                 mutation_strategy: Callable[[Composition, float], Composition]):
        self.melody = melody
        self.fitness_function = fitness_function
        self.crossover_strategy = crossover_strategy
        self.mutation_strategy = mutation_strategy

    def get_init_generation(self, candidates_num: int) -> List[Composition]:
        """Return randomly generated accompaniments."""
        return [get_random_candidate(self.melody) for i in range(candidates_num)]

    def get_next_generation(self, candidates_fitness_sorted: List[Tuple[Composition, float]], mutation_chance: float,
                            best_parents_num: int, random_parents_num: int, generation_size: int,
                            similarity_to_single_parent: float) -> List[Composition]:
        """Returns Compositions as a result of mutation on results of crossover of given candidates.

        Compositions for crossover (parents) are selected among the best and random candidates, the number of which is
        given by parameters best_parents_num and random_parents_num, respectively. The offspring is obtained as a result
        of a crossover between random pairs of parents.

        """
        parents_num = best_parents_num + random_parents_num
        assert parents_num >= 2, "at least two parents should be provided to make crossover"
        assert len(candidates_fitness_sorted) >= parents_num, "parents_num can not exceed size of population"
        parents = candidates_fitness_sorted[:best_parents_num] + \
                  random.sample(candidates_fitness_sorted[best_parents_num:], random_parents_num)
        log(f"\tAverage parents fitness:\t"
            f"{sum([fitn for cand, fitn in parents]) / parents_num}\n"
            f"\tAverage best parents fitness:\t"
            f"{(sum([fitn for cand, fitn in candidates_fitness_sorted[:best_parents_num]]) / best_parents_num) if best_parents_num != 0 else 0}\n"
            f"\tAverage random parents fitness:\t"
            f"{(sum([fitn for cand, fitn in candidates_fitness_sorted[best_parents_num:]]) / random_parents_num) if random_parents_num != 0 else 0}")
        # crossover children
        children = []
        while len(children) < generation_size:
            parent12 = random.sample(parents, 2)
            child1, child2 = self.crossover_strategy(parent12[0][0], parent12[1][0], similarity_to_single_parent)
            if generation_size - len(children) > 1:
                children.extend([child1, child2])
            else:
                children.append(child1)
        # mutate children
        for i, child in enumerate(children):
            children[i] = self.mutation_strategy(child, mutation_chance)

        return children

    def solve(self, generation_size: int, mutation_chance: float, best_parents_num: int, random_parents_num: int,
              similarity_to_single_parent: float, target_fitness: float = None, iterations_num: int = None) \
            -> (Composition, float):
        """Return best accompaniment of last offspring and its fitness value.

        Algorithm generate new offsprings until desired number of iterations is reached or target fitness is obtained.

        """
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
                                                              generation_size=generation_size,
                                                              similarity_to_single_parent=similarity_to_single_parent)
                ],
                key=lambda candidate_fitness: candidate_fitness[1]
            )
            best_candidate, best_fitness = candidates_fitness[0]
            log(f"{i+1}\t generation info:\n\tBest fitness:\t{best_fitness}\n\tAverage fitness:\t"
                f"{sum([fitn for cand, fitn in candidates_fitness]) / len(candidates_fitness)}")
            i += 1
        return best_candidate, best_fitness
