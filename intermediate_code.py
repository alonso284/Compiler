"""
CUADS
OPR OPN1 OPN2 RES

VARIABLES (INITIALIZE ALL IN DEFAULT VALUE)
:= DEFAULT _ A

GO TO (START OF MAIN)

FUNCTIONS

WHEN FUNCTION IS CALLED, PUSH TO STACK THE CALLING LINE (CALL) AND AFTER FUNCTION, POP (RETURN)
STACK IS FOR THE INTERPRETER, NOT FOR THE INTERMEDIATE CODE GENERATOR
BLOCKS
CALL FUNCTION _ _
RETURN _ _ _

FOR LOOPS:
#1 ACTION
#2 EXPRESSION
#3 GOTOF EXPRESSION 7_ : #4 IS TRUE, ELSE #7
#4 BLOCK
#5 ACTION 2
#6 GOTO 2 _ _

WHILE LOOPS:
#1 EXPRESSION
#2 GOTOF EXPRESSION 5 _: #3 IS TRUE, ELSE #5
#3 BLOCK
#4 GOTO 1 _ _

IF STATEMENTS:
#1 EXPRESSION
#2 GOTOF EXPRESSION 4 _: #3 IS TRUE, ELSE #4
#3 BLOCK
#4 BLOCK (ELSE IF EXISTS)
"""


from nodes_ast import DecrementNode, ForNode, AssignmentNode, FunctionCallNode, IfNode, ProgramNode, UnaryOpNode, WhileNode, WriteNode, IncrementNode, IdentifierNode, LiteralNode, BinaryOpNode, StringNode, CharNode

# DEFAULT TYPES
DEFAULT_VALUES = {
    "int": 0,
    "float": 0.0,
    "string": "",
    "char": "x",
    "bool": False,
}


class IntermediateCodeGenerator:
    def __init__(self):
        self.code = []

    functions_lines = {}  # Map function names to their starting line numbers in the code

    def generate(self, node):
        self.code.clear()
        self.functions_lines.clear()
        if isinstance(node, ProgramNode):
            self._generate_program(node)
        else:
            raise NotImplementedError(f"Code generation not implemented for node type: {type(node)}")
        
    def _generate_program(self, node: ProgramNode):
        # Generate code for variable declarations
        for var_decl in node.variables:
            default_value = DEFAULT_VALUES.get(var_decl.var_type, "0")
            self.code.append(f":= {var_decl.name} _ {default_value}")

        # Generate code for functions
        for function in node.functions:
            self._generate_function(function)

        # Generate code for the main block
        self._generate_block(node.block)

        self.code.append("END _ _ _")  # Mark the end of the program

    def _generate_function(self, function):
        print(f"Generating code for function: {function.name}")
        self.functions_lines[function.name] = len(self.code)  # Store the line number where the function starts
        self._generate_block(function.block)
        self.code.append("POP _ _ jump")  # Clean up the stack after the function returns
        self.code.append("GOTO jump _ _")  # Return to the caller

    def _generate_block(self, block):
        for statement in block.statements:
            self._generate_statement(statement)

    def _generate_statement(self, statement):
        if isinstance(statement, FunctionCallNode):
            self._function_call(statement.name)
        elif isinstance(statement, AssignmentNode):
            self._generate_assignment(statement)
        elif isinstance(statement, WriteNode):
            self._generate_write(statement)
        elif isinstance(statement, IncrementNode):
            self._generate_increment(statement)
        elif isinstance(statement, DecrementNode):
            self._generate_decrement(statement)
        elif isinstance(statement, WhileNode):
            self._generate_while(statement)
        elif isinstance(statement, ForNode):
            self._generate_for(statement)
        elif isinstance(statement, IfNode):
            self._generate_if(statement)
        else:
            raise NotImplementedError(f"Code generation not implemented for statement type: {type(statement)}")
        
    # =====================================================
    # STATEMENTS
    # =====================================================

    def _function_call(self, name):
        line_caller = len(self.code)  # Get the current line number to return to after the function call
        self.code.append(f"PUSH {line_caller} _ _")  # Push the return address onto the stack
        self.code.append(f"GOTO {self.functions_lines[name]} _ _")  # Jump to the function's starting line

    def _generate_assignment(self, node: AssignmentNode):
        variable = node.variable.name
        expression_code = self._generate_expression(node.expression)
        self.code.append(f":= {variable} _ {expression_code}")

    def _generate_write(self, node: WriteNode):
        expression_code = self._generate_expression(node.expression)
        self.code.append(f"WRITE {expression_code} _ _")

    def _generate_increment(self, node: IncrementNode):
        variable = node.variable.name
        self.code.append(f"+ {variable} 1 {variable}")

    def _generate_decrement(self, node: DecrementNode):
        variable = node.variable.name
        self.code.append(f"- {variable} 1 {variable}")

    def _generate_while(self, node: WhileNode):
        start_line = len(self.code)
        expression_code = self._generate_expression(node.condition)
        goto_line = len(self.code)
        self.code.append(f"GOTOF {expression_code} ") # rest added later
        
        self._generate_block(node.body)
        self.code.append(f"GOTO {start_line} _ _")
        end_line = len(self.code)
        self.code[goto_line] += f"{end_line} _" # complete the GOTOF

    def _generate_for(self, node: ForNode):
        self._generate_statement(node.init)
        start_line = len(self.code)
        expression_code = self._generate_expression(node.condition)
        goto_line = len(self.code)
        self.code.append(f"GOTOF {expression_code} ") # rest added later
        
        self._generate_block(node.body)
        self._generate_statement(node.update)
        self.code.append(f"GOTO {start_line} _ _")
        end_line = len(self.code)
        self.code[goto_line] += f"{end_line} _" # complete the GOTOF

    def _generate_if(self, node: IfNode):
        expression_code = self._generate_expression(node.condition)
        goto_line = len(self.code)
        self.code.append(f"GOTOF {expression_code} ") # rest added later
        self._generate_block(node.then_body)

        if node.else_body:
            go_to_end_line = len(self.code)
            self.code.append(f"GOTO ") # rest added later to skip the else block if the
            self.code[goto_line] += f"{len(self.code)} _" # complete the GOTOF
            self._generate_block(node.else_body)
            self.code[go_to_end_line] += f"{len(self.code)} _" # complete the GOTO to skip the else block
        else:
            self.code[goto_line] += f"{len(self.code)} _" # complete the GOTOF to skip the then block if the condition is false

    # =====================================================
    # EXPRESSIONS
    # =====================================================

    def _generate_expression(self, expression):
        if isinstance(expression, IdentifierNode):
            return expression.name
        elif isinstance(expression, LiteralNode):
            if isinstance(expression, StringNode) or isinstance(expression, CharNode):
                return f'"{expression.value}"'  # Add quotes around string and char literals
            return str(expression.value)
        elif isinstance(expression, BinaryOpNode):
            left_code = self._generate_expression(expression.left)
            right_code = self._generate_expression(expression.right)
            temp_var = f"t{len(self.code)}"  # Temporary variable for the result
            self.code.append(f"{expression.operator} {left_code} {right_code} {temp_var}")
            return temp_var
        elif isinstance(expression, UnaryOpNode):
            operand_code = self._generate_expression(expression.operand)
            temp_var = f"t{len(self.code)}"  # Temporary variable for the result
            self.code.append(f"{expression.operator} {operand_code} _ {temp_var}")
            return temp_var
        else:
            raise NotImplementedError(f"Code generation not implemented for expression type: {type(expression)}")
        
if __name__ == "__main__":
    from builder_ast import ASTBuilder
    from semantic_analyzer import SemanticAnalyzer
    from lark import Lark

    parser = Lark.open("parser.lark", parser="lalr")
    test_file = "tests/success/simple_program.k"
    with open(test_file, "r") as file:
        code = file.read()
    
    tree = parser.parse(code)
    ast = ASTBuilder().transform(tree)
    SemanticAnalyzer().analyze(ast)
    generator = IntermediateCodeGenerator()
    generator.generate(ast)


    for line_num, line in enumerate(generator.code):
        print(f"{line_num}: {line}")