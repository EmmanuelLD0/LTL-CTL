import * from GBA
import * from kripke
import * from LTL
import * from LTLtoGBA
import * from product
import * from emptyTest

#Entrées : une formule LTL et une structure de Kripke et un ensemble de propositions atomiques
#Sortie : renvoie True si ttes les traces de la structure satisfont la formule faux sinon
def satisfait(formule, kripke):
    neg = LTL("non", [formule]).convertNNF()
    propositions = kripke.ap
    gba1 = buildBuchi(neg, propositions)
    gba2 = kripke.toGBA()
    produit = product(gba1,gba2)
    return is_GBA_empty(produit)

if __name__ == "__main__":	
    #machine à laver
    propositions = ["b","f","d","v"]
    mlaver=Kripke([0,1,2,3,4],[0],["b","f","d","v"],[(0,1),(0,2),(1,3),(1,0),(2,3),(3,2),(3,4),(4,4)],{0:set(),1:{"f"},2:{"b"},3:{"b","f"},4:{"b","f","d","v"}})
    mlaver.export("mlaver")
    #Test avec formule1, doit être faux
    formule1 = new_LTL("F(d)")
    satisfait(formule1, mlaver, ["b","f","d","v"])
    #Test avec formule2, doit être vrai
    formule2 = new_LTL("G(~d+f)")
    satisfait(formule2, mlaver, ["b","f","d","v"])
    #Test avec formule3, doit être vrai
    formule3 = new_LTL("G(~d+G(d))")
    satisfait(formule3, mlaver, ["b","f","d","v"])
    #Test avec formule4, doit être vrai
    formule4 = new_LTL("G(~d.~v)+F(d.v))")
    satisfait(formule4, mlaver, ["b","f","d","v"])
