import os
import time

import mido

from app_config import EVENT_TO_AWARD_WEIGHTS
from genetic_algorithm.crossover_strategy import make_crossover
from genetic_algorithm.fitness_function.fitness_function import fitness_function, calculate_metrics
from genetic_algorithm.genetic_algorithm import GeneticAlgorithm
from genetic_algorithm.mutation_strategy import make_mutation
from music_interfaces.composition.composition import Composition

# Specify inputs
input_file_name = "input1"
generation_size = 200
mutation_chance = 0.005
best_parents_num = 10
random_parents_num = 1
iterations_num = 1
target_fitness = None
similarity_to_single_parent = 0.5

# Run algorithm
start_time = time.time()
melody = Composition(midi_file=mido.MidiFile(f"input/{input_file_name}.mid"))
gen_alg = GeneticAlgorithm(melody=melody, fitness_function=fitness_function, crossover_strategy=make_crossover,
                           mutation_strategy=make_mutation)
accompaniment, fitness = gen_alg.solve(generation_size=generation_size, mutation_chance=mutation_chance,
                                       best_parents_num=best_parents_num, random_parents_num=random_parents_num,
                                       similarity_to_single_parent=similarity_to_single_parent,
                                       target_fitness=target_fitness, iterations_num=iterations_num)
execution_time = time.time() - start_time
print(f"Execution time: {execution_time}")
print(f"Accompaniment fitness: {fitness}")

# Save results
save_dir_path = f"output/{input_file_name}/"
os.makedirs(os.path.dirname(save_dir_path), exist_ok=True)
i = 1
while os.path.isdir(f"{save_dir_path}/{i}"):
    i += 1
save_dir_path = f"{save_dir_path}{i}/"
os.makedirs(os.path.dirname(save_dir_path), exist_ok=True)
merge = accompaniment + melody
merge.save_midi(f"{save_dir_path}{input_file_name}_with_accompaniment.mid")
accompaniment.save_midi(f"{save_dir_path}/{input_file_name}_accompaniment.mid")
with open(f"{save_dir_path}/result_description.txt", "w") as description_file:
    description_file.write(f"Config:\n"
                           f"\tgeneration_size = {generation_size}\n"
                           f"\tmutation_chance = {mutation_chance}\n"
                           f"\tbest_parents_num = {best_parents_num}\n"
                           f"\trandom_parents_num = {random_parents_num}\n"
                           f"\tsimilarity_to_single_parent = {similarity_to_single_parent}\n"
                           f"\titerations_num = {iterations_num}\n"
                           f"\ttarget_fitness = {target_fitness}\n"
                           f"\tEVENT_TO_AWARD_WEIGHTS = {EVENT_TO_AWARD_WEIGHTS}\n"
                           f"\n"
                           f"Results:\n"
                           f"\tAccompaniment fitness: {fitness}\n"
                           f"\tExecution time: {execution_time}\n"
                           f"\tMetrics: {calculate_metrics(melody, accompaniment)}")
