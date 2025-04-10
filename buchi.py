# -*-coding:UTF-8 -*
from graphviz import Digraph


def fstr(formula):
    form_str = ""
    for l in formula:
    	form_str = form_str+l+','
    return form_str[:-1]
    
def is_consistent(formula):
    for l in formula:
    	if "~"+l in formula:
    	    return False
    return True

# Buchi automata
class Buchi:

    def __init__(self, all_states, initial_states, propositions, edges, accepting):

        # States: a set of integers
        self.all_states = set(all_states)
        # Initial states: a set of integers
        self.initial_states = set(initial_states).intersection(self.all_states)
        # There must be an initial state; if there isn't, an initial state 0
        # is added
        if not self.initial_states:
            self.initial_states.add(0)
            self.all_states.add(0)
        #Defining the set of accepting states
        self.accepting_states = set(accepting)
        #Defining the set of propositionnal variables
        self.ap = set(propositions)
        #We build the set of formulas appearing in transitions
        #A formula is represented by a set of litterals ie a variable or its negation
        if edges:
        	self.formulas = {frozenset(formula) for (_,formula,_) in edges}
        else:
        	self.formulas = set()
        self.next_states = {(state, formula): set()
                            for state in self.all_states
                            for formula in self.formulas}
        for edge in edges:
            if (edge[0] in self.all_states) and (edge[2] in self.all_states) and is_consistent(edge[1]):
                self.next_states[(edge[0], frozenset(edge[1]))].add(edge[2])
        self.labels = {state:str(state) for state in self.all_states}

    # Adds a new state to the structure
    def add_state(self):
        add_state = max(self.all_states) + 1
        self.all_states.add(add_state)
        for formula in self.formulas:
        	self.next_states[add_state,formula] = set()
        self.labels[add_state]= str(add_state)
        return add_state
        
    def add_initial(self, state):
        self.initial_states.add(state)
        return state

    # Removes the state 'state' from the structure if it exists.
    def remove_state(self, state):
        if state in self.all_states:
            self.all_states.remove(state)
            if state in self.initial_states:
                self.initial_states.remove(state)
            del self.labels[state]
            del self.valuation[state]
            # Remove the successors of 'state', but also all the edges
            # leading to 'state'
            del self.next_states[state]
            for origin in self.all_states:
                if state in self.next_states[origin]:
                    self.next_states[origin].remove(state)


    # Adds a new edge from the state 'origin' to the state 'destination'
    def add_edge(self, origin, formula, destination):
        if origin in self.all_states:
            if destination in self.all_states:
            	if not frozenset(formula) in self.formulas:
            	    self.formulas.add(frozenset(formula))
            	    for st in self.all_states:
            	        self.next_states[(st, frozenset(formula))] = set()
            	self.next_states[(origin, frozenset(formula))].add(destination)
            else:
                raise KeyError("The destination " + str(destination) \
                        + " isn't a known state.")
        else:
                raise KeyError("The origin " + str(origin) \
                    + " isn't a known state.")


    # Returns the set of all states reachable from the state 'origin'
    # with one transition
    def get_successors(self, origin, formula):
        if not origin in self.all_states:
            raise KeyError("The origin " + str(origin) \
                    + " isn't a known state.")
        return self.next_states[(origin, formula)]

    # Exports a picture of the automaton to 'file'.pdf.
    def export(self, file):
        graph = Digraph(filename = file)
        graph.graph_attr['rankdir'] = 'LR'
        for state in self.all_states:
            node_shape = 'circle'
            if state in self.accepting_states:
                node_shape = 'doublecircle'
            graph.attr('node', shape = node_shape, style = 'filled', \
                    fillcolor = 'white')
            graph.node(str(state), label = self.labels[state])
            if state in self.initial_states:
                graph.node(str(state) + "_i", style = "invisible")
                graph.edge(str(state) + "_i", str(state))
        for state in self.all_states:
            for formula in self.formulas:
                for next_state in self.next_states[(state, formula)]:
                    if not formula:
                        edge_label = "True"
                    else:
                    	edge_label = fstr(formula)
                    graph.edge(str(state), str(next_state), label=edge_label,
                            color='black')
        graph.render()
        
#exemple
exempleCours=Buchi([0,1],[0,1],["a","b"],[(0,["b"],0),(0,["a","b"],1),(1,["a","b"],1)],[1])
exempleCours.export("BuchiExemple")
