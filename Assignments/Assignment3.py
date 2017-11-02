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
    
    # Propagate wind and smell from cell
    def propagate(self, cell, decay, prop, parent=-1):
#         print('going to ' + str(cell) + ". parent is " + str(parent))
        if self.contents[cell] == 'Wall':
            return
        if parent != -1:
            if self.properties[cell][prop] >= parent*decay:
                return
            else:
#                 print(parent*decay)
                self.properties[cell][prop] = parent*decay
        for i in self.graph[cell]:
#                 print(self.properties[cell][prop])
                self.propagate(i, decay, prop, parent=self.properties[cell][prop])
    
    def populate(self, W, P, G, M, w_decay, s_decay):
        if W + P + G + M > self.N:
            raise ValueError("Not enough nodes to populate!")
            
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
        print(str(cell) + ' ' + str(self.contents[cell]) + ' wind: ' + str(self.properties[cell]['wind']) + ', smell: ' + str(self.properties[cell]['smell']) + ' ->'),
        for j in range(0, len(self.graph[cell])):
            print(' ' + str(self.graph[cell][j])),
        print('\n')
    
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
        
        self.wp_jump = [0] * self.N # Wall Pit Jump variables
        self.wp_jump_started = [False] * self.N
        self.wp_jump_node = [-1] * self.N
    
    def tick(self):
#         print(self.monster_wait)
        # Recalculate wind
        for i in range(0, self.N):
            self.wind[i] = self.properties[i]['wind'] * abs(math.cos(math.pi/180 * self.clock))
        
        #TODO: Move Monsters
        monster_temp = [x for x in self.monster]
        double = [False] * self.N # Double source smell or not
        for i in range(0, self.N):
            best_node = {'node':0, 'priority':-1}
            if self.monster[i] > 0:
                
                skip_t = False
                if self.wp_jump_started[i]:
                    # jump started
                    self.wp_jump[i] += 1
#                     print("Jump wait", self.wp_jump[i])
                    if self.wp_jump[i] >= 3:
                        self.monster_wait[i] = 0
                        self.wp_jump_started[i] = False
#                         print("Teleporting " + str(i) + " to " + str(self.wp_jump_node[i]))
                        monster_temp[i] -= self.monster[i]
                        monster_temp[self.wp_jump_node[i]] += self.monster[i]
                        self.monster_smell_history[i] = 1
                        skip_t = True        
                
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
                if best_node['priority'] >= 0 and not self.wp_jump_started[i] and not skip_t:
#                     print("Trying to move " + str(i) + " to " + str(best_node['node']))
                    self.monster_wait[i] = 0        
                    # Move the monster(s)
                    if self.contents[best_node['node']] == 'Wall': # Wall or Pit encountered
                        double[i] = True
                        if not self.wp_jump_started[i]:
                            jump_nodes = self.min_smell_nodes()
                            violations = [self.color(x)[0] for x in jump_nodes]
#                             print(violations)
                            v_bool = [x == 0 for x in violations]
                            self.wp_jump_started[i] = True
                            self.wp_jump[i] = 1
                            if any(v_bool):
                                for j in zip(v_bool, jump_nodes):
                                    if j[0]:
                                        self.wp_jump_node[i] = j[1]
                                        self.monster_smell_history[j[1]] = max(self.monster_smell_history[j[1]], self.smell[j[1]]) * 4 + self.tau
#                                         print("planning to jump to", self.wp_jump_node[i])
                                        break
                            else:
#                                 print("doing probabilistic stuff")
                                for i in range(0, len(violations)):
                                    violations[i] /= sum(violations)
                                    violations * randint(0, 10)
                                self.wp_jump_node[i] = violations.index(max(violations))
                                self.monster_smell_history[j[1]] = max(self.monster_smell_history[self.wp_jump_node[i]], self.smell[self.wp_jump_node[i]]) * 4 + self.tau
#                                 print("planning to jump to", self.wp_jump_node[i])
                                break
                        else:
                            skip_t = False
                    elif self.contents[best_node['node']] == 'Pit':
#                         self.monster_smell_history = [0] * self.N
                        if not self.wp_jump_started[i]:
                            jump_nodes = self.min_smell_nodes()
                            violations = [self.color(x)[0] for x in jump_nodes]
#                             print(violations)
                            v_bool = [x == 0 for x in violations]
                            if any(v_bool):
                                self.wp_jump_started[i] = True
                                self.wp_jump[i] = 1
                                for j in zip(v_bool, jump_nodes):
                                    if j[0]:
                                        self.wp_jump_node[i] = j[1]
                                        self.monster_smell_history[j[1]] = max(self.monster_smell_history[j[1]], self.smell[j[1]]) * 4 + self.tau
#                                         print("planning to jump to", self.wp_jump_node[i])
                                        break
                            else:
#                                 print("doing probabilistic stuff")
                                for i in range(0, len(violations)):
                                    violations[i] /= sum(violations)
                                    violations * randint(0, 10)
                                self.wp_jump_node[i] = violations.index(max(violations))
                                self.monster_smell_history[j[1]] = max(self.monster_smell_history[self.wp_jump_node[i]], self.smell[self.wp_jump_node[i]]) * 4 + self.tau
#                                 print("planning to jump to", self.wp_jump_node[i])
                                break
                        else:
                            skip_t = False
                    else: # Not (Wall or Pit)
#                         print("Moving " + str(i) + " to " + str(best_node['node']))
                        monster_temp[i] -= self.monster[i]
                        monster_temp[best_node['node']] += self.monster[i]
                        self.monster_smell_history[i] = 1
                else:
                    if not skip_t:
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
    
    def color(self, node, max_colors = 4): # Uses same approach as discussed in class, but without backtracking and inference
#         print("Graph is ", self.graph)
        colors = [-1] * self.N # Map of colors
        violations = 0
        to_color = set(self.graph[node]).union(set([node])) # set of nodes that we are supposed to color
#         print("Doing the color thing!")
        
        while True:
#             print(to_color, colors)
            # get set of minimum remaining values's
            mrvs = set()
            min_val = self.N
            for i in to_color:
                if colors[i] != -1:
                    continue
                p_set = set(range(0, max_colors)) # possible colors
                adj_cols = set([colors[x] for x in self.graph[i]])
                adj_cols.discard(-1)
                _val = len(p_set.difference(adj_cols))
                if (_val < min_val):
                    mrvs = set()
                    min_val = _val
                if (_val == min_val):
                    mrvs.add(i)
#             print("Minimum Remaining Values: ", mrvs)
            
            node_to_color = -1
            
            if len(mrvs) > 1:
                # pick using degree heuristic
                dh = set()
                max_degree = -1
                for i in mrvs:
                    degree_guy = len([x for x in self.graph[i] if x in to_color])
                    if degree_guy > max_degree:
                        dh = set()
                        max_degree = degree_guy
                    if degree_guy == max_degree:
                        dh.add(i)
#                 print("After degree heuristic", dh)
                node_to_color = dh.pop()
            else:
                node_to_color = mrvs.pop()
            
#             print("Coloring", node_to_color)
            
            # Finding least constraining value
            col_set = set(range(0, max_colors)) # possible colors
            adj_cols = set([colors[x] for x in self.graph[node_to_color]])
            adj_cols.discard(-1)
            col_set = col_set.difference(adj_cols)
#             print("Available colors", col_set)
    
            if len(col_set) == 0: # if no colors are allowed
                # Make a violation!
                violations += 1
                col_set = set(range(0, max_colors)) # Allow all colors
                
            max_choices = -1
            max_choices_color = -1
            for i in col_set:
                choices_sum = 0
                for j in self.graph[node_to_color]:
                    if j in to_color and colors[j] == -1:
                        p_set = set(range(0, max_colors))# possible colors for adjacent guys
                        p_set.discard(i)
                        adj_cols = set([colors[x] for x in self.graph[j]])
                        adj_cols.discard(-1)
                        adj_cols.discard(i)
#                         print(p_set.difference(adj_cols))
                        _val = len(p_set.difference(adj_cols))
                        choices_sum += _val
                if choices_sum > max_choices:
                    max_choices = choices_sum
                    max_choices_color = i
#             print("Color is", max_choices_color)
            
            colors[node_to_color] = max_choices_color
            
            left = [x for x in to_color if colors[x] == -1]
#             print("Left to color:",left)
            if len(left) < 1:
                break;
        return violations, colors
    
    def min_smell_nodes(self, n_nodes = 5): # n_nodes - max amount of returned nodes
        # Sort nodes based on smell
        sorted_nodes = [x for _,x in sorted(zip(self.smell, range(0, self.N)),  key=lambda pair: pair[0])]
        # Remove walls and pits from it
        sorted_nodes_ = [x for x in sorted_nodes if self.contents[x] != 'Wall' and self.contents[x] != 'Pit']
        return sorted_nodes_[0:n_nodes]

class AgentClockedContentMaze(ClockedContentMaze):
    def __init__(self, N, K, k, p, tau = 0.1):
        super(AgentClockedContentMaze, self).__init__(N, K, k, p, tau = tau)
        self.agentseq = ''
        self.end = False
    
    def populate(self, W, P, G, M, w_decay, s_decay):
        super(AgentClockedContentMaze, self).populate(W, P, G, M, w_decay, s_decay)
        # Choose a cell for the agent
        available_cells = [i for i, x in enumerate(self.contents) if x == None]
        self.agent = available_cells[randint(0, len(available_cells) - 1)]
    
    def tick(self):
        super(AgentClockedContentMaze, self).tick()
        
        agent_adj_len = len(a.graph[self.agent])
        agent_orientation = randint(0, agent_adj_len - 1)
        agent_dest = a.graph[self.agent][agent_orientation]
        counter = 0
        
        action = agent_orientation + 1
        gold = 0
        
        if self.contents[self.agent] == 'Gold':
            action = 0
            gold = 1
            self.end = True
        
        state = "R" + str(agent_adj_len) + ',' + str(self.wind[self.agent]) + ',' + str(self.smell[self.agent]) + ',' + str(gold) + ',' + str(action) + ';'
        self.agentseq += state
        
        if self.contents[agent_dest] != 'Wall':
            if action > 0:
                self.agent = agent_dest # Go forward!
        
        if self.contents[self.agent] == 'Pit':
            self.end = True
        if self.monster[self.agent] > 0:
            self.end = True

# Example

#import copy
a = AgentClockedContentMaze(60, 18, 2, 6, tau = 0.1)
a.construct()
a.populate(3, 5, 3, 3, 0.75, 0.75)
print(a.contents)
#print(a.agent)
#agent_save = a.agent
#backup = copy.deepcopy(a) # save the graph
total = ''

f = open("output.csv", "w")
for i in range(10000):
    b = AgentClockedContentMaze(60, 18, 2, 6, tau = 0.1)#copy.deepcopy(backup)
    b.construct()
    b.populate(3, 5, 3, 3, 0.75, 0.75)
    #b.agent = agent_save
    j = 0
    while not b.end:
        j += 1
        if j > 10000:
            break;
        b.tick()
    s = str(i) + ': ' + b.agentseq + '\n'
    f.write(s)
f.close()
