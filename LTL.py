# -*-coding:UTF-8 -*
from graphviz import Digraph


# A pseudo-LR(1) parser for simple regular expressions, based on the following
# context-free grammar G:
# [1] E -> 's'
# where s is any sequence of characters not featuring ().+~XGFU
# [2] E -> '('E')'
# [3] E -> '~'E*
# [4] E -> 'X'E*
# [5] E -> 'G'E*
# [6] E -> 'F'E*
# [7] E -> E('U'E)*
# [8] E -> E('.'E)*
# [9] E -> E('+'E)*
# The rules being ordered by decreasing priority.


# A class for input tokens
class token:

    def __init__(self, type_t, value_t=None):
        # The string 'type' stands for the symbol in the grammar's terminals
        # matched to the token.
        self.type = type_t
        # The string 'value' stands for the value carried by tokens of type "s".
        self.value = value_t


# A tree-based representation of regular expresssions
class LTL:

    def __init__(self, root, children = []):
        # The string attribute 'root' stands for the operator labelling the
        # root.
        self.root = root
        # The list attribute 'children'
        self.children = children

    # Exports a picture of the regular expression tree to 'file'.pdf.
    def export(self, file):
        graph = Digraph(filename = file)
        graph.graph_attr['rankdir'] = 'TB'
        if self.children:
            graph.attr('node', shape = 'circle', style = 'filled', \
                    fillcolor = 'white')
            graph.node("0", label = self.root)
            write_graph(self, "0", graph)
        else:
            graph.attr('node', shape = 'box', style = 'filled', \
                    fillcolor = 'white')
            graph.node("0", label = self.root)
        graph.render()
    
        
    def copy(self):
        cpchildren = []
        for child in self.children:
        	cpchildren.append(child.copy())
        return LTL(self.root, cpchildren)
        
    def convertNNF(self):
        if self.root == "non":
            child = self.children[0]
            self.root = child.root
            self.children = child.children
            self.negativeNNF()
        else:
            for child in self.children:
                child.convertNNF()
        
    def negativeNNF(self):
        if not self.children:
            self.children=[LTL(self.root, self.children)]
            self.root="non"
        elif self.root == "non":
            child = self.children[0]
            self.root = child.root
            self.children = child.children
            self.convertNNF()
        else:
            if self.root == "et":
                self.root = "ou"
            elif self.root == "ou":
                self.root = "et"
            elif self.root == "U":
                self.root = "R"
            elif self.root == "R":
                self.root = "U"
            elif self.root == "G":
                self.root = "F"
            elif self.root == "F":
                self.root = "G"
            for child in self.children:
                child.negativeNNF()
                
    def equals(self, formula):
        if self.root != formula.root:
            return False
        for i in range(len(self.children)):
            if not (self.children[i].equals(formula.children[i])):
                return False
        return True

# Writes in the Graphviz graph 'graph' the tree structure of the regular
# expression 'LTL', starting from its root 'root_string'.
def write_graph(LTL, root_string, graph):
    if LTL.children:
        index = 0
        for child in LTL.children:
            child_root = root_string + str(index)
            if not child.children:
                graph.attr('node', shape = 'box', style = 'filled', \
                    fillcolor = 'white')
                lab = child.root if child.root else "<&#949;>"
                graph.node(child_root, label = lab)
                graph.edge(root_string, child_root)
            else:
                graph.attr('node', shape = 'circle', style = 'filled', \
                    fillcolor = 'white')
                graph.node(child_root, label = child.root)
                graph.edge(root_string, child_root)
                write_graph(child, child_root, graph)
            index += 1


# A class for terminal and non-terminal symbols the parser can push on the
# stack
class symbol:

    def __init__(self, type_t, LTL_tree=None):
        # The string 'type' stands for the symbol in the grammar's vocabulary
        # matched to the symbol.
        self.type = type_t
        # The LTL 'tree' stands for the regular expression matched to the
        # symbol, based on the parsing operations applied so far.
        self.tree = LTL_tree


# A class for the bottom-up parsing process
class LTL_Parser:

    def __init__(self, LTL_string):
        # The input string 'stream' from which tokens are generated
        self.stream = LTL_string
        # The list 'stack' that stands for the parsing stack.
        self.stack = []

    # Returns the head token of the string attribute 'stream'; if the latter is
    # empty, returns the end of file token "$" instead.
    def look_ahead(self):
        if not self.stream:
            return token("$", "$")
        if self.stream[0] in ["(", ")", ".", "+", "X", "U", "~", "G", "F", "R"]:
            return token(self.stream[0], self.stream[0])
        else:
            index = 0
            while index < len(self.stream):
                if self.stream[index] in ["(", ")", ".", "+", "X", "U","~", "G", "F", "R"]:
                    break
                index += 1
            return token("s", self.stream[0:index])

    # Removes and returns the head token of the string attribute 'stream'; if
    # if the input stream is empty while expecting a token of type 'head_type',
    # raises an error.
    def pop_stream(self, head_type = ""):
        if not self.stream:
            if head_type:
                raise IndexError("End of string reached prematurely while " \
                    "looking for token '" + head_type + "'.")
            else:
                raise IndexError("End of string reached prematurely.")
        stream_head = self.look_ahead()
        self.stream = self.stream[len(stream_head.value):]
        return stream_head

    # Checks if rule [1] can be applied.
    def check_string_rule(self):
        return (len(self.stack) > 0) and (self.stack[-1].type == "s")

    # Checks if rule [2] can be applied.
    def check_par_rule(self):
        return (len(self.stack) > 2) and (self.stack[-1].type == ")") \
            and (self.stack[-2].type == "E") and (self.stack[-3].type == "(") \

    # Checks if rule [3] can be applied.
    def check_not_rule(self, look_ahead_t):
        return (len(self.stack) > 1) and (self.stack[-2].type == "~") \
            and (self.stack[-1].type == "E")
    # Checks if rule [4] can be applied.
    def check_next_rule(self):
        return (len(self.stack) > 1) and (self.stack[-2].type == "X") \
            and (self.stack[-1].type == "E")
            
    # Checks if rule [5] can be applied.       
    def check_G_rule(self, look_ahead_t):
        return (len(self.stack) > 1) and (self.stack[-2].type == "G") \
            and (self.stack[-1].type == "E")
            
    # Checks if rule [6] can be applied.
    def check_F_rule(self, look_ahead_t):
        return (len(self.stack) > 1) and (self.stack[-2].type == "F") \
            and (self.stack[-1].type == "E")
            
    # Checks if rule [7] can be applied; the type of the next token
    # 'look_ahead_t' is required in order to solve shift-reduce conflicts
    # by applying the grammar's priority rules.
    def check_until_rule(self, look_ahead_t):
        return (len(self.stack) > 2) and (self.stack[-1].type == "E") \
            and (self.stack[-2].type == "U") and (self.stack[-3].type == "E") \
            and not (look_ahead_t in {"X","G","F","~"})

    # Checks if rule [8] can be applied; the type of the next token
    # 'look_ahead_t' is required in order to solve shift-reduce conflicts
    # by applying the grammar's priority rules.
    def check_dot_rule(self, look_ahead_t):
        return (len(self.stack) > 2) and (self.stack[-1].type == "E") \
            and (self.stack[-2].type == ".") and (self.stack[-3].type == "E") \
            and not (look_ahead_t in {"X","G","F","~","U"})

    # Checks if rule [9] can be applied; the type of the next token
    # 'look_ahead_t' is required in order to solve shift-reduce conflicts
    # by applying the grammar's priority rules.
    def check_plus_rule(self, look_ahead_t):
        return (len(self.stack) > 2) and (self.stack[-1].type == "E") \
            and (self.stack[-2].type == "+") and (self.stack[-3].type == "E") \
            and not (look_ahead_t in {"X","G","F","~","U","."})

    # Checks if the implicit initial rule Z -> E'$' can be applied. Note that
    # the end of file symbol is never pushed on the stack; it merely appears
    # as an incoming token of type 'look_ahead_t' instead. Moreover, the stack
    # must consist in a single non-terminal symbol E in order to avoid
    # accepting with a non-empty stack.
    def check_initial_rule(self, look_ahead_t):
        return (len(self.stack) == 1) and (self.stack[0].type == "E") \
            and (look_ahead_t == "$")

    # Applies rule [1].
    def apply_string_rule(self):
        tree = self.stack[-1].tree
        self.stack = self.stack[:-1]
        self.stack.append(symbol("E", tree))

    # Applies rule [2].
    def apply_par_rule(self):
        tree = self.stack[-2].tree
        self.stack = self.stack[:-3]
        self.stack.append(symbol("E", tree))

    # Applies rule [3].
    def apply_not_rule(self):
        tree = self.stack[-1].tree
        self.stack = self.stack[:-2]
        self.stack.append(symbol("E", LTL("non", [tree])))
        
    # Applies rule [4].
    def apply_next_rule(self):
        tree = self.stack[-1].tree
        self.stack = self.stack[:-2]
        self.stack.append(symbol("E", LTL("X", [tree])))
        
    # Applies rule [5].    
    def apply_G_rule(self):
        tree = self.stack[-1].tree
        self.stack = self.stack[:-2]
        self.stack.append(symbol("E", LTL("G", [tree])))
    
    # Applies rule [6].
    def apply_F_rule(self):
        tree = self.stack[-1].tree
        self.stack = self.stack[:-2]
        self.stack.append(symbol("E", LTL("F", [tree])))
        
    # Applies rule [7].
    def apply_until_rule(self):
        right_tree = self.stack[-1].tree
        left_tree = self.stack[-3].tree
        self.stack = self.stack[:-3]
        self.stack.append(symbol("E", LTL("U", [left_tree, right_tree])))

    # Applies rule [8].
    def apply_dot_rule(self):
        right_tree = self.stack[-1].tree
        left_tree = self.stack[-3].tree
        self.stack = self.stack[:-3]
        self.stack.append(symbol("E", LTL("et", [left_tree, right_tree])))

    # Applies rule [9].
    def apply_plus_rule(self):
        right_tree = self.stack[-1].tree
        left_tree = self.stack[-3].tree
        self.stack = self.stack[:-3]
        self.stack.append(symbol("E", LTL("ou", [left_tree, right_tree])))

    # Shifts the incoming token of type 'look_ahead_t' on the stack.
    def shift(self, look_ahead_t):
        new_token = self.pop_stream(look_ahead_t)
        # String tokens carry a simple regular expression tree reduced to
        # a single node.
        if new_token.type == "s":
            if new_token.value == "ε":
                self.stack.append(symbol("s", LTL("")))
            else:
                self.stack.append(symbol("s", LTL(new_token.value)))
        # Other terminal symbols do not carry syntactic trees.
        else:
            self.stack.append(symbol(new_token.type))

    # The parser itself. It either returns a LTL tree or raises a SyntaxError
    # once it has read the entire stream yet cannot perform any reduction.
    # The stack trace is shown if the Boolean 'trace' is true.
    def parse(self, trace = False):
        while True:
            look_ahead = self.look_ahead()
            # Shows the stack trace for debugging purposes.
            if trace:
                for symb in self.stack:
                    print(symb.type, end=";")
                print()
            # First tries to apply the reduction rules in their matching
            # priority order.
            if self.check_string_rule():
                self.apply_string_rule()
            elif self.check_par_rule():
                self.apply_par_rule()
            elif self.check_next_rule():
                self.apply_next_rule()
            elif self.check_not_rule(look_ahead.type):
                self.apply_not_rule()
            elif self.check_G_rule(look_ahead.type):
                self.apply_G_rule()
            elif self.check_F_rule(look_ahead.type):
                self.apply_F_rule()
            elif self.check_until_rule(look_ahead.type):
                self.apply_until_rule()
            elif self.check_dot_rule(look_ahead.type):
                self.apply_dot_rule()
            elif self.check_plus_rule(look_ahead.type):
                self.apply_plus_rule()
            # If the initial reduction can be performed, the parsing process
            # succeeds.
            elif self.check_initial_rule(look_ahead.type):
                return self.stack[0].tree
            # It otherwise shifts a token from the input stream, assuming it is
            # not empty.
            elif look_ahead.type != "$":
                self.shift(look_ahead.type)
            # The parser can no longer shift or reduce, hence, fails.
            else:
                raise SyntaxError("Can no longer shift a symbol or reduce" \
                    " a rule.")


# Returns a tree of type LTL representing the string 'LTL_string'.
def new_LTL(LTL_string):
    return LTL_Parser(LTL_string).parse()


# Tests
if __name__ == "__main__":
    P1 = LTL_Parser("a")
    P1_tokens = []
    while P1.stream:
        P1_tokens.append(P1.look_ahead().value)
        P1.pop_stream()
    P1_tokens.append(P1.look_ahead().value)
    print(P1_tokens)
    formule = new_LTL("~(a+X~a+Gb.F~c)")
    formule.convertNNF()
    formule.export("test")
