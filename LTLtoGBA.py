# -*-coding:UTF-8 -*
from LTL import *
from GBA import *

def equals(formules1, formules2):
	difference = formules1.copy()
	for form1 in formules2:
		equals = False
		for form2 in formules1:
			if form1.equals(form2):
				difference.remove(form2)
				equals = True
		if not equals:
			return False
	return not difference

def findall(val, formule):
	result = set()
	for couple in val:
		if equals(formule,couple[0]):
			result.add(couple[1])
	return result
	
def clean(formules):
	new = []
	for form1 in formules:
		toAdd = True
		for form2 in new:
			if form1.equals(form2):
				toAdd = False
		if toAdd:
			new.append(form1)
	formules = new
	return new

def copy(formules):
	result = []
	for formule in formules:
		result.append(formule.copy())
	return result
	
def is_in(formule, formules):
	for formule2 in formules:
		if formule.equals(formule2):
			return True
	return False

def duplicate(state, structure, todo, val, toExpand):
	statecp=structure.add_state()
	if state in structure.initial_states:
		structure.add_initial(statecp)
	update_val(state, statecp, val)
	todo[statecp]=copy(todo[state])
	todo[state]=copy(todo[state])
	toExpand.append(statecp)
	return statecp

def update_val(state, statecp, val):
	for couple in val:
		if couple[1]==state:
			val.append((couple[0],statecp))
	return val

def traitET(formule, i, structure, todo, state, val, toExpand):
	child1 = formule.children[0]
	child2 = formule.children[1]
	formulecp = copy(todo[state])
	todo[state] = formulecp
	formulecp[i] = child1
	formulecp.append(child2)
	val.append((formulecp,state))
	return True
	
def traitOU(formule, i, structure, todo, state, val, toExpand):
	#on duplique l'état considéré pour avoir deux choix de transitions possibles
	state2 = duplicate(state, structure, todo, val, toExpand)
	#on récupère les formules à droite et à gauche du OU
	child1 = formule.children[0]
	child2 = formule.children[1]
	#on modifie les formules courantes pour avoir dans un état child1 et dans l'autre child2
	todo[state][i] =  child1.copy()
	todo[state2][i] =  child2.copy()
	#on ajoute le fait que state et state2 satisfont le nouvel ensemble de formules
	val.append((todo[state], state))
	val.append((todo[state2],state2))
	return True
	
def traitF(formule, i, structure, todo, state, val, toExpand):
	#on duplique l'état considéré pour avoir deux choix de transitions possibles
	state2 = duplicate(state, structure, todo, val, toExpand)
	#on récupère la formule sous le F
	child = formule.children[0]
	#on construit la formule avec XF
	nextF = LTL("X", [formule])
	#on modifie les formules courantes pour avoir dans un état child et dans l'autre XF(child)
	todo[state2][i] =  child
	todo[state][i] = nextF
	#on ajoute le fait que state et state2 satisfont le nouvel ensemble de formules
	val.append((todo[state], state))
	val.append((todo[state2],state2))
	return True
	
def traitG(formule, i, structure, todo, state, val, toExpand):
	child = formule.children[0]
	formulecp = todo[state].copy()
	todo[state] = formulecp
	formulecp.append(child)
	formulecp[i] = LTL("X", [formule])
	val.append((formulecp,state))
	return True

def traitU(formule, i, structure, todo, state, val, toExpand):
	#on duplique l'état considéré pour avoir deux choix de transitions possibles
	state2 = duplicate(state, structure, todo, val, toExpand)
	#on récupère les formules à droite et à gauche du U
	child1 = formule.children[0]
	child2 = formule.children[1]
	#on construit la formule avec X..U..
	nextU = LTL("X", [formule])
	#on modifie les formules courantes
	#à compléter
	# cas 1 : on satisfait la partie droite -> on remplace U par child2
	todo[state2][i] = child2
	# cas 2 : on continue à satisfaire la partie gauche -> on garde child1 et ajoute X(U)
	todo[state][i] = nextU
	todo[state].append(child1)
	#on ajoute le fait que state et state2 satisfont le nouvel ensemble de formules
	val.append((todo[state], state))
	val.append((todo[state2],state2))
	return True	

def traitement(done, i, structure, todo, state, val, toExpand):
	formule = todo[state][i]
	if formule.root == "et":
		return traitET(formule, i, structure, todo, state, val, toExpand)
	elif formule.root == "ou":
		return traitOU(formule, i, structure, todo, state, val, toExpand)
	elif formule.root == "F":
		return traitF(formule, i, structure, todo, state, val, toExpand)
	elif formule.root == "G":
		return traitG(formule, i, structure, todo, state, val, toExpand)
	elif formule.root == "U":
		return traitU(formule, i, structure, todo, state, val, toExpand)
	else:
		return False

def buildBuchi(formule, propositions):
	structure = GBA([0],[0],propositions,[],[])
	val=[([formule], 0)]
	todo = {0:[formule]}
	expandState(structure, todo, 0, val, [0])
	accept_conditions(structure, todo, val)
	return structure
	
		
def expandState(structure, todo, state, val, toExpand):
	done = False
	i = 0
	while not done and i < len(todo[state]):
		done = traitement(done, i, structure, todo, state, val, toExpand)
		i=i+1
	if not done:
		toExpand = toExpand[1:] 
	if toExpand:
		expandState(structure, todo, toExpand[0], val, toExpand)
	else:
		computeSucc(structure, todo, val)
	return val
		
def computeSucc(structure, todo, val):
	states = structure.all_states.copy()
	for state in states:
		succ = findall(val, next(todo[state]))
		if not succ:
			new = structure.add_state()
			val.append((next(todo[state]),new))
			todo[new]=next(todo[state])
			expandState(structure, todo, new, val, [new])
			succ = findall(val, next(todo[state]))
		label = now(todo[state])
		if is_consistent(label):
			for s in succ:
				structure.add_edge(state,label, s)
				
def accept_conditions(structure, todo, val):
	cond = []
	for couple in val:
		for formule in couple[0]:
			if formule.root in {"F","U"} and not is_in(formule,cond):
				cond.append(formule)
	sets = []
	for i in range(len(cond)):
		formule = cond[i]
		sets.append([])
		for state in structure.all_states:
			if not is_in(LTL("X", [formule]), todo[state]):
				sets[i].append(state)
	structure.change_accept(sets)
	return structure
				
	
def next(formules):
	retour = []
	for formule in formules:
		if formule.root == "X":
			retour.append(formule.children[0])
	return retour
	
def now(formules):
	retour = []
	for formule in formules:
		if formule.root == "non":
			retour.append("~"+formule.children[0].root)
		if not formule.children:
			retour.append(formule.root)
	return retour

if __name__ == "__main__":	
	formule = new_LTL("G(a).Fb")
	trad = buildBuchi(formule, ["a","b"])
	trad.export("trad")
	print(trad.accepting_states)
