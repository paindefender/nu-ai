# Documentation
#
# Main functions(methods)
#	maze = ContentMaze(N, K, k, p) to initialize a maze
# 	maze.construct() to construct the graph
# 	maze.populate(Walls, Pits, Gold, Monsters, Wind Decay, Smell Decay) to populate the maze
# 	maze.info(cell) to print info about one cell
#
# Additional methods
#	maze.graphvizify() to get a graph representation compatible with http://graphs.grevian.org
# 	maze.print_maze() to print the info about all cells
#	maze.propagate(Cell, Decay, Property) to propagate a certain property through the graph
#
# Additional Assignment 3 functions
#   maze = ClockedContentMaze(N, K, k, p, tau=0.1) to create a maze with a clock
#   maze.tick() to start one tick

from random import randint
import math

class Maze(object):
    def __init__(self, N, K, k, p):
        self.graph = [[] for x in range(0, N)]
        self.N = N
        self.K = K
        self.k = k
        self.p = p
    
    def construct(self):
        # Number of edges test
        if (self.K * self.k + ((self.N - self.K) * self.p)) % 2 == 1:
            raise ValueError("Error: Number of edges is not an integer!")
        
        # Create list of remaining weights
        r_weights = [self.k] * self.K + [self.p] * (self.N - self.K)
        
        # Validity of using the node for connection
        node_validity = [x != 0 for x in r_weights]
        
        while any(node_validity):
            
            # Determine the minimum
            req_edges_min = max(self.k, self.p) + 1
            req_edges_min_i = -1
            
            for i in range(0, len(r_weights)):
                if (node_validity[i] and r_weights[i] < req_edges_min):
                    req_edges_min = r_weights[i]
                    req_edges_min_i = i 
            
            # Make minimum invalid
            node_validity[req_edges_min_i] = False
            
            # Make all nodes already connected to minimum invalid
            for i in range(0, len(self.graph[req_edges_min_i])):
                node_validity[self.graph[req_edges_min_i][i]] = False
            
            # Check if there are valid nodes available
            if not any(node_validity):
                raise ValueError("Error: Invalid Graph!")
            
            # Determine the maximum
            req_edges_max = req_edges_max_i = -1
            
            for i in range(0, len(r_weights)):
                if (node_validity[i] and r_weights[i] > req_edges_max):
                    req_edges_max = r_weights[i]
                    req_edges_max_i = i 
            
            # Decrease the required weight and connect the nodes
            r_weights[req_edges_max_i]-=1
            r_weights[req_edges_min_i]-=1
            self.graph[req_edges_max_i].append(req_edges_min_i)
            self.graph[req_edges_min_i].append(req_edges_max_i)
                
            node_validity = [x != 0 for x in r_weights]
    
    def info(self,cell):
        if len(self.graph[cell]) == 0: # happens when graph is not initialized, or when the construct ended in error(?)
            print("Node " + cell + "Has no neighbors")
        
        print("Neighbors of node " + str(cell) + ": "),
        for i in self.graph[cell]:
            print(str(i)),
        print(" ")
    
    def graphvizify(self): # for use with http://graphs.grevian.org
        s = "graph {\n"
        for i in range(0, self.N):
            for j in range(0, len(self.graph[i])):
                if i < self.graph[i][j]:
                    s += "\t" + str(i) + " -- " + str(self.graph[i][j]) + "\n"
        s += "}\n"
        return s

class ContentMaze(Maze):
    def __init__(self, N, K, k, p):
        self.contents = [None] * N
        self.properties = [{'wind': 0, 'smell': 0} for x in range(0, N)]
        super(ContentMaze, self).__init__(N, K, k, p)
    
    def propagate(self, cell, decay, prop, parent=-1):
        if self.contents[cell] == 'Wall':
            return
        if parent != -1:
            if self.properties[cell][prop] >= parent*decay:
                return
            else:
                self.properties[cell][prop] = parent*decay
        for i in self.graph[cell]:
                self.propagate(i, decay, prop, parent=self.properties[cell][prop])
    
    def populate(self, W, P, G, M, w_decay, s_decay): # Walls, Pits, Gold, Monsters, Wind Decay, Smell Decay
        if W + P + G + M > self.N:
            raise ValueError("Not enough nodes to populate!")
        if w_decay > 1 or w_decay < 0 or s_decay > 1 or s_decay < 0:
            raise ValueError("Decay should be a real number between 0 and 1") 
        
        available = [x for x in range(0, self.N)] 
        
        for i in range(0, W):
            index = randint(0, len(available)-1)
            self.contents[available[index]] = 'Wall'
            del available[index]
        for i in range(0, P):
            index = randint(0, len(available)-1)
            self.contents[available[index]] = 'Pit'
            self.properties[available[index]]['wind'] = 1
            self.propagate(available[index], w_decay, 'wind')
            del available[index]
        for i in range(0, G):
            index = randint(0, len(available)-1)
            self.contents[available[index]] = 'Gold'
            del available[index]
        for i in range(0, M):
            index = randint(0, len(available)-1)
            self.contents[available[index]] = 'Monster'
            self.properties[available[index]]['smell'] = 1
            self.propagate(available[index], s_decay, 'smell')
            del available[index]
    
    def info(self, cell):
        print(str(cell) + ' ' + str(self.contents[cell]) + ', wind: ' + str(self.properties[cell]['wind']) + ', smell: ' + str(self.properties[cell]['smell']) + ' ->'),
        for j in range(0, len(self.graph[cell])):
            print(' ' + str(self.graph[cell][j])),
        print('')
    
    def print_maze(self):
        for i in range(0, self.N):
            self.info(i)

class ClockedContentMaze(ContentMaze):
    def __init__(self, N, K, k, p, tau = 0.1):
        self.clock = 0
        self.wind = [0]*N
        self.smell = [0]*N
        self.monster_smell_history = [0]*N # Smell that monsters leave after themselves
        self.monster = [0]*N # How much monsters in each node
        self.monster_wait = [0]*N # How long each monster is waiting
        self.tau = tau # smell temporal constraint
        super(ClockedContentMaze, self).__init__(N, K, k, p)
    
    def populate(self, W, P, G, M, w_decay, s_decay):
        super(ClockedContentMaze, self).populate(W, P, G, M, w_decay, s_decay)
        self.s_decay = s_decay
        for i in range(0, self.N):
            self.wind[i] = self.properties[i]['wind']
            self.smell[i] = self.properties[i]['smell']
            self.monster = [0]*self.N
            for i in range(0, self.N):
                if self.contents[i] == 'Monster':
                    self.monster[i] = 1
    
    def tick(self):
        print(self.monster_wait)
        # Recalculate wind
        for i in range(0, self.N):
            self.wind[i] = self.properties[i]['wind'] * abs(math.cos(math.pi/180 * self.clock))
        
        #TODO: Move Monsters
        monster_temp = [x for x in self.monster]
        double = [False] * self.N # Double source smell or not
        for i in range(0, self.N):
            best_node = {'node':0, 'priority':-1}
            if self.monster[i] > 0:
                #Get neighbors
                for j in self.graph[i]:
                    # Higher priority is better
                    # priority 0 - monster feels smell and smell is higher than the wind (Wait 15)
                    # priority 1 - monster cannot smell any smell (Wait 3)
                    # priority 2 - monster feels smell and smell is lower than wind (Go immediately)
                    
                    if self.smell[j] > 0.6:
                        # priorities 0 and 2
                        if self.smell[j] < self.wind[j]:
                            # priority 2
                            if best_node['priority'] < 2:
                                best_node['node'] = j
                                best_node['priority'] = 2
                        else:
                            # priority 0
                            if self.monster_wait[i] >= 15:
                                if best_node['priority'] < 0:
                                    best_node['node'] = j
                                    best_node['priority'] = 0
                    else: 
                        # priority 1
                        if self.monster_wait[i] >= 3:
                            if best_node['priority'] < 1:
                                best_node['node'] = j
                                best_node['priority'] = 1
                # Destination determined
                if best_node['priority'] >= 0:
                    self.monster_wait[i] = 0
                    # Move the monster(s)
                    if self.contents[best_node['node']] == 'Wall': # Wall or Pit encountered
                        double[i] = True
                    elif self.contents[best_node['node']] == 'Pit':
                        self.monster_smell_history = [0] * self.N
                    else: # Not (Wall or Pit)
                        print("Moving " + str(i) + " to " + str(best_node['node']))
                        monster_temp[i] -= self.monster[i]
                        monster_temp[best_node['node']] += self.monster[i]
                        self.monster_smell_history[i] = 1
                else:
                    self.monster_wait[i] += 1
        self.monster = [x for x in monster_temp]
        # Propagate smell with new monster coordinates
        self.smell = [0]*self.N
        for i in range(0, self.N):
            if self.monster[i] > 0:
                self.smell[i] = (2 if double[i] else 1)
                self.propagate_smell(i, self.s_decay)
        for i in range(0, self.N):
            if self.smell[i] > self.monster_smell_history[i]:
                self.monster_smell_history[i] = self.smell[i]
        # Reduce the aftersmell / Merge aftersmell with smell
        for i in range(0, self.N):
            if self.smell[i] < self.monster_smell_history[i]:
                self.monster_smell_history[i] -= self.tau
            if self.smell[i] < self.monster_smell_history[i]:
                self.smell[i] = self.monster_smell_history[i]
        
        self.clock += 1
    
    def propagate_smell(self, cell, decay, parent=-1):
        if self.contents[cell] == 'Wall':
            return
        if parent != -1:
            if self.smell[cell] >= parent*decay:
                return
            else:
                self.smell[cell] = parent*decay
        for i in self.graph[cell]:
                self.propagate_smell(i, decay, parent=self.smell[cell])
    
    def info(self, cell):
        print(str(cell) + ' ' + ('None' if self.contents[cell] == 'Monster' else str(self.contents[cell])) + ((' ' + str(self.monster[cell]) + ' monster(s)') if self.monster[cell]>0 else '') + ' wind: ' + str(self.wind[cell]) + ', smell: ' + str(self.smell[cell]) + ' ->'),
        for j in range(0, len(self.graph[cell])):
            print(' ' + str(self.graph[cell][j])),
        print('')

# Example
a = ClockedContentMaze(4, 3, 2, 2, tau=0.05)
a.construct()
a.populate(1,1,1,1,0.3,0.8)

for i in range(0,20):
    a.print_maze()
    a.tick()
