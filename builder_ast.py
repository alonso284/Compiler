from lark import Token, Transformer
from nodes_ast import *

# =========================================================
# AST BUILDER
# =========================================================

class ASTBuilder(Transformer):

    _NOISE_TOKENS = {
        "PROGRAM", "MAIN", "VAR", "PROCEDURE", "BEGIN", "END", "WHILE", "DO", "FOR", "IF", "THEN", "ELSE", "WRITE",
        "LBRACE", "RBRACE", "LPAREN", "RPAREN", "LBRACKET", "RBRACKET", "COLON", "SEMICOLON", "COMMA",
    }

    _UNARY_OP_TOKENS = {"PLUS", "MINUS", "NOT"}

    @staticmethod
    def _is_token(value, token_type=None):
        if not isinstance(value, Token):
            return False
        return token_type is None or value.type == token_type

    @staticmethod
    def _fold_left(items):
        node = items[0]
        for i in range(1, len(items), 2):
            node = BinaryOpNode(
                left=node,
                operator=str(items[i]),
                right=items[i + 1],
            )
        return node

    # =====================================================
    # PROGRAM
    # =====================================================

    def start(self, items):
        return items[0]

    def code(self, items):
        declarations = []
        procedures = []

        for item in items:
            if not isinstance(item, list):
                continue
            if item and isinstance(item[0], VarDeclNode):
                declarations = item
            elif item and isinstance(item[0], ProcedureNode):
                procedures = item

        block = next(item for item in items if isinstance(item, BlockNode))

        return ProgramNode(
            variables=declarations,
            procedures=procedures,
            block=block,
        )

    def declarations(self, items):
        return [decl for group in items for decl in group]

    def procedures(self, items):
        return items

    # =====================================================
    # DECLARATIONS
    # =====================================================

    def declaration(self, items):
        var_type = next(
            (item for item in items if isinstance(item, str) and not isinstance(item, Token)),
            "",
        )
        identifiers = [item for item in items if isinstance(item, IdentifierNode)]

        return [
            VarDeclNode(
                name=identifier.name,
                var_type=var_type
            )
            for identifier in identifiers
        ]

    def type(self, items):
        return str(items[0])

    def name(self, items):
        identifier = str(items[0])
        return IdentifierNode(name=identifier)

    # =====================================================
    # PROCEDURES
    # =====================================================

    def procedure(self, items):
        name = next(item for item in items if isinstance(item, str))
        block = next(item for item in items if isinstance(item, BlockNode))

        return ProcedureNode(
            name=name,
            block=block,
        )

    # =====================================================
    # BLOCKS / STATEMENTS
    # =====================================================

    def block(self, items):
        statements = next((item for item in items if isinstance(item, list)), [])
        return BlockNode(statements=statements)

    def statements(self, items):
        return items

    def statement(self, items):
        return next((item for item in items if isinstance(item, StatementNode)), StatementNode())
            
    # =====================================================
    # ACTIONS
    # =====================================================

    def action(self, items):
        return next((item for item in items if isinstance(item, StatementNode)), StatementNode())

    def assignment(self, items):
        variable = next(item for item in items if isinstance(item, IdentifierNode))
        expression = next(item for item in reversed(items) if isinstance(item, ExpressionNode))

        return AssignmentNode(
            variable=variable,
            expression=expression,
        )

    def write(self, items):
        expression = next(item for item in items if isinstance(item, ExpressionNode))

        return WriteNode(
            expression=expression,
        )

    def increment(self, items):
        variable = next(item for item in items if isinstance(item, IdentifierNode))

        return IncrementNode(
            variable=variable,
        )

    def decrement(self, items):
        variable = next(item for item in items if isinstance(item, IdentifierNode))

        return DecrementNode(
            variable=variable,
        )

    # =====================================================
    # CONTROL FLOW
    # =====================================================

    def while_stmt(self, items):
        condition = next(item for item in items if isinstance(item, ExpressionNode))
        body_statements = next((item for item in items if isinstance(item, list)), [])

        return WhileNode(
            condition=condition,
            body=BlockNode(body_statements),
        )

    def for_stmt(self, items):
        actions = [item for item in items if isinstance(item, StatementNode)]
        condition = next(item for item in items if isinstance(item, ExpressionNode))
        body_statements = next((item for item in items if isinstance(item, list)), [])

        return ForNode(
            init=actions[0],
            condition=condition,
            update=actions[1],
            body=BlockNode(body_statements),
        )

    def if_stmt(self, items):
        condition = next(item for item in items if isinstance(item, ExpressionNode))
        blocks = [item for item in items if isinstance(item, list)]

        return IfNode(
            condition=condition,
            then_body=BlockNode(blocks[0]) if blocks else BlockNode([]),
            else_body=BlockNode(blocks[1]) if len(blocks) > 1 else None,
        )

    # =====================================================
    # PROCEDURE CALLS
    # =====================================================

    def procedure_call(self, items):
        name = next(item for item in items if isinstance(item, str))

        return ProcedureCallNode(
            name=name,
        )

    # =====================================================
    # EXPRESSIONS
    # =====================================================

    def expression(self, items):
        return self._fold_left(items) if len(items) > 1 else items[0]

    def boolean_expression(self, items):
        return self._fold_left(items) if len(items) > 1 else items[0]

    def addition_expression(self, items):
        return self._fold_left(items) if len(items) > 1 else items[0]

    def product_expression(self, items):
        return self._fold_left(items) if len(items) > 1 else items[0]

    def value_expression(self, items):
        filtered = [
            item for item in items
            if not (self._is_token(item) and item.type in self._NOISE_TOKENS)
        ]

        if len(filtered) == 1:
            return filtered[0]

        if self._is_token(filtered[0]) and filtered[0].type in self._UNARY_OP_TOKENS:
            return UnaryOpNode(
                operator=str(filtered[0]),
                operand=filtered[1],
            )

        return filtered[0]

    # =====================================================
    # LITERALS
    # =====================================================

    def CTE(self, token):
        text = str(token)

        if text.lower() in {"true", "false"}:
            return BoolNode(text.lower() == "true")
        if text.startswith('"') and text.endswith('"'):
            return StringNode(text[1:-1])
        if text.startswith("'") and text.endswith("'"):
            return CharNode(text[1:-1])
        if "." in text:
            return FloatNode(float(text))
        return IntegerNode(int(text))

    def INTEGER(self, token):
        return IntegerNode(int(token))

    def FLOAT_NUM(self, token):
        return FloatNode(float(token))

    def STRING_VALUE(self, token):
        text = str(token)
        return StringNode(text[1:-1])

    def CHAR_VALUE(self, token):
        text = str(token)
        return CharNode(text[1:-1])

    def TRUE(self, token):
        return BoolNode(True)

    def FALSE(self, token):
        return BoolNode(False)

    def BOOL(self, token):
        return str(token)

    def ID(self, token):
        return IdentifierNode(name=str(token))

# only run if programm is main
if __name__ == "__main__":
    simple_program = "tests/success/simple_program.k"

    from lark import Lark
    parser = Lark.open("parser.lark", parser="lalr")

    with open(simple_program, "r") as file:
        code = file.read()

    tree = parser.parse(code)
    ast = ASTBuilder().transform(tree)

    print(ast.variables)
    print(ast.procedures)
    print(ast.block)
