from random import randint

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
#         print(r_weights)
        
        # Validity of using the node for connection
        node_validity = [x != 0 for x in r_weights]
#         print(node_validity)
        
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
#             print(req_edges_max_i, req_edges_min_i)
            self.graph[req_edges_max_i].append(req_edges_min_i)
            self.graph[req_edges_min_i].append(req_edges_max_i)
            
#             print(r_weights)
                
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

a = ContentMaze(4, 3, 2, 2)
a.construct()
a.populate(1,1,1,1,0.3,0.1)
a.print_maze()
