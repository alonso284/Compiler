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
        try:
            tree = self.parser.parse(code)
            ast = self.ast_builder.transform(tree)
        except Exception as e:
            print(f"Error during parsing:\n  {e}")
            return

        try:
            self.semantic_analyzer.analyze(ast)
        except Exception as e:
            print(f"Error during semantic analysis:\n  {e}")
            return

        try:
            intermediate_code = self.code_generator.generate(ast)
        except Exception as e:
            print(f"Error during code generation:\n  {e}")
            return

        try:
            self.interpreter.run(intermediate_code)
        except Exception as e:
            print(f"Error during execution:\n  {e}")
            return

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