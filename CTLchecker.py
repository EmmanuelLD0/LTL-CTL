# -*-coding:UTF-8 -*
from CTL import *
from kripke import *

def find(formule, val):
    for couple in val:
        if formule == couple[0]:
            return (True, couple[1])
    return (False, set())

def traitTerm(structure, formule, val):
    result = set()
    for state in structure.all_states:
        if formule.root in structure.valuation[state]:
            result.add(state)
    val.append((formule, result))
    return val

def traitET(structure, formule, val):
    f1, f2 = formule.children
    (_, sats1) = find(f1, val)
    (_, sats2) = find(f2, val)
    result = sats1 & sats2
    val.append((formule, result))
    return val

def traitNON(structure, formule, val):
    f = formule.children[0]
    (_, sats) = find(f, val)
    result = structure.all_states - sats
    val.append((formule, result))
    return val

def traitOU(structure, formule, val):
    f1, f2 = formule.children
    (_, sats1) = find(f1, val)
    (_, sats2) = find(f2, val)
    result = sats1 | sats2
    val.append((formule, result))
    return val

def traitIMP(structure, formule, val):
    f1, f2 = formule.children
    (_, sats1) = find(f1, val)
    (_, sats2) = find(f2, val)
    result = (structure.all_states - sats1) | sats2
    val.append((formule, result))
    return val

def traitEX(structure, formule, val):
    sous_formule = formule.children[0]
    (_, sats) = find(sous_formule, val)
    result = set()
    for q in structure.all_states:
        for succ in structure.get_successors(q):
            if succ in sats:
                result.add(q)
                break
    val.append((formule, result))
    return val

def traitAX(structure, formule, val):
    sous_formule = formule.children[0]
    (_, sats) = find(sous_formule, val)
    result = set()
    for q in structure.all_states:
        successeurs = structure.get_successors(q)
        if successeurs and successeurs <= sats:
            result.add(q)
    val.append((formule, result))
    return val

def traitEU(structure, formule, val):
    f1, f2 = formule.children
    (_, sats1) = find(f1, val)
    (_, sats2) = find(f2, val)
    result = set(sats2)
    changed = True
    while changed:
        changed = False
        for q in structure.all_states:
            if q in sats1:
                for succ in structure.get_successors(q):
                    if succ in result:
                        if q not in result:
                            result.add(q)
                            changed = True
    val.append((formule, result))
    return val

def traitAU(structure, formule, val):
    f1, f2 = formule.children
    (_, sats1) = find(f1, val)
    (_, sats2) = find(f2, val)
    result = set(sats2)
    changed = True
    while changed:
        changed = False
        for q in structure.all_states:
            if q in sats1 and all(succ in result for succ in structure.get_successors(q)):
                if q not in result:
                    result.add(q)
                    changed = True
    val.append((formule, result))
    return val

def traitement(structure, formule, val):
    if formule.root == "et":
        return traitET(structure, formule, val)
    elif formule.root == "non":
        return traitNON(structure, formule, val)
    elif formule.root == "ou":
        return traitOU(structure, formule, val)
    elif formule.root == "=>":
        return traitIMP(structure, formule, val)
    elif formule.root == "EX":
        return traitEX(structure, formule, val)
    elif formule.root == "AX":
        return traitAX(structure, formule, val)
    elif formule.root == "EU":
        return traitEU(structure, formule, val)
    elif formule.root == "AU":
        return traitAU(structure, formule, val)
    else:
        raise Exception("Etiquette invalide : " + formule.root)

def CTLcheck(structure, formule, val):
    (found, states) = find(formule, val)
    if found:
        return val
    if formule.children:
        for child in formule.children:
            val = CTLcheck(structure, child, val)
        return traitement(structure, formule, val)
    else:
        return traitTerm(structure, formule, val)

def satisfait(structure, formule):
    val = CTLcheck(structure, formule, [])
    (_, states) = find(formule, val)
    print(f"Formule {formule}: États satisfaisants = {states}")  # Debugging log
    return structure.initial_states <= states
