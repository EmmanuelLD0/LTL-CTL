# -*-coding:UTF-8 -*
from graphviz import Digraph

# A class for input tokens
class token:

    def __init__(self, type_t, value_t=None):
        # The string 'type' stands for the symbol in the grammar's terminals
        # matched to the token.
        self.type = type_t
        # The string 'value' stands for the value carried by tokens of type "s".
        self.value = value_t

# A tree-based representation of CTL formulas
class CTL:

    def __init__(self, root, children = []):
        # The string attribute 'root' stands for the operator labelling the
        # root.
        self.root = root
        # The list attribute 'children'
        self.children = children

    # Exports a picture of the CTL formula tree to 'file'.pdf.
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


# Writes in the Graphviz graph 'graph' the tree structure of the
# CTL formula ctl, starting from its root 'root_string'.
def write_graph(ctl, root_string, graph):
    if ctl.children:
        index = 0
        for child in ctl.children:
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

    def __init__(self, type_t, CTL_tree=None):
        # The string 'type' stands for the symbol in the grammar's vocabulary
        # matched to the symbol.
        self.type = type_t
        # The CTL 'tree' stands for the regular expression matched to the
        # symbol, based on the parsing operations applied so far.
        self.tree = CTL_tree


          
# A class for the bottom-up parsing process
class CTL_Parser:

    def __init__(self, CTL_string):
        # The input string 'stream' from which tokens are generated
        self.stream = CTL_string
        # The list 'stack' that stands for the parsing stack.
        self.stack = []

    # Returns the head token of the string attribute 'stream'; if the latter is
    # empty, returns the end of file token "$" instead.
    def look_ahead(self):
        if not self.stream:
            return token("$", "$")
        if self.stream[0] in ["(", ")", ".", "+", "~"]:
            return token(self.stream[0], self.stream[0])
        elif self.stream[0] in ["A", "E"] and len(self.stream)>1 and self.stream[1] in ["X","U","G","F","R"]:
            return token(self.stream[0]+self.stream[1], self.stream[0]+self.stream[1])
        else:
            index = 0
            while index < len(self.stream):
                if self.stream[index] in ["(", ")", ".", "+","~"]:
                    break
                elif self.stream[index] in ["A", "E"] and index+1<len(self.stream) and self.stream[index+1] in ["X","U","G","F","R"]:
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
    def check_AX_rule(self):
        return (len(self.stack) > 1) and (self.stack[-2].type == "AX") \
            and (self.stack[-1].type == "E")
            
    # Checks if rule [5] can be applied.
    def check_EX_rule(self):
        return (len(self.stack) > 1) and (self.stack[-2].type == "EX") \
            and (self.stack[-1].type == "E")
            
    # Checks if rule [6] can be applied.       
    def check_AG_rule(self, look_ahead_t):
        return (len(self.stack) > 1) and (self.stack[-2].type == "AG") \
            and (self.stack[-1].type == "E")
            
    # Checks if rule [7] can be applied.
    def check_AF_rule(self, look_ahead_t):
        return (len(self.stack) > 1) and (self.stack[-2].type == "AF") \
            and (self.stack[-1].type == "E")
                
    # Checks if rule [8] can be applied.       
    def check_EG_rule(self, look_ahead_t):
        return (len(self.stack) > 1) and (self.stack[-2].type == "EG") \
            and (self.stack[-1].type == "E")
            
    # Checks if rule [9] can be applied.
    def check_EF_rule(self, look_ahead_t):
        return (len(self.stack) > 1) and (self.stack[-2].type == "EF") \
            and (self.stack[-1].type == "E")
            
    # Checks if rule [10] can be applied; the type of the next token
    # 'look_ahead_t' is required in order to solve shift-reduce conflicts
    # by applying the grammar's priority rules.
    def check_AU_rule(self, look_ahead_t):
        return (len(self.stack) > 2) and (self.stack[-1].type == "E") \
            and (self.stack[-2].type == "AU") and (self.stack[-3].type == "E") \
            and not (look_ahead_t in {"AX","AG","AF","EX","EG","EF","~"})
            
    # Checks if rule [11] can be applied; the type of the next token
    # 'look_ahead_t' is required in order to solve shift-reduce conflicts
    # by applying the grammar's priority rules.
    def check_EU_rule(self, look_ahead_t):
        return (len(self.stack) > 2) and (self.stack[-1].type == "E") \
            and (self.stack[-2].type == "EU") and (self.stack[-3].type == "E") \
            and not (look_ahead_t in {"AX","AG","AF","EX","EG","EF""~"})

    # Checks if rule [12] can be applied; the type of the next token
    # 'look_ahead_t' is required in order to solve shift-reduce conflicts
    # by applying the grammar's priority rules.
    def check_dot_rule(self, look_ahead_t):
        return (len(self.stack) > 2) and (self.stack[-1].type == "E") \
            and (self.stack[-2].type == ".") and (self.stack[-3].type == "E") \
            and not (look_ahead_t in {"X","G","F","~","U"})

    # Checks if rule [13] can be applied; the type of the next token
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
        self.stack.append(symbol("E", CTL("non", [tree])))
        
    # Applies rule [4].
    def apply_AX_rule(self):
        tree = self.stack[-1].tree
        self.stack = self.stack[:-2]
        self.stack.append(symbol("E", CTL("AX", [tree])))
        
    # Applies rule [5].
    def apply_EX_rule(self):
        tree = self.stack[-1].tree
        self.stack = self.stack[:-2]
        self.stack.append(symbol("E", CTL("EX", [tree])))
        
    # Applies rule [6].    
    def apply_AG_rule(self):
        tree = self.stack[-1].tree
        self.stack = self.stack[:-2]
        self.stack.append(symbol("E", CTL("AG", [tree])))
    
    # Applies rule [7].
    def apply_AF_rule(self):
        tree = self.stack[-1].tree
        self.stack = self.stack[:-2]
        self.stack.append(symbol("E", CTL("AF", [tree])))
        
    # Applies rule [8].    
    def apply_EG_rule(self):
        tree = self.stack[-1].tree
        self.stack = self.stack[:-2]
        self.stack.append(symbol("E", CTL("EG", [tree])))
    
    # Applies rule [9].
    def apply_EF_rule(self):
        tree = self.stack[-1].tree
        self.stack = self.stack[:-2]
        self.stack.append(symbol("E", CTL("EF", [tree])))
        
    # Applies rule [10].
    def apply_AU_rule(self):
        right_tree = self.stack[-1].tree
        left_tree = self.stack[-3].tree
        self.stack = self.stack[:-3]
        self.stack.append(symbol("E", CTL("AU", [left_tree, right_tree])))
        
    # Applies rule [11].
    def apply_EU_rule(self):
        right_tree = self.stack[-1].tree
        left_tree = self.stack[-3].tree
        self.stack = self.stack[:-3]
        self.stack.append(symbol("E", CTL("EU", [left_tree, right_tree])))

    # Applies rule [12].
    def apply_dot_rule(self):
        right_tree = self.stack[-1].tree
        left_tree = self.stack[-3].tree
        self.stack = self.stack[:-3]
        self.stack.append(symbol("E", CTL("et", [left_tree, right_tree])))

    # Applies rule [13].
    def apply_plus_rule(self):
        right_tree = self.stack[-1].tree
        left_tree = self.stack[-3].tree
        self.stack = self.stack[:-3]
        self.stack.append(symbol("E", CTL("ou", [left_tree, right_tree])))

    # Shifts the incoming token of type 'look_ahead_t' on the stack.
    def shift(self, look_ahead_t):
        new_token = self.pop_stream(look_ahead_t)
        # String tokens carry a simple regular expression tree reduced to
        # a single node.
        if new_token.type == "s":
            if new_token.value == "ε":
                self.stack.append(symbol("s", CTL("")))
            else:
                self.stack.append(symbol("s", CTL(new_token.value)))
        # Other terminal symbols do not carry syntactic trees.
        else:
            self.stack.append(symbol(new_token.type))

    # The parser itself. It either returns a CTL tree or raises a SyntaxError
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
            elif self.check_EX_rule():
                self.apply_EX_rule()
            elif self.check_AX_rule():
                self.apply_AX_rule()
            elif self.check_not_rule(look_ahead.type):
                self.apply_not_rule()
            elif self.check_AG_rule(look_ahead.type):
                self.apply_AG_rule()
            elif self.check_AF_rule(look_ahead.type):
                self.apply_AF_rule()
            elif self.check_AU_rule(look_ahead.type):
                self.apply_AU_rule()
            elif self.check_EG_rule(look_ahead.type):
                self.apply_EG_rule()
            elif self.check_EF_rule(look_ahead.type):
                self.apply_EF_rule()
            elif self.check_EU_rule(look_ahead.type):
                self.apply_EU_rule()
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


# Returns a tree of type CTL representing the string 'CTL_string'.
def new_CTL(CTL_string):
    return CTL_Parser(CTL_string).parse()

#exemple de formule            

formule3 = new_CTL("(AF(aEUb)AU(EXAX(cAUd)))")
formule3.export("formule3")
