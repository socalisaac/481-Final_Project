import os
import random
import sys

from game import *
from genetic import *
from variables import *

MAX_POP_SIZE = 60
MAX_GENERATIONS = 100

CROSSOVER_PROBABILITY = 0.7
CROSSOVER_THEN_MUTATION_PROBABILITY = 0.03
PERMUTATION_PROBABILITY = 0.03
INVERSION_PROBABILITY = 0.02

ELITE_RATIO=  .4

SLOTS = 4 # Number of "Colors" in the code [1,2,3,4] by default
random.seed(os.urandom(32))  # create a seed so our "random results" are more consistent between plays

class Mastermind(game):
    def __init__(self):
        print("create mastermind game")
        self.Colors = []    # Create an Empty List of Potential "Colors" which will be represented by integers (ex 1-6)
        self.turn = 0       # initialize turn to 0 at the start of a new game
        self.currentGuess = []  # create an initial code for the genetic mutation to begin working with 
        self.guesses = []   # a list of attempted guesses and their respective result stored in tuple (guess,result)
        self.newGeneration = []
    
    def manualPlay(self):
        self.turn += 1

        print()
        print("The Current Round is: " , self.turn)
        print("The computer has guessed: ", self.currentGuess)
        correctColorLocation = input("Please enter the number of correct color and location: ")
        correctColor = input("Please enter the number of correct numbr of colors not in the right location: ")
        print()

        result = (int(correctColorLocation), int(correctColor))

        self.guesses.append((self.currentGuess, result))

        return result
    
    def checkPlay(self, aiChoice, rightChoice):
        '''
        Returns number of good placements and bad placements from aiChoice
        compared to rightChoice
        Assert aiChoice and rightChoice with same length
        '''
        assert len(aiChoice) == len(rightChoice)

        # local copy of color to guess as reference of already calculated colors

        copyRightChoice = []
        for code in rightChoice:
            copyRightChoice.append(code)

        copyaiChoice = []
        for code in aiChoice:
            copyaiChoice.append(code)

        placeTrue = 0
        placeFalse = 0

        for i in range(len(rightChoice)):
            if rightChoice[i] == aiChoice[i]:
                placeTrue = placeTrue + 1
                copyRightChoice[i] = -1
                copyaiChoice[i] = -2

        for code in copyaiChoice:
            if code in copyRightChoice:
                placeFalse = placeFalse + 1
                for i,c in enumerate(copyRightChoice):
                    if c == code:
                        copyRightChoice[i] = -3

        return (placeTrue,placeFalse)

    def getDifference(self, trial, guess):
        # The result AI guess obtained
        guessResult = guess[1]

        # The ai guess code
        guessCode = guess[0]

        # We assume `guess` is the color to guess
        # we then establish the score our `trial` color would obtain

        trialResult = self.checkPlay(trial, guessCode)

        # We get the difference between the scores
        dif = [0,0]
        for i in range(2):
            dif[i] = abs(trialResult[i] - guessResult[i])

        return tuple(dif)

    def fitnessScore(self, trial, code, guesses):
        # Given a list of guesses (picked from elite generations),
        # we build a list of difference score comparing our trial to
        # each guess
        differences = []
        for guess in guesses:
            differences.append(self.getDifference(trial, guess))

        # Sum of well placed colors
        sumBlackPinDifferences = 0
        # Sum of wrong placed colors
        sumWhitePinDifferences = 0

        for dif in differences:
            sumBlackPinDifferences += dif[0]
            sumWhitePinDifferences += dif[1]

        # Final score
        score = sumBlackPinDifferences + sumWhitePinDifferences
        return score

    def crossover(self, code1, code2):
        newcode = []
        for i in range(SLOTS):
            if random.random() > CROSSOVER_PROBABILITY:
                newcode.append(code1[i])
            else:
                newcode.append(code2[i])
        return newcode

    def mutate(self, code, allAvailableNumbers):
        i = random.randint(0, SLOTS-1)
        v = random.choice(allAvailableNumbers)
        # v = random.randint(1, len(self.Colors))
        code[i] = v
        return code

    def permute(self, code):
        for i in range(SLOTS):
            if random.random() <= PERMUTATION_PROBABILITY:
                firstRandomPosition = random.randint(0, SLOTS-1)
                secondRandomPosition = random.randint(0, SLOTS-1)

                saveFirstPositionValue = code[firstRandomPosition]

                code[firstRandomPosition] = code[secondRandomPosition]
                code[secondRandomPosition] = saveFirstPositionValue

        return code

    def geneticEvolution(self, popSize, generations, eliteRatio=ELITE_RATIO):
        '''
        Function implementing the genetic algorithm to guess the right color code
        for MasterMind game

        We generate several populations of guesses using natural selection strategies
        like crossover, mutation and permutation.

        In this function, we assume our color code to guess as a chromosome.
        The populations we generate are assimilated to sets of chromosomes for
        which the nitrogenous bases are our color code

        popSize: the maximum size of a population
        generations: maxumum number of population generations
        costfitness: function returning the fitness score of a chromosome (color code)
        '''

        # We generate the first population of chromosomes, in a randomized way
        # in order to reduce probability of duplicates
        badNumbers = []
        for guess in self.guesses:
            if guess[1] == (0,0):
               
                badNumbers.append(guess[0][0])
                badNumbers.append(guess[0][1])
                badNumbers.append(guess[0][2])
                badNumbers.append(guess[0][3])

        allAvailableNumbers = self.Colors

        for num in badNumbers:
            if num in allAvailableNumbers:
                allAvailableNumbers.remove(num)

        if round == 1 and self.guesses[0][1] == (0,4):
            population = [[random.randint(self.guesses[0][0][0],self.guesses[0][0][1],self.guesses[0][0][2],self.guesses[0][0][3]) for i in range(SLOTS)]\
                                   for j in range(popSize)]
        else:

            population = [[random.choice(allAvailableNumbers) for i in range(SLOTS)]\
                                   for j in range(popSize)]

            # population = [[random.randint(1, len(self.Colors)) for i in range(SLOTS)]\
            #                        for j in range(popSize)]


        # population = [[random.randint(1, len(self.Colors)) for i in range(SLOTS)]\
        #                            for j in range(popSize)]


        # Set of our favorite choices for the next play (Elite Group Ei)
        chosenOnes = []
        h = 1
        k = 0
        while len(chosenOnes) <= popSize and h <= generations:

                # Prepare the population of sons who will inherit from the parent
                # generation using a natural selection strategy
                sons = []

                for i in range(len(population)):

                        # If we find two parents for the son, we pick the son
                        if i == len(population) - 1:
                            sons.append(population[i])
                            break

                        # Apply cross over

                        # print(population[i], " ", population[i+1])

                        son = self.crossover(population[i], population[i+1])

                        # print(son)

                        # Apply mutation after cross over
                        if random.random() <= CROSSOVER_THEN_MUTATION_PROBABILITY:
                                son = self.mutate(son, allAvailableNumbers)

                        # Apply mutation
                        son = self.permute(son)

                        # Add the son to the population
                        sons.append(son)

                # We link each son to a fitness score. The closest the score to
                # Zero, the better chance our code is the right guess
                popScore = []
                for son in sons:
                    # popScore.append((costfitness(son), son))
                    popScore.append((self.fitnessScore(son, self.currentGuess, self.guesses), son))

                # We order our sons population based on fitness score (increasing)
                popScore = sorted(popScore, key=lambda x: x[0])

                # We use the eliteRation parameter to choose an elite of chosen
                # codes among the choices, imitating natural selection process
                # NOTE: elite ratio is not currently used

                # First we pick an eligible elite (Score is Zero)
                eligibles = [(score, e) for (score, e) in popScore if score == 0]

                if len(eligibles) == 0:
                    h = h + 1
                    continue

                # Pick out the code from our eligible elite (score, choice) tuples
                newEligibles = []
                for (score, c) in eligibles:
                    newEligibles.append(c)
                eligibles = newEligibles

                # We remove the eligible codes already included in the elite choices (Ei)

                for code in eligibles:
                    if code in chosenOnes:
                        chosenOnes.remove(code)

                        # We replace the removed duplicate elite code with a random one
                        chosenOnes.append([random.choice(allAvailableNumbers) for i in range(SLOTS)])
                        # chosenOnes.append([random.randint(1, len(self.Colors)) for i in range(SLOTS)])

                # We add the eligible elite to the elite set (Ei)
                for eligible in eligibles:
                    # Make sure we don't overflow our elite size (Ei <= popSize)
                    if len(chosenOnes) == popSize:
                        break

                    # If the eligible elite code is not already chosen, promote it
                    # to the elite set (Ei)
                    if not eligible in chosenOnes:
                        chosenOnes.append(eligible)

                # Prepare the parent population for the next generation based
                # on the current generation
                population=[]
                population.extend(eligibles)


                # We fill the rest of the population with random codes up to popSize
                j = len(eligibles)
                while j < popSize:
                    population.append([random.randint(1, len(self.Colors)) for i in range(SLOTS)])
                    j = j + 1

                # For each generation, we become more aggressive in choosing
                # the best eligible codes. We become more selective
                if not eliteRatio < 0.01:
                    eliteRatio -= 0.01

                h = h + 1

        # print(len(chosenOnes))

        mastermindGame.newGeneration = chosenOnes
                
        return chosenOnes

    def updateCurrentGuess(self):
        self.currentGuess = self.newGeneration.pop()

    def removeDuplicates(self):
        while self.currentGuess in [c for (c, r) in self.guesses]:
            # print('DUPLICAAAAAAAAAATE')
            # code = eligibles.pop()
            self.updateCurrentGuess()    
    
    def lenColors(self):
            if len(self.Colors) == 0:
                inp = input("How many Colors would you like to play with? (0-10): ")
                self.Colors.extend(range(1, int(inp) + 1))
                self.getFirstGuess()

    def getFirstGuess(self):
            i = random.randint(1,len(self.Colors))
            x = random.randint(1,len(self.Colors))

            while i == x:
                x = random.randint(1,len(self.Colors))

            iCounter = 0
            xCounter = 0
            firstGuess = []
            choices = [i,x]
            while iCounter + xCounter < SLOTS:
                
                value = random.choice(choices)
                if value == i and iCounter < SLOTS / 2:
                    iCounter += 1
                    firstGuess.append(i)
                elif value == x and xCounter < SLOTS / 2:
                    xCounter += 1
                    firstGuess.append(x)
            
            # if SLOTS % 2 == 1:
            #     firstGuess.append(random.choice(choices))

            self.currentGuess = firstGuess    

if __name__ == '__main__':
    mastermindGame = Mastermind()
    mastermindGame.lenColors()
    
    random.seed(os.urandom(32))

    # def scoref(trial):
    #         return fitnessScore(trial, code, guesses, SLOTS=4)

    # result=play(code, turn, TOGUESS)
    result = mastermindGame.manualPlay()

    while result != (SLOTS,0):
        # print("HERERE")
        # eligibles = geneticEvolution(MAX_POP_SIZE, MAX_GENERATIONS, scoref, SLOTS=4)
        mastermindGame.geneticEvolution(MAX_POP_SIZE, MAX_GENERATIONS)
        # print('Ei', len(eligibles))

        while len(mastermindGame.newGeneration) == 0:
            print('is 0')
        
            mastermindGame.geneticEvolution(MAX_POP_SIZE*2, MAX_GENERATIONS/2)
    
        mastermindGame.updateCurrentGuess()

        mastermindGame.removeDuplicates()

        result=mastermindGame.manualPlay()

        if result == (SLOTS,0):
            print('WIIIIIIN')
            print(mastermindGame.currentGuess, result)