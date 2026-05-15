from lark import Transformer, Tree
from nodes_ast import *

# =========================================================
# AST BUILDER
# =========================================================

class ASTBuilder(Transformer):

    # =====================================================
    # PROGRAM
    # =====================================================

    def code(self, items):
        return ProgramNode(
            variables=self.declarations(items.children[0].children[3]),
            procedures=self.procedures(items.children[0].children[4]),
            block=self.block(items.children[0].children[5])
        )

    def declarations(self, items):
        declarations = [
            self.declaration(item)
            for item in items.children # declaration line
        ]
        # return flatten list of declarations
        return [decl for sublist in declarations for decl in sublist]

    def procedures(self, items):
        return [
            self.procedure(item)
            for item in items.children # procedure line
        ]

    # =====================================================
    # DECLARATIONS
    # =====================================================

    def declaration(self, items):
        var_type = items.children[-2].children[0].value
        
        return [
            VarDeclNode(
                name=child.children[0].value,
                var_type=var_type,
                length=len(child.children) > 2 and self.expression(child.children[2]) or None
            )
            for child in items.children
            if isinstance(child, Tree) and child.data.value == "name"
        ]

    def type(self, items):
        return str(items[0])

    def name(self, items):
        identifier = str(items.children[0])

        if len(items.children) > 1:
            return IdentifierNode(
                name=identifier,
                index=self.expression(items.children[2])
            )

        return IdentifierNode(identifier)

    # =====================================================
    # PROCEDURES
    # =====================================================

    def procedure(self, items):
        return ProcedureNode(
            name=str(items.children[1]),
            block=self.block(items.children[3])
        )

    # =====================================================
    # BLOCKS / STATEMENTS
    # =====================================================

    def block(self, items):
        return BlockNode(
            statements=self.statements(items.children[2])
        )

    def statements(self, items):
        return [
            self.statement(item)
            for item in items.children
        ]

    def statement(self, items):
        return \
            self.action(items.children[0].children[0]) if items.children[0].data == "action" else \
            self.procedure_call(items.children[0]) if items.children[0].data == "procedure_call" else \
            self.while_stmt(items.children[0]) if items.children[0].data == "while_stmt" else \
            self.for_stmt(items.children[0]) if items.children[0].data == "for_stmt" else \
            self.if_stmt(items.children[0]) if items.children[0].data == "if_stmt" else \
            StatementNode() # default case
            
    # =====================================================
    # ACTIONS
    # =====================================================

    def action(self, items):
        return self.assignment(items) if items.data == "assignment" else \
               self.writeln(items) if items.data == "writeln" else \
               self.increment(items) if items.data == "increment" else \
               self.decrement(items) if items.data == "decrement" else \
               StatementNode() # default case

    def assignment(self, items):
        return AssignmentNode(
            variable=self.name(items.children[0]),
            expression=self.expression(items.children[2])
        )

    def writeln(self, items):
        return WritelnNode(
            expression=self.expression(items.children[2])
        )

    def increment(self, items):
        return IncrementNode(
            variable=self.name(items.children[0])
        )

    def decrement(self, items):
        return DecrementNode(
            variable=self.name(items.children[0])
        )

    # =====================================================
    # CONTROL FLOW
    # =====================================================

    def while_stmt(self, items):
        return WhileNode(
            condition=self.expression(items.children[2]),
            body=BlockNode(items.children[6])
        )

    def for_stmt(self, items):
        return ForNode(
            init=self.action(items.children[2].children[0]),
            condition=self.expression(items.children[4]),
            update=self.action(items.children[6].children[0]),
            body=self.statements(items.children[9])
        )

    def if_stmt(self, items):
        return IfNode(
            condition=self.expression(items.children[2]),
            then_body=self.statements(items.children[6]),
            else_body=self.statements(items.children[10]) if len(items.children) > 8 else None
        )

    # =====================================================
    # PROCEDURE CALLS
    # =====================================================

    def procedure_call(self, items):
        return ProcedureCallNode(
            name=items.children[0],
        )

    # =====================================================
    # EXPRESSIONS
    # =====================================================

    def expression(self, items):
        return self.global_expression(items.children)

    def global_expression(self, items):
        return \
            self.boolean_expression(items[0].children) if len(items) == 1 else \
            BinaryOpNode(
                left=self.boolean_expression(items[0].children),
                operator=items[1],
                right=self.global_expression(items[2:])
            )

    def boolean_expression(self, items):
        return \
            self.addition_expression(items[0].children) if len(items) == 1 else \
            BinaryOpNode(
                left=self.addition_expression(items[0].children),
                operator=items[1],
                right=self.addition_expression(items[2].children)
            )

    def addition_expression(self, items):
        return \
            self.product_expression(items[0].children) if len(items) == 1 else \
            BinaryOpNode(
                left=self.product_expression(items[0].children),
                operator=items[1],
                right=self.addition_expression(items[2:])
            )

    def product_expression(self, items):
        return \
            self.value_expression(items[0].children) if len(items) == 1 else \
            BinaryOpNode(
                left=self.value_expression(items[0].children),
                operator=items[1],
                right=self.product_expression(items[2:])
            )

    def value_expression(self, items):
        if len(items) == 1:
            return items[0]
        operator = str(items[0])
        operand = items[1]

        return UnaryOpNode(
            operator=operator,
            operand=operand
        )

    # =====================================================
    # LITERALS
    # =====================================================

    def INTEGER(self, token):
        return IntegerNode(int(token))

    def FLOAT(self, token):
        return FloatNode(float(token))

    def STRING(self, token):
        return StringNode(str(token))

    def CHAR(self, token):
        return CharNode(str(token))

    def BOOL(self, token):
        value = str(token).lower() == "true"
        return BoolNode(value)

    def ID(self, token):
        return str(token)

# only run if programm is main
if __name__ == "__main__":
    simple_program = "tests/success/simple_program.k"

    from lark import Lark
    parser = Lark.open("parser.lark", parser="lalr")

    with open(simple_program, "r") as file:
        code = file.read()

    tree = parser.parse(code)
    ast = ASTBuilder().code(tree)

    # print(ast.variables)
    # print(ast.procedures[0].block)
    print(ast.block)
