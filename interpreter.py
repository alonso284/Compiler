"""
For operands, if FIRST letter is digit, or surrounded by double quotes, it's a literal. Otherwise, it's an identifier.
"""

class Interpreter:

    def __init__(self):
        self.index = 0
        self.stack = []
        self.variables = {}

    def run(self, code):
        self.index = 0
        self.stack = []
        self.variables = {}
        while self.index < len(code):
            op, opn1, opn2, res = code[self.index]
            # print(f"Executing line {self.index}: {op} {opn1} {opn2} {res}")
            self._execute(op, opn1, opn2, res)
            self.index = self.index + 1

    def _execute(self, op, opn1, opn2, res):
        if op == ":=":
            value = self._get_value(opn1)
            self.variables[res] = value
        elif op == "NOT":
            value = self._get_value(opn1)
            self.variables[res] = not value
        elif op == "AND":
            value1 = self._get_value(opn1)
            value2 = self._get_value(opn2)
            self.variables[res] = value1 and value2
        elif op == "OR":
            value1 = self._get_value(opn1)
            value2 = self._get_value(opn2)
            self.variables[res] = value1 or value2
        elif op == "+":
            value1 = self._get_value(opn1)
            value2 = self._get_value(opn2)
            self.variables[res] = value1 + value2
        elif op == "-":
            value1 = self._get_value(opn1)
            value2 = self._get_value(opn2)
            self.variables[res] = value1 - value2
        elif op == "*":
            value1 = self._get_value(opn1)
            value2 = self._get_value(opn2)
            self.variables[res] = value1 * value2
        elif op == "/":
            value1 = self._get_value(opn1)
            value2 = self._get_value(opn2)
            self.variables[res] = value1 / value2
        elif op == "==":
            value1 = self._get_value(opn1)
            value2 = self._get_value(opn2)
            self.variables[res] = value1 == value2
        elif op == "!=":
            value1 = self._get_value(opn1)
            value2 = self._get_value(opn2)
            self.variables[res] = value1 != value2
        elif op == "<":
            value1 = self._get_value(opn1)
            value2 = self._get_value(opn2)
            self.variables[res] = value1 < value2
        elif op == "<=":
            value1 = self._get_value(opn1)
            value2 = self._get_value(opn2)
            self.variables[res] = value1 <= value2
        elif op == ">":
            value1 = self._get_value(opn1)
            value2 = self._get_value(opn2)
            self.variables[res] = value1 > value2
        elif op == ">=":
            value1 = self._get_value(opn1)
            value2 = self._get_value(opn2)
            self.variables[res] = value1 >= value2
        elif op == "WRITE":
            value = self._get_value(opn1)
            print(value)
        elif op == "GOTO":
            self.index = int(opn1) - 1  # -1 because we will increment index after this method
        elif op == "PUSH":
            self.stack.append(self.index+1)
        elif op == "POP":
            self.index = self.stack.pop()
        elif op == "GOTOF":
            condition = self._get_value(opn1)
            if not condition:
                self.index = int(opn2) - 1  # -1 because we will increment index after this method
        elif op == "END":
            print("Program finished.")
        else:
            raise NotImplementedError(f"Operation not implemented: {op}")

    def _get_value(self, operand):
        if not operand:
            return ""
        if operand[0].isdigit():
            if "." in operand:
                return float(operand)
            return int(operand)
        if (operand[0] == '"'  and operand[-1] == '"'):
            return operand.strip('"')  # Return literal value without quotes
        if operand == "True" or operand == "False":
            return operand == "True"  # Convert string to boolean
        return self.variables.get(operand, 0)  # Return variable value or 0 if not defined
    
if __name__ == "__main__":
    from lark import Lark
    from builder_ast import ASTBuilder
    from semantic_analyzer import SemanticAnalyzer
    from intermediate_code import IntermediateCodeGenerator

    parser = Lark.open("parser.lark", parser="lalr")
    with open("tests/success/function.k", "r") as file:
        code = file.read()

    tree = parser.parse(code)
    ast = ASTBuilder().transform(tree)
    SemanticAnalyzer().analyze(ast)
    generator = IntermediateCodeGenerator()
    generator.generate(ast)
    interpreter = Interpreter()
    interpreter.run(generator.code)
