# Conductor: Accompaniment generator based on genetic algorithm
Accompaniment generator based on genetic algorithm implemented in Python. Algorithm accepts MIDI file with melody and
outputs MIDI file with merged melody and accompaniment on two separate tracks.

## Usage

The steps to obtain a music of given melody and generated accompaniment are:

1. `pip3 install -r requirements.txt`
2. (Optional step) Configure fitness and mutation functions parameters in *app_config.py* 
3. `python3 main.py -ifp input/barbiegirl_mono.mid -in 100` (command line parameters description: 
`python3 main.py -h`)
4. Wait until the script completes its work.
5. Resulting melody with accompaniment, pure accompaniment and results description files will be saved to 
*save_dir_path/N/*.

## Results example

The given melody:

https://user-images.githubusercontent.com/57181871/167402860-f87e4b0f-1850-46c1-b918-1987e0433cd4.mp4

The melody with generated accompaniment:

https://user-images.githubusercontent.com/57181871/167402892-ca3c2e58-8cc5-48f0-9be0-aa89505affc8.mp4

## Project description

### Introduction

The project was implemented as part of the course Introduction to Artificial Intelligence in Innopolis University. 
The task was to apply the theory of genetic algorithms in practice. The task was to generate an accompaniment to a 
given melody. The task required the use of mutation and crossover in the genetic algorithm. For accompaniment, it 
was proposed to use chords consisting of only three notes, or rests.

The result of the work is a Python code for generating accompaniment using a genetic algorithm. The resulting music was 
liked by 83% of people from the focus group.

### Implementation

#### Genetic algorithm

The genetic algorithm for generating the accompaniment was implemented according to a model, which included the 
generation of the initial population and cyclic process of selection of individuals using the fitness function, 
crossover, and mutation. The result of the algorithm is the best accompaniment from the last generation in terms of 
fitness value. The algorithm iterates through new generations until an individual with the required fitness value 
appears among the population or the limit on the number of iterations performed is reached.

##### Initial population generation

The initial accompaniment population is generated as a sequence of random chords at random positions on the stave at 
each beat tick.

##### Crossover

The uniform order crossover type was chosen for the crossover process. This means that each chord could be swapped 
between two parent accompaniments regardless of its position in the timeline. At the same time, the position of the 
chords in the timeline was preserved.

##### Mutation

The mutation is applied chordally to each individual in the population. Each chord in the accompaniment can be mutated 
with a parameterized probability. For one mutation of a chord, one transformation can be randomly applied among: 
randomly shifting all the notes of the chord by a random limited amount, moving all the notes of the chord by a random 
unlimited amount, and replacing the chord with another random chord. The division into limited displacement was made to 
speed up the process of finding the optimal position of chords in the learning process.

##### Fitness

The value of fitness shows the goodness of the accompaniment in combination with this melody. In the implementation 
less means better. The fitness evaluation function is implemented in two steps, namely, the calculation of metrics, 
and then the calculation of the fitness value according to the given award value as a multiplication of the award value 
by the corresponding metric value. Metrics award values were experimentally derived.

The list of calculated metrics for accompaniment with their award values and description is listed next:
- Correct chord for melody key, -9, applicable chord for melody key was used; 
- Completed progression, -1, progression inside 4-quarter interval was fully applied;
- Partial progression, -4, progression was partially implemented, the value of the metric is proportional to the share of the realized progression;
- Chord is not below melody, 20, one of the notes in chord is not below lowest note in melody;
- Too low chord, 15, lowest note is below allowable;
- Too wide accompaniment range, 10, the chord is further from the median of the chords than the allowable distance in notes;
- Chord include melody note, -3, proportion of incoming notes from the melody to the accompaniment by position within octave;
- Missing accompaniment for melody, 8, at a certain moment, a note from the melody plays, but not a single note in the accompaniment plays;
- Excessive accompaniment chord, 4, a note from the accompaniment plays at a certain moment, but not a single note in the melody plays;
- Too big chord drop, 10, the difference between the lowest notes of two consecutive chords exceeds the allowable value;
- Accompaniment chord exists, -2, at a certain point a chord was used in the accompaniment;
- Empty accompaniment, 10000, accompaniment contain no notes at all

#### Chords used

The list of the used chords for the accompaniment generation is stated next:
- Major triad;
- Minor triad;
- First inversion of major triad;
- Second inversion of major triad;
- First inversion of minor triad;
- Second inversion of minor triad;
- Diminished;
- Sus2;
- Sus4;
- Empty chord

The list was compiled in accordance with the recommendations of the task.

#### App config

The set of settings has been included in the implementation for code maintainability. It includes function switches and 
the definition of global variables, namely metric count switches, definitions needed to calculate them, reward values 
for each metric, definitions for mutation functions, Note class, and a logging level switch. It is specified in 
*app_config.py* section of Python script code.

#### Composition 

The Composition class is an interface for working with notes and metadata in music. The class includes a set of methods 
for working with chords, melody and MIDI files.

### Results

The result of the work is the implementation of the genetic algorithm in the Python programming language, a number of 
music files with melodies and accompaniments generated by the algorithm and interesting observations. 

In the process of testing various parameters of the genetic algorithm, the following facts were noticed. 
- A smaller sample of the best individuals for the generation of the next generation gives faster, in terms of 
iterations, the achievement of the desired fitness values; 
- Using too large mutation_chance values can slow down the learning process;
- More iterations of the genetic algorithm gives a better average fitness value for the population.

In the course of a survey of a focus group consisting of five students of Innopolis University and one resident of the 
city of Innopolis, it was found that 83% of people like music with an accompaniment generated by an implemented 
algorithm.

### Discussion

The list of chords and progressions considered by the algorithm can be extended. But this has a drawback in the form 
that it will increase the search area and, accordingly, the algorithm's running time.

For the fitness function, a non-linear evaluation method can be used, which could potentially improve the pleasance of 
the accompaniment. In this case, the selection of award values can become more complex.

### Conclusion
The genetic algorithm turned out to be a working tool for the task of generating an accompaniment to a given melody. In 
the course of the work, the influence of the parameters of the genetic algorithm on the learning process and results 
was revealed. The work experimentally identified influential metrics for assessing the nobility of sound. The 
implementation of the genetic included the use of a limited set of mutations, a uniform order crossover, and a limited 
set of triad chords. The resulting music was found enjoyable by 83% of listeners.

