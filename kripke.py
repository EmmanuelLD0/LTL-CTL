# -*-coding:UTF-8 -*
from graphviz import Digraph


# Kripke structure
class Kripke:

    def __init__(self, all_states, initial_states, propositions, edges, valuations):

        # States: a set of integers
        self.all_states = set(all_states)
        # Initial states: a set of integers
        self.initial_states = set(initial_states).intersection(self.all_states)
        # There must be an initial state; if there isn't, an initial state 0
        # is added
        if not self.initial_states:
            self.initial_states.add(0)
            self.all_states.add(0)
        self.ap = propositions
        self.next_states = {state: set()
                            for state in self.all_states}
        for edge in set(edges):
            if (edge[0] in self.all_states) and (edge[1] in self.all_states):
                self.next_states[edge[0]].add(edge[1])
        self.valuation = valuations
        self.labels = {state:str(self.valuation[state]) for state in self.all_states}

    # Adds a new state to the structure
    def add_state(self, val):
        add_state = max(self.all_states) + 1
        self.all_states.add(add_state)
        self.next_states[add_state] = set()
        self.valuation[add_state] = val
        self.labels[add_state]= str(val)
        return add_state

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

    # Returns the set of all states reachable from the state 'origin'
    # with one transition
    def get_successors(self, origin):
        if not origin in self.all_states:
            raise KeyError("The origin " + str(origin) \
                    + " isn't a known state.")
        return self.next_states[origin]

    # Exports a picture of the automaton to 'file'.pdf.
    def export(self, file):
        graph = Digraph(filename = file)
        graph.graph_attr['rankdir'] = 'LR'
        for state in self.all_states:
            node_shape = 'circle'
            graph.attr('node', shape = node_shape, style = 'filled', \
                    fillcolor = 'white')
            graph.node(str(state), label = self.labels[state])
            if state in self.initial_states:
                graph.node(str(state) + "_i", style = "invisible")
                graph.edge(str(state) + "_i", str(state))
        for state in self.all_states:
            for next_state in self.next_states[state]:
                edge_colour = 'black'
                edge_label = ""
                graph.edge(str(state), str(next_state), label=edge_label,
                            color=edge_colour)
        graph.render()
        
#machine à laver
mlaver=Kripke([0,1,2,3,4],[0],["B","F","D","V"],[(0,1),(0,2),(1,3),(1,0),(2,3),(3,2),(3,4),(4,4)],{0:set(),1:{"F"},2:{"B"},3:{"B","F"},4:{"B","F","D","V"}})
mlaver.export("mlaver")
