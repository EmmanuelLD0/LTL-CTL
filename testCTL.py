from CTL import CTL
from CTLchecker import satisfait
from kripke import mlaver

formules = [
    CTL("EX", [CTL("D")]),
    CTL("AX", [CTL("B")]),
    CTL("EU", [CTL("F"), CTL("D")]),
    CTL("AU", [CTL("F"), CTL("D")])
]

for i, f in enumerate(formules):
    print(f"Test {i+1}: formule = {f}")
    if satisfait(mlaver, f):
        print("  → Résultat : Satisfait")
    else:
        print("  → Résultat : Non satisfait")
