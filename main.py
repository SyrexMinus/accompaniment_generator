import os
import time
from argparse import ArgumentParser

import mido

from app_config import EVENT_TO_AWARD_WEIGHTS
from genetic_algorithm.crossover_strategy import make_crossover
from genetic_algorithm.fitness_function.fitness_function import fitness_function, calculate_metrics
from genetic_algorithm.genetic_algorithm import GeneticAlgorithm
from genetic_algorithm.mutation_strategy import make_mutation
from music_interfaces.composition.composition import Composition, save_two_compostitions


GENERATION_SIZE_DEFAULT = 200
MUTATION_CHANCE_DEFAULT = 0.005
BEST_PARENTS_NUM_DEFAULT = 10
RANDOM_PARENTS_NUM_DEFAULT = 1
ITERATIONS_NUM_DEFAULT = 1000
TARGET_FITNESS_DEFAULT = None
SIMILARITY_TO_SINGLE_PARENT_DEFAULT = 0.5
SAVE_DIR_PATH_DEFAULT = "output/"

# Specify inputs
parser = ArgumentParser()
parser.add_argument("-ifp", "--input_file_path", dest="input_file_path",
                    help="Path to the input MIDI file with melody.", metavar="PATH")
parser.add_argument("-gs", "--generation_size", dest="generation_size",
                    help=f"Number of accompaniments in one generation. Default: {GENERATION_SIZE_DEFAULT}",
                    metavar="INT")
parser.add_argument("-mc", "--mutation_chance", dest="mutation_chance",
                    help=f"Chance that a chord in an accompaniment will be mutated. Default: {MUTATION_CHANCE_DEFAULT}",
                    metavar="FLOAT")
parser.add_argument("-bpn", "--best_parents_num", dest="best_parents_num",
                    help=f"Number of best accompaniments in a generation that will be used as parents for next "
                         f"generation. Default: {BEST_PARENTS_NUM_DEFAULT}", metavar="INT")
parser.add_argument("-rpn", "--random_parents_num", dest="random_parents_num",
                    help=f"Number of random accompaniments in a generation (except from best) that will be used as "
                         f"parents for next generation. Default: {RANDOM_PARENTS_NUM_DEFAULT}", metavar="INT")
parser.add_argument("-in", "--iterations_num", dest="iterations_num",
                    help=f"Limit number of iterations that genetic algorithm will perform. "
                         f"Default: {ITERATIONS_NUM_DEFAULT}", metavar="INT")
parser.add_argument("-tf", "--target_fitness", dest="target_fitness",
                    help=f"Target fitness of the best accompaniment after reaching which the algorithm will stop. "
                         f"Default: {TARGET_FITNESS_DEFAULT}",
                    metavar="FLOAT")
parser.add_argument("-stsp", "--similarity_to_single_parent", dest="similarity_to_single_parent",
                    help=f"Probability of performing a change of a chord in the crossover. "
                         f"Default: {SIMILARITY_TO_SINGLE_PARENT_DEFAULT}", metavar="FLOAT")
parser.add_argument("-sdp", "--save_dir_path", dest="save_dir_path",
                    help=f"Path to save directory. Default: {SAVE_DIR_PATH_DEFAULT}", metavar="PATH")
args = parser.parse_args()

generation_size = int(args.generation_size or GENERATION_SIZE_DEFAULT)
mutation_chance = float(args.mutation_chance or MUTATION_CHANCE_DEFAULT)
best_parents_num = int(args.best_parents_num or BEST_PARENTS_NUM_DEFAULT)
random_parents_num = int(args.random_parents_num or RANDOM_PARENTS_NUM_DEFAULT)
iterations_num = int(args.iterations_num or ITERATIONS_NUM_DEFAULT)
target_fitness = float(args.target_fitness) if args.target_fitness is not None else TARGET_FITNESS_DEFAULT
similarity_to_single_parent = float(args.similarity_to_single_parent or SIMILARITY_TO_SINGLE_PARENT_DEFAULT)
input_file_path = args.input_file_path
assert input_file_path is not None, "Specify input_file_path by \"python3 main.py -ifp PATH\""
save_dir_path = args.save_dir_path or SAVE_DIR_PATH_DEFAULT

input_file_path_normpath = os.path.normpath(input_file_path)
input_file_path_dir = input_file_path_normpath.split(os.sep)
input_file_name = os.path.splitext(input_file_path_dir[-1])[0]

save_dir_path_normpath = os.path.normpath(save_dir_path)
print(save_dir_path_normpath)


# Run algorithm
start_time = time.time()
melody = Composition(midi_file=mido.MidiFile(input_file_path_normpath))
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
os.makedirs(save_dir_path_normpath, exist_ok=True)
i = 1
while os.path.isdir(f"{save_dir_path_normpath}/{i}"):
    i += 1
save_dir_path = f"{save_dir_path_normpath}/{i}"
os.makedirs(save_dir_path, exist_ok=True)
melody.MIDI_TEMPLATE_PATH = input_file_path
save_two_compostitions(melody, accompaniment, f"{save_dir_path}/{input_file_name}_with_accompaniment.mid")
accompaniment.MIDI_TEMPLATE_PATH = input_file_path
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
print(f"Results were saved to {save_dir_path}")
