import os
import random
from os import system

# NOTE: This version of our Program will only work with the orignial game rules and settings. This means that the slot numeber WILL ALWAYS be equal to 4 and SHOULD NOT be changed.
#       The Number of colors that can be play with are ranged from 2 - 10.


MAX_POP_SIZE = 60                           # MAX number of valid candidates generated before Genetic evolution stops
MAX_GENERATIONS = 100                       # MAX number of generations to create children before evolution stops
CROSSOVER_PROBABILITY = 0.7                 # if random.random() returns > 0.7 , we will do a crossover on two parents
CROSSOVER_THEN_MUTATION_PROBABILITY = 0.03  # if random.random() returns < 0.03 , we will do a crossover on two parents and then mutate the child
PERMUTATION_PROBABILITY = 0.03              # if random.random() returns > 0.03 , we will do a permutation of the parent code
SLOTS = 4                                   # Number of "Colors" in the code [1,2,3,4] by default 
random.seed(os.urandom(32))                 # create a seed so our "random results" are more consistent between plays

class Mastermind():
    def __init__(self):
        self.printMastermindLogo()

        self.Colors = []        # Create an Empty List of Potential "Colors" which will be represented by integers (ex 1-6)
        self.turn = 0           # initialize turn to 0 at the start of a new game
        self.currentGuess = []  # create an initial code for the genetic mutation to begin working with 
        self.guesses = []       # a list of attempted guesses and their respective result stored in tuple (guess,result)
        self.newGeneration = [] # a list of the new generation of guesses

    def printMastermindLogo(self):
        system('cls')
        print("\n __  __           _                      _           _ ")
        print("|  \/  |         | |                    (_)         | |")
        print("| \  / | __ _ ___| |_ ___ _ __ _ __ ___  _ _ __   __| |")
        print("| |\/| |/ _` / __| __/ _ \ '__| '_ ` _ \| | '_ \ / _` |")
        print("| |  | | (_| \__ \ ||  __/ |  | | | | | | | | | | (_| |")
        print("|_|  |_|\__,_|___/\__\___|_|  |_| |_| |_|_|_| |_|\__,_|\n\n")                                 
    
    def manualPlay(self):
        
        # manualPlay is for allowing a human to play agaist the computer.
        # It asks the user what are the results of each guess the computer makese. 
        # It Then returns the users input as a tuple.
        
              
        self.turn += 1

        print()
        print("Round #" , self.turn)
        print("The computer has guessed: ", self.currentGuess)
        correctColorLocation = int(input("Enter the number of correct COLORS and locations: "))
        correctColor = int(input("Enter the number of correct COLORS that are not in the right locations: "))
        while correctColorLocation > SLOTS or correctColor > SLOTS:
            print("\n\nIncorrect Input:")
            correctColorLocation = int(input("Please enter a number between: (0-" + str(SLOTS) + '): '))
            correctColor = int(input("Please enter a number between: (0-"+ str(SLOTS) +'): '))
        print()
        
        result = (int(correctColorLocation), int(correctColor))

        self.guesses.append((self.currentGuess, result))

        return result
    
    def checkPlay(self, aiChoice, rightChoice):
    
        # checkPlay creates a tuple score for the aiChoice compared to the rightChoice
        # It then returns the score as a tuple.
        
        
        assert len(aiChoice) == len(rightChoice)


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
                for i, c in enumerate(copyRightChoice):
                    if c == code:
                        copyRightChoice[i] = -3

        return (placeTrue,placeFalse)

    def getDifference(self, trial, guess):
        # getDifference() is a function used mainly in our 100TestMastermind. It is a method
        # of finding the number of white pegs (in the correct slots and correct color), and black pegs 
        # (correct color but not in the right slot) for randomly-generated code variants of the game
        # This function is not used in the user-Feedback version of the game, because the difference is
        # the feedback the user provides ex (1,3) (4,0) etc: 
        guessResult = guess[1] 
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
        # We score every individual child using the fitnessScore function,
        # this score is what is calculated in the population score and determines
        # which child is considered the "best candidate"
        differences = []
        for guess in guesses:
            differences.append(self.getDifference(trial, guess))

        locationDifferences = 0
        colorDifferences = 0

        for dif in differences:
            locationDifferences += dif[0]
            colorDifferences += dif[1]

        score = locationDifferences + colorDifferences
        return score

    def crossover(self, code1, code2):
        
        # crossover takes the parents (code1 and code2) and crosses their genetics with eachother 
        # if the random.random() generates a value greater than the current CROSSOVER_PROBABILITY it will pull a gene
        # from code1, else it will pull from code2. This will be done SLOTS times, which will then return the newcode.
        
        newcode = []
        for i in range(SLOTS):
            if random.random() > CROSSOVER_PROBABILITY:
                newcode.append(code1[i])
            else:
                newcode.append(code2[i])
                
        return newcode

    def mutate(self, code, allAvailableNumbers):
        
        # mutate takes a code and all the allAvailableNumbers.
        # it will then select a random spot in the code and 
        # replace it with a random number from the allAvailableNumbers list.
        # Tt will then return the modified code.
        
        i = random.randint(0, SLOTS-1)
        v = random.choice(allAvailableNumbers)
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

    def geneticEvolution(self, popSize, generations):
        
        
        # We generate the first population of chromosomes, in a randomized way
        # in order to reduce probability of duplicates
        # we create a new list to hold our children called "sons" who will inherit from the parent codes
        # generation using a natural selection strategy that is randomly selected.
        
        
        # Generate a list of Number we know are not correct
        badNumbers = []
        for guess in self.guesses:
            if guess[1] == (0,0):
                badNumbers.append(guess[0][0])
                badNumbers.append(guess[0][1])
                badNumbers.append(guess[0][2])
                badNumbers.append(guess[0][3])

        allAvailableNumbers = self.Colors
        
        # Remove all the known bad numbers from the possible generation list
        for num in badNumbers:
            if num in allAvailableNumbers:
                allAvailableNumbers.remove(num)

        if round == 1 and self.guesses[0][1] == (0,4):
            population = [[random.randint(self.guesses[0][0][0],self.guesses[0][0][1],self.guesses[0][0][2],self.guesses[0][0][3]) for _ in range(SLOTS)]\
                                   for _ in range(popSize)]
        else:
            population = [[random.choice(allAvailableNumbers) for _ in range(SLOTS)]\
                                   for _ in range(popSize)]

        chosenOnes = []
        h = 1
        k = 0
        while len(chosenOnes) <= popSize and h <= generations:
                sons = []

                for i in range(len(population)):
                        if i == len(population) - 1:
                            sons.append(population[i])
                            break

                        # Apply cross over
                        son = self.crossover(population[i], population[i+1])

                        # Apply mutation after cross over if random.random() returns a value < .03
                        if random.random() <= CROSSOVER_THEN_MUTATION_PROBABILITY:
                                son = self.mutate(son, allAvailableNumbers)

                        # Apply permutation individually from any parameter requirements
                        son = self.permute(son)

                        # Add the genetically modified son to the population
                        sons.append(son)

                # We link each son to a fitness score.
                popScore = []
                for son in sons:
                    popScore.append((self.fitnessScore(son, self.currentGuess, self.guesses), son))

                # We re-order our sons population based on fitness score
                popScore = sorted(popScore, key=lambda x: x[0])

                # we create our eligibles list by iterating through our popScore list and appending eligible children that have scores = 0
                # these are eligible codes that can produce results that are considered "better" than our previous (parent) guess. Though the overall
                # scoring method we use to grade the children is a Maximum score in our FitnessScore(): this example uses a minimum score to compare how well each child
                # compares to its parents results. 
                eligibles = [(score, e) for (score, e) in popScore if score == 0]

                if len(eligibles) == 0:
                    h = h + 1
                    continue

                newEligibles = []
                for (_, c) in eligibles:
                    newEligibles.append(c)
                eligibles = newEligibles

                for code in eligibles:
                    if code in chosenOnes:
                        chosenOnes.remove(code)
                        chosenOnes.append([random.choice(allAvailableNumbers) for _ in range(SLOTS)])


                # Iiterate through eligible children
                for eligible in eligibles:
                    # Make sure we don't overflow our MAX_POP_SIZE
                    if len(chosenOnes) == popSize:
                        break

                    if not eligible in chosenOnes:
                        chosenOnes.append(eligible)

                # Extends eligibiles for population
                population = []
                population.extend(eligibles)

                # We fill the rest of the population with random codes up to popSize
                j = len(eligibles)
                while j < popSize:
                    population.append([random.randint(1, len(self.Colors)) for _ in range(SLOTS)])
                    j = j + 1

                h = h + 1
        # We assign the list of "chosenOnes" as the newGeneration member variable of the mastermind class
        mastermindGame.newGeneration = chosenOnes
                
        return chosenOnes

    def updateCurrentGuess(self):
        self.currentGuess = self.newGeneration.pop()

    def removeDuplicates(self):
        while self.currentGuess in [c for (c, _) in self.guesses]:
            self.updateCurrentGuess()    
    
    def lenColors(self):
            
            inp = int(input("How many COLORS would you like to play with? (2-10): "))
                
            while inp < 2 or inp > 10:
                 inp = int(input("\nPlease re-enter the number of COLORS you like to play with, and make sure the value is between 2 and 10: "))

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
            
            self.currentGuess = firstGuess

    def endGame(self):      
        print("The computer has cracked your code!")
        print("\nYour code was ",self.currentGuess)

        return input("\nWould you like to play again? (Y/N): ")
        
                                                       
if __name__ == '__main__':
    play = 'Y'
    while (play == 'Y' or play == 'y' or play == 'Yes' or play == 'yes'):
        mastermindGame = Mastermind()
        mastermindGame.lenColors()
        
        random.seed(os.urandom(32))

        result = mastermindGame.manualPlay()

        while result != (SLOTS,0):
            mastermindGame.geneticEvolution(MAX_POP_SIZE, MAX_GENERATIONS)

            while len(mastermindGame.newGeneration) == 0:
                print('Computer Thinking 🤔' )
                # This print statement simply means that a valid candidate was not found, so we will modify some of
                # our parameters and attempt more rigorously generate children
                mastermindGame.geneticEvolution(MAX_POP_SIZE*2, MAX_GENERATIONS/2)
        
            mastermindGame.updateCurrentGuess()

            mastermindGame.removeDuplicates()

            result = mastermindGame.manualPlay()
            
        play = mastermindGame.endGame()
    
    print("\n _____                           ____                 ")
    print("/ ____|                         / __ \                ")
    print("| |  __  __ _ _ __ ___   ___   | |  | |_   _____ _ __ ") 
    print("| | |_ |/ _` | '_ ` _ \ / _ \  | |  | \ \ / / _ \ '__|") 
    print("| |__| | (_| | | | | | |  __/  | |__| |\ V /  __/ |   ") 
    print("\______|\__,_|_| |_| |_|\___|   \____/  \_/ \___|_|   ")
    print("\nThank you for playing!")