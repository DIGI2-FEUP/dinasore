import numpy as np
import time
import paho.mqtt.client as mqtt
import random
import pandas as pd
import operator

class City:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def distance(self, city):
        xDis = abs(self.x - city.x)
        yDis = abs(self.y - city.y)
        distance = np.sqrt((xDis ** 2) + (yDis ** 2))
        return distance

    def __repr__(self):
        return "(" + str(self.x) + "," + str(self.y) + ")"

class Fitness:
    def __init__(self, route):
        self.route = route
        self.distance = 0
        self.fitness = 0.0

    def routeDistance(self):
        if self.distance == 0:
            pathDistance = 0
            for i in range(0, len(self.route)):
                fromCity = self.route[i]
                toCity = None
                if i + 1 < len(self.route):
                    toCity = self.route[i + 1]
                else:
                    toCity = self.route[0]
                pathDistance += fromCity.distance(toCity)
            self.distance = pathDistance
        return self.distance

    def routeFitness(self):
        if self.fitness == 0:
            self.fitness = 1 / float(self.routeDistance())
        return self.fitness


class OPTIMIZER:

    def createRoute(self, cityList):
        route = random.sample(cityList, len(cityList))
        return route

    def initialPopulation(self, popSize, cityList):
        population = []

        for i in range(0, popSize):
            population.append(self.createRoute(cityList))
        return population

    def selection(self, popRanked, eliteSize):
        selectionResults = []
        df = pd.DataFrame(np.array(popRanked), columns=["Index", "Fitness"])
        df['cum_sum'] = df.Fitness.cumsum()
        df['cum_perc'] = 100 * df.cum_sum / df.Fitness.sum()

        for i in range(0, eliteSize):
            selectionResults.append(popRanked[i][0])
        for i in range(0, len(popRanked) - eliteSize):
            pick = 100 * random.random()
            for i in range(0, len(popRanked)):
                if pick <= df.iat[i, 3]:
                    selectionResults.append(popRanked[i][0])
                    break
        return selectionResults

    def matingPool(self, population, selectionResults):
        matingpool = []
        for i in range(0, len(selectionResults)):
            index = selectionResults[i]
            matingpool.append(population[index])
        return matingpool

    def breed(self, parent1, parent2):
        child = []
        childP1 = []
        childP2 = []

        geneA = int(random.random() * len(parent1))
        geneB = int(random.random() * len(parent1))

        startGene = min(geneA, geneB)
        endGene = max(geneA, geneB)

        for i in range(startGene, endGene):
            childP1.append(parent1[i])

        childP2 = [item for item in parent2 if item not in childP1]

        child = childP1 + childP2
        return child

    def breedPopulation(self, matingpool, eliteSize):
        children = []
        length = len(matingpool) - eliteSize
        pool = random.sample(matingpool, len(matingpool))

        for i in range(0, eliteSize):
            children.append(matingpool[i])

        i = 0
        while i < length:
            child = self.breed(pool[i], pool[len(matingpool) - i - 1])
            if child not in children:
                children.append(child)
                i +=1

        return children

    def mutate(self, individual, mutationRate):
        for swapped in range(len(individual)):
            if (random.random() < mutationRate):
                swapWith = int(random.random() * len(individual))

                city1 = individual[swapped]
                city2 = individual[swapWith]

                individual[swapped] = city2
                individual[swapWith] = city1
        return individual

    def mutatePopulation(self, population, mutationRate):
        mutatedPop = []

        for ind in range(0, len(population)):
            mutatedInd = self.mutate(population[ind], mutationRate)
            mutatedPop.append(mutatedInd)
        return mutatedPop

    def nextGeneration(self, results, currentGen, eliteSize, mutationRate):
        #popRanked = rankRoutes(currentGen)
        popRanked = sorted(results.items(), key=operator.itemgetter(1), reverse=True)
        selectionResults = self.selection(popRanked, eliteSize)
        matingpool = self.matingPool(currentGen, selectionResults)
        print("matingpool: " , len(matingpool))
        children = self.breedPopulation(matingpool, eliteSize)
        print("children: ", len(children))
        nextGeneration = self.mutatePopulation(children, mutationRate)
        return nextGeneration

    def schedule(self, event_name, event_value, target, result, param, init_pop, pop_size, elite_size, mutation, n_generations):

        if event_name == 'INIT':

            self.results = {} #fitness function
            self.params = [] #Population
            self.generation_counter = 0
            self.indexes = []

            return [None, None, None,
                    None, None]

        if event_name == 'RUN': # initial execution

            # GA Parameter to execute
            self.target = target
            self.init_pop = eval(init_pop)
            self.pop_size = int(pop_size)
            self.elite_size = int(elite_size)
            self.mutation = float(mutation)
            self.n_generations = int(n_generations)

            pop = self.initialPopulation(self.pop_size, self.init_pop)

            self.params = pop

            return [None, event_value, None,
                    str(self.params), None]

        if event_name == 'RESULT_I':

            #print("OPTIMIZER: received param:" , param, "all params:" , self.params)
            print("OPTIMIZER: received param:" , param)

            self.results[self.params.index(param)] = result

            self.indexes.append(self.params.index(param))
            print("OPTIMIZER: " , self.indexes , param)

            print("OPTIMIZER: len(self.results): " , len(self.results) , "len(self.params):" , len(self.params))

            if len(self.results) == len(self.params): # reached the end of a generations

                if self.generation_counter == self.n_generations:  # end of algorithm execution

                    popRanked = sorted(self.results.items(), key=operator.itemgetter(1), reverse=True)
                    bestRouteIndex = popRanked[0][0]
                    bestRoute = self.params[bestRouteIndex]

                    cityList = []
                    for i in range(0, len(bestRoute)):
                        cityList.append(City(bestRoute[i][0], bestRoute[i][1]))

                    print("Final distance: " + str(1 / Fitness(cityList).routeFitness()))

                    return [None, None, event_value,
                            None, bestRoute]
                else:

                    # sort results
                    nextPop = self.nextGeneration(self.results, self.params, self.elite_size, self.mutation)

                    self.results = {}
                    self.params = nextPop
                    self.generation_counter += 1

                    return [None, event_value, None,
                            str(self.params), None]

            else: #wait for more results
                return [None, None, None,
                        None, None]