from lark import Lark
from builder_ast import ASTBuilder
from semantic_analyzer import SemanticAnalyzer
from intermediate_code import IntermediateCodeGenerator
from interpreter import Interpreter

class Compiler:
    def __init__(self):
        self.parser = Lark.open("parser.lark", parser="lalr")
        self.ast_builder = ASTBuilder()
        self.semantic_analyzer = SemanticAnalyzer()
        self.code_generator = IntermediateCodeGenerator()
        self.interpreter = Interpreter()

    def compile_and_run(self, code):
        # Parse the code and build the AST
        tree = self.parser.parse(code)
        ast = self.ast_builder.transform(tree)

        # Perform semantic analysis
        self.semantic_analyzer.analyze(ast)

        # Generate intermediate code
        intermediate_code = self.code_generator.generate(ast)

        # Run the intermediate code
        self.interpreter.run(intermediate_code)

if __name__ == "__main__":
    compiler = Compiler()
    with open("tests/success/simple_program.k", "r") as file:
        code = file.read()
    compiler.compile_and_run(code)