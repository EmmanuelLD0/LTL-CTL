# -*-coding:UTF-8 -*
from collections import deque

# Entrée : une formule sous forme de liste de littéraux (ie une variable ou sa négation)
# Vérifie que cette formule est consistante cad qu'elle ne contient pas à la fois une variable et sa négation
def is_consistent(formula):
    for l in formula:
        if "~" + l in formula:
            return False
    return True

# Entrée : un automate de Büchi
# Sortie : renvoie True si cet automate n'admet aucune exécution acceptante, False sinon
def is_Buchi_empty(buchi):
    visited = set()
    stack = []

    # DFS classique
    def dfs(state):
        visited.add(state)
        stack.append(state)
        for formula in buchi.formulas:
            for succ in buchi.get_successors(state, formula):
                if succ not in visited:
                    if dfs(succ):
                        return True
                elif succ in stack:
                    # cycle trouvé
                    if succ in buchi.accepting_states[0]:
                        return True
        stack.pop()
        return False

    for init in buchi.initial_states:
        visited.clear()
        stack.clear()
        if dfs(init):
            return False  # L'automate **n'est pas** vide
    return True  # Aucun cycle acceptant trouvé → vide

# Entrée : un automate de Büchi généralisé
# Sortie : renvoie True si cet automate n'admet aucune exécution acceptante, False sinon
def is_GBA_empty(gba):
    # On transforme le GBA en automate de Büchi "classique" via le produit croisé avec les acceptants
    from GBA import GBA

    new_states = set()
    new_init = set()
    new_edges = []
    new_accepting = set()

    # Chaque acceptant devient une phase (on passe à un automate de Büchi "à compteur")
    for idx, accepting_set in enumerate(gba.accepting_states):
        for state in gba.all_states:
            new_state = (state, idx)
            new_states.add(new_state)
            if state in gba.initial_states and idx == 0:
                new_init.add(new_state)

    for idx, accepting_set in enumerate(gba.accepting_states):
        for ((state, formula), dests) in gba.next_states.items():
            for dest in dests:
                current = (state, idx)
                if state in accepting_set:
                    # si on est dans un état acceptant de la phase i → on passe à la phase suivante
                    next_idx = (idx + 1) % len(gba.accepting_states)
                else:
                    next_idx = idx
                next_state = (dest, next_idx)
                new_edges.append((current, list(formula), next_state))

    for (state, idx) in new_states:
        if idx == 0 and state in gba.accepting_states[0]:
            new_accepting.add((state, idx))

    # Création du nouvel automate de Büchi "classique"
    buchi = GBA(
        all_states=new_states,
        initial_states=new_init,
        propositions=gba.ap,
        edges=new_edges,
        acceptings=[new_accepting]
    )

    return is_Buchi_empty(buchi)