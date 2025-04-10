from GBA import *

#Entrée : une formule sous forme de liste de littéraux (ie une variable ou sa négation)
#Vérifie que cette formule est consistente cad qu'elle ne contient pas à la fois une variable et sa négation
def is_consistent(formula):
    for l in formula:
        if "~" + l in formula:
            return False
        if l.startswith("~") and l[1:] in formula:
            return False
    return True

#Entrées : 2 automates de buchi généralisés
#Sortie : le produit synchrone de ces automates
def product(gba1,gba2):
    states = {(state1, state2) for state1 in gba1.all_states for state2 in gba2.all_states}
    initials = {(state1, state2) for state1 in gba1.initial_states for state2 in gba2.initial_states}
    formulas = {f1.union(f2) for f1 in gba1.formulas for f2 in gba2.formulas}
    ap = gba1.ap.union(gba2.ap)
    edges = []
    #à compléter
    for f in formulas:
        if not is_consistent(f):
            continue
        f_frozen = frozenset(f)
        for s1 in gba1.all_states:
            for s2 in gba2.all_states:
                dest1 = gba1.get_successors(s1, frozenset({l for l in f if l in gba1.ap or "~" + l in gba1.ap}))
                dest2 = gba2.get_successors(s2, frozenset({l for l in f if l in gba2.ap or "~" + l in gba2.ap}))
                for d1 in dest1:
                    for d2 in dest2:
                        edges.append(((s1, s2), list(f), (d1, d2)))
    accepting = []
    for acc in gba1.accepting_states:
    	accepting.append(frozenset({(state1, state2) for state1 in acc for state2 in gba2.all_states}))
    for acc in gba2.accepting_states:
    	accepting.append(frozenset({(state1, state2) for state1 in gba1.all_states for state2 in acc}))
    return GBA(states, initials, ap, edges, accepting)
    	
if __name__ == "__main__":
    gba1 =GBA([0,1],[0,1],["a"],[(0,[],0),(0,["a"],1),(1,["a"],1)],[[1]])
    gba2 =GBA([0,1],[0,1],["b"],[(0,[],0),(0,["b"],1),(1,["b"],1)],[[1]])
    produitTest = product(gba1,gba2)
    produitTest.export("produitTest")
    produit = GBA([0,1,2,3],[0,1,2,3],["a", "b"],[(0,[],0),(0,["a","b"],3),(0,["a"],1),(1,["a"],1),(0,["b"],2),(1,["a","b"],3),(2,"b",2), (2,["a","b"],3), (3,["a","b"],3)],[[1,3],[2,3]])
    produit.export("produit")

