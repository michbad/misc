# Michal Badura
# Using a genetic algorithm to create a walking bassline for a sequence of chords
# Fitness is evaluated by hitting the chord notes on the upbeats, not having large intervals and not containing repeatedly the same notes
import random
import itertools

#notes are represented as integers, 0 being C2, 1 being C#2 and so on
#we start at C2

notes_dict = {"C":0, "C#":1, "D":2, "D#":3, "E":4, "F":5, "F#":6, "G":7, "G#":8,
              "A":9, "A#":10, "B":11}
idx_dict = {val:key for (key,val) in notes_dict.items()}

def name_to_idx(name):
    octave = int(name[-1])
    note = name[0:-1]
    return 12*(octave-2)+notes_dict[note]

def idx_to_name(idx):
    octave = idx // 12
    note = idx%12
    return idx_dict[note]+str(octave+2)

def chord_to_idx(tonic, kind):
    s = name_to_idx(tonic+"2") #as name_to_idx requires octave
    if kind=="maj":
        return [s, s+4, s+7]
    if kind=="m":
        return [s,s+3, s+7]
    if kind=="7":
        return [s, s+4, s+7, s+10]
    if kind=="maj7":
        return [s,s+4,s+7,s+11]
    if kind=="m7":
        return [s,s+3,s+7,s+10]
    


def interval(note1, note2):
    return abs(note1 - note2)


class Environment():
    def __init__(self, chords, duration=4, mating=0.5, mutating=0.1,
                 size=10, carry=4, fitness_coef=1, no_conseq=True):
        self.chords = chords
        self.duration = duration #how many notes for each chord
        self.mating = mating #chance of mating between two lines
        self.mutating = mutating
        self.size = size
        self.chordline = [[chord]*duration for chord in chords] #one chord item for each note
        self.chordline = [chord for chord in chords for chords in self.chordline]
        self.carry = carry #how many best lines are carried over to next generation
        self.fitness_coef = fitness_coef #importance of boredom in proportion to terseness for fitness
        self.octaves = 2
        self.note_range = list(range(0, 12*self.octaves))
        self.length = len(self.chordline)
        self.no_conseq = no_conseq #do we allow consecutive identical notes

        self.generation = [self.randomLine() for _ in range(self.size)]
        self.fitdict = self.createFitnessDict()
        self.best_line = []
        self.best_fitness = -1

    def randomChordNote(self, chord):
        return random.choice(chord) + 12*random.randint(0, self.octaves-1)

    def randomLine(self):
        line = []
        for i in range(self.length):
            if i%2==0:
                line.append(self.randomChordNote(self.chordline[i]))
            else:
                if self.no_conseq:
                    note = random.choice(self.note_range)
                    while note==line[i-1]:
                           note = random.choice(self.note_range)
                    line.append(note)
                else:
                    line.append(random.choice(self.note_range))
        return line

    def createFitnessDict(self):
        fitdict = {i:self.fitness(self.generation[i]) for i in range(self.size)}
        return fitdict

    def topLines(self, nlines):
        """Gets best nlines lines from the current generation"""
        result = []
        fitdictcp = dict(self.fitdict) #copy, so that real one not affected by changes
        for i in range(nlines):
            best_key = max(fitdictcp.keys(), key=lambda k: fitdictcp[k])
            result.append(self.generation[best_key])
            del fitdictcp[best_key]
        return result
        

    def fitness(self,line):
        terseness = sum([interval(line[i], line[i+1])**2 for i in range(len(line)-1)])
        boredom = 0
        for i in range(4, self.length):
            for j in range(0,4):
                if line[i-j] == line[i]:
                    boredom += 1
            
        return 1/(terseness + self.fitness_coef * boredom**2)

    def mutate(self, line):
        for i in range(self.length):
            if random.random() < self.mutating:
                if i%2==0:
                    line[i] = self.randomChordNote(self.chordline[i])
                else:
                    note = random.choice(self.note_range)
                    if self.no_conseq:
                        while note==line[i-1]:
                            note = random.choice(self.note_range)
                    line[i] = note
        return line

    def crossover(self, line1, line2):
        split = random.choice(range(self.length))
        new_line = line1[:split]+line2[split:]
        return new_line

    def roulette(self):
        total = sum(self.fitdict.values())
        target = random.uniform(0,total)
        for key in self.fitdict:
            target -= self.fitdict[key]
            if target<0:
                return self.generation[key]

    def newGeneration(self):
        new_generation = []
        for line in self.topLines(self.carry):
            new_generation.append(line)
        while len(new_generation) < self.size:
            parent1 = self.roulette()
            parent2 = self.roulette()
            if random.random() < self.mating:
                child1, child2 = self.crossover(parent1, parent2), self.crossover(parent1, parent2)
            else:
                child1, child2 = parent1, parent2
            child1, child2 = self.mutate(child1), self.mutate(child2)
            new_generation.append(child1)
            new_generation.append(child2)
        self.generation = new_generation
        self.fitdict = self.createFitnessDict()

    def evolve(self, time):
        for t in range(time):
            #if t%1000==0:
            #    print(1/self.best_fitness)
            self.newGeneration()
            current_best_line = self.topLines(1)[0]
            current_best_fitness = self.fitness(current_best_line)
            if current_best_fitness > self.best_fitness:
                self.best_line = current_best_line
                self.best_fitness = current_best_fitness

    def showResult(self):
        return [idx_to_name(i) for i in self.best_line]
                
        
                

test_chords = [chord_to_idx(a,b) for (a,b) in [("D","m7"), ("G","7"), ("C","maj7"),("A","m7")]]
env = Environment(test_chords, size=10, carry=5, mutating=0.07, mating=0.85, fitness_coef=15)
env.evolve(10000)
print(env.showResult())

        
        
