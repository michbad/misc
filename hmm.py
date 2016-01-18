#Michal Badura
#Hidden Markov Model learning algorithm and Viterbi algorithm for most likely sequence of states
#written as a part of Computational Linguistics class

import random
import sys
from math import log

PREC = 3

def genRandDist(n):
    probs = [random.random() for i in range(n)]
    normalized = [p/sum(probs) for p in probs]
    return normalized


def plog(x):
    return -1 * log(x,2)

def mergeDicts(dict1, dict2):
    """sums the values of two dicts that have the same keys, possibly recursively"""
    result = dict1
    for item in dict2:
        if type(dict2[item]) == dict:
            result[item] = mergeDicts(dict1[item], dict2[item])
        else:
            result[item] += dict2[item]
    return result


class HMM():
    def __init__(self, states=[0, 1], letters=["b","a","d","i", "#"], verboseFlag=True, out_path="log.txt", corpus = [],
                 initial=None, transitions=None, emissions=None):
        self.states = states
        self.verboseFlag = verboseFlag
        self.letters = letters
        self.corpus = corpus
        self.softCounts = {(orig, dest): {letter : 0 for letter in self.letters} for orig in self.states for dest in self.states}
        self.initialSoftCounts = {(orig, dest): {letter : 0 for letter in self.letters} for orig in self.states for dest in self.states}
        if initial == None:
            dist = genRandDist(len(states))
            self.initial = dict(zip(states, dist))
        else:
            self.initial = initial

        if transitions == None:
            self.transitions = {}
            for state in states:
                dist = genRandDist(len(list(states)))
                self.transitions[state] = dict(zip(states, dist))
        else:
            self.transitions = transitions

        if emissions == None:
            self.emissions = {}
            for state in states:
                dist = genRandDist(len(letters))
                self.emissions[state] = dict(zip(letters, dist))
        else:
            self.emissions = emissions      


        if verboseFlag:
            self.out = open(out_path, "w+")
            self.out.write("INITIALIZATION\n---------------------\n")
            self.out.write(self.strStateInfo())




    def strStateInfo(self):
        output = ""
        for state in self.states:
            output += "STATE {0}\n".format(state)
            output += "Transitions\n"
            for dest in self.states:
                output += "\t{0} to {1}: {2}\n".format(state,dest,self.transitions[state][dest])
            output+= "Emissions\n"
            for letter in sorted(self.emissions[state], key=lambda v: self.emissions[state][v], reverse=True):
                output += "\t{0}: {1}\n".format(letter, self.emissions[state][letter])
            output+= "\tTotal: {0}\n\n".format(sum(self.emissions[state].values()))

        output += "Initial probabilities\n"
        for state in self.states:
            output += "STATE {0}: {1}\n".format(state,self.initial[state])
        output += "\n\n"

        return output



    def computeAlpha(self, word, verboseFlag = None):
        if verboseFlag == None:
            verboseFlag = self.verboseFlag
        alpha = self.initial #a_i(1) = pi_i
        
        if verboseFlag:
            log = "----------\n"
            log += "Calculating forward probabilities for '{0}'\nInitial values:\n".format(word)
            for state in self.states:
                log += "\tState {0}: {1}\n".format(state, alpha[state])

        #time printed is actually t+2, as it was said in the lecture to start from 1, and first letter is emitted only after first state
        for t in range(len(word)):
            new_alpha = {}
            for dest in self.states:
                values = [(alpha[state] * self.emissions[state][word[t]] * self.transitions[state][dest], state) for state in self.states]
                new_alpha[dest] = sum([value[0] for value in values])

                if verboseFlag:
                    log += "\t\tTo state {0}\n".format(dest)
                    for value in values:
                        log += "\t\t\tfrom state {0}: {1}\n".format(value[1], value[0])

            alpha = new_alpha          

            if verboseFlag:
                log+= "\nProbabilities at time {0}, letter '{1}'\n".format(t+2, word[t])
                for (state, prob) in alpha.items():
                    log+= "\tState {0}: {1}\n".format(state, prob)
        
        final_alpha = sum(alpha.values())
        if verboseFlag:
            log += "\nFinal forward probability of string '{0}': {1}\n\n".format(word, final_alpha)
            self.out.write(log)
        
        return final_alpha

    def computeBeta(self, word, verboseFlag = None):        
        if verboseFlag == None:
            verboseFlag = self.verboseFlag
        beta = {state: 1 for state in self.states}         
        
        if verboseFlag:
            log = "----------\n"
            log += "Calculating backward probabilities for '{0}'\nInitial values:\n".format(word)
            for state in self.states:
                log += "\tState {0}: {1}\n".format(state, beta[state])

        #time printed is actually t+2, as it was said in the lecture to start from 1, and first letter is emitted only after first state
        for t in reversed(range(len(word))):
            new_beta = {}
            for origin in self.states:
                values = [(beta[state] * self.emissions[origin][word[t]] * self.transitions[origin][state],state) for state in self.states]
                new_beta[origin] = sum([value[0] for value in values])
            
                if verboseFlag:
                    log += "\t\tFrom state {0}\n".format(origin)
                    for value in values:
                        log += "\t\t\tto state {0}: {1}\n".format(value[1], value[0])

            beta = new_beta

            if verboseFlag:
                log+= "\nProbabilities at time {0}, letter '{1}'\n".format(t+2, word[t])
                for (state, prob) in beta.items():
                    log+= "\tState {0}: {1}\n".format(state, prob)

        final_beta = sum([beta[state] * self.initial[state] for state in self.states])
        if verboseFlag:
            log += "\nFinal backward probability of string '{0}': {1}\n\n".format(word, final_beta)
            self.out.write(log)

        return final_beta


    def computeAlphaPartial(self, word, state, numLetters):
        alpha = self.initial

        for t in range(numLetters):
            new_alpha = {}
            for dest in self.states:
                values = [(alpha[state] * self.emissions[state][word[t]] * self.transitions[state][dest], state) for state in self.states]
                new_alpha[dest] = sum([value[0] for value in values])

            alpha = new_alpha          
        return alpha[state]

    def computeBetaPartial(self, word, state, numLeftLetter):
        beta = {state: 1 for state in self.states}    
        for t in reversed(range(numLeftLetter, len(word))):
            new_beta = {}
            for origin in self.states:
                values = [(beta[state] * self.emissions[origin][word[t]] * self.transitions[origin][state],state) for state in self.states]
                new_beta[origin] = sum([value[0] for value in values])
            beta = new_beta
        return beta[state]        


    def computeSoftCounts(self, word, verboseFlag = None):
        if verboseFlag == None:
            verboseFlag = self.verboseFlag

        if verboseFlag:
            log = "SOFT COUNTS for {0}\n-----------------------\n".format(word)

        wordProb = self.computeAlpha(word, verboseFlag=False)
        softCounts = {(orig, dest): {letter : 0 for letter in self.letters} for orig in self.states for dest in self.states}
        
        for t in range(len(word)):
            letter = word[t]
            if verboseFlag:
                log += "\tLetter: {0}\n".format(letter)
            for (orig, dest) in softCounts:
                value = self.computeAlphaPartial(word, orig, t) * self.transitions[orig][dest] * \
                        self.emissions[orig][letter] * self.computeBetaPartial(word, dest, t+1) / wordProb
                softCounts[(orig, dest)][letter] += value

                if verboseFlag:
                    log += "\t\tFrom state {0} to state {1}: {2:.{P}f}\n".format(orig, dest, value, P=PREC)

        if verboseFlag:
            log += "\nExpected counts table: \n"
            for letter in sorted(self.letters):
                for (orig, dest) in softCounts:
                    log += "\t{0}\t{1}\t{2}\t{3:.{P}f}\n".format(letter, orig, dest, softCounts[(orig,dest)][letter], P=PREC)                  
            self.out.write(log)
        
        return softCounts


    def computeInitialSoftCounts(self, word, verboseFlag = None):
        if verboseFlag == None:
            verboseFlag = self.verboseFlag

        wordProb = self.computeAlpha(word, verboseFlag=False)
        softCounts = {(orig, dest): {letter : 0 for letter in self.letters} for orig in self.states for dest in self.states}
        t = 0
        letter = word[t]
        for (orig, dest) in softCounts:
                value = self.computeAlphaPartial(word, orig, t) * self.transitions[orig][dest] * \
                        self.emissions[orig][letter] * self.computeBetaPartial(word, dest, t+1) / wordProb
                softCounts[(orig, dest)][letter] += value

        return softCounts

    def showSoftCounts(self):
        log = ""
        log += "SOFT COUNTS FOR THE ENTIRE CORPUS\n-----------------------------\n"
        for letter in sorted(self.letters):
            for (orig, dest) in self.softCounts:
                log += "\t{0}\t{1}\t{2}\t{3:.{P}f}\n".format(letter, orig, dest, self.softCounts[(orig,dest)][letter], P=PREC)
        log += "\n\tInitial counts\n\t--------------\n"                
        for letter in sorted(self.letters):
            for (orig, dest) in self.initialSoftCounts:
                log += "\t{0}\t{1}\t{2}\t{3:.{P}f}\n".format(letter, orig, dest, self.initialSoftCounts[(orig,dest)][letter], P=PREC)
        return log

    def setCorpusSoftCounts(self, verboseFlag = None):
        if verboseFlag == None:
            verboseFlag = self.verboseFlag

        for word in self.corpus:
            self.computeAlpha(word, verboseFlag)
            self.computeBeta(word, verboseFlag) #those are just for printing to the log

            wordSC = self.computeSoftCounts(word, verboseFlag)
            wordISC = self.computeInitialSoftCounts(word, verboseFlag)

            self.softCounts = mergeDicts(wordSC, self.softCounts)
            self.initialSoftCounts = mergeDicts(wordISC, self.initialSoftCounts)

        if verboseFlag:
            log = self.showSoftCounts()
            self.out.write(log)


if __name__ == "__main__":  
    
    model = HMM(corpus=["babi#", "dida#"], out_path="sample_log.txt")
    model.setCorpusSoftCounts(verboseFlag=True)