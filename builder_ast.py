from lark import Transformer, Token

from ast_nodes import *

class ASTBuilder(Transformer):

    # ==========================
    # TOKENS
    # ==========================

    def ID(self, token: Token):
        return str(token)

    def INTEGER(self, token: Token):
        return IntegerNode(int(token))

    def FLOAT_NUMBER(self, token: Token):
        return FloatNode(float(token))

    def STRING_LITERAL(self, token: Token):
        return StringNode(str(token)[1:-1])

    # ==========================
    # PROGRAM
    # ==========================

    def program(self, items):
        declarations = items[0]
        procedures = items[1]
        block = items[2]

        return ProgramNode(
            declarations=declarations,
            procedures=procedures,
            block=block,
        )

    def declarations(self, items):
        return items

    def procedures(self, items):
        return items

    # ==========================
    # DECLARATIONS
    # ==========================

    def type(self, items):
        token = items[0]

        return TypeNode(token.lower())

    def declaration(self, items):
        *names, var_type = items

        return VarDeclNode(
            names=names,
            var_type=var_type,
        )

    def name(self, items):
        if len(items) == 1:
            return (items[0], None)

        return (items[0], int(items[1]))

    # ==========================
    # PROCEDURES
    # ==========================

    def procedure(self, items):
        return ProcedureNode(
            name=items[0],
            block=items[1],
        )

    # ==========================
    # BLOCK
    # ==========================

    def block(self, items):
        return BlockNode(statements=items[0])

    def statements(self, items):
        return items