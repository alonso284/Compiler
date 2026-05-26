import argparse
from lark import Lark
from builder_ast import ASTBuilder
from semantic_analyzer import SemanticAnalyzer
from intermediate_code import IntermediateCodeGenerator
from interpreter import Interpreter

class Compiler:
    def __init__(self, verbose=False):
        self.parser = Lark.open("parser.lark", parser="lalr")
        self.ast_builder = ASTBuilder()
        self.semantic_analyzer = SemanticAnalyzer()
        self.code_generator = IntermediateCodeGenerator()
        self.interpreter = Interpreter(verbose=verbose)

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
    arg_parser = argparse.ArgumentParser(description="Compile and run a .k program")
    arg_parser.add_argument("file", help="Path to the source file to compile and run")
    arg_parser.add_argument("-v", "--verbose", action="store_true",
                            help="Print intermediate code instructions as they execute")
    args = arg_parser.parse_args()

    compiler = Compiler(verbose=args.verbose)
    with open(args.file, "r") as file:
        code = file.read()
    compiler.compile_and_run(code)