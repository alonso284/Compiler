from dataclasses import dataclass
from typing import Optional

# =========================================================
# PROGRAM
# =========================================================

@dataclass
class ProgramNode:
    variables: list[VarDeclNode]
    procedures: list[ProcedureNode]
    block: BlockNode

@dataclass
class VarDeclNode:
    name: str 
    var_type: str

@dataclass
class ProcedureNode:
    name: str
    block: BlockNode

# =========================================================
# STATEMENTS
# =========================================================

@dataclass
class StatementNode:
    pass

@dataclass
class BlockNode:
    statements: list[StatementNode]

@dataclass
class AssignmentNode(StatementNode):
    variable: IdentifierNode
    expression: ExpressionNode

@dataclass
class WriteNode(StatementNode):
    expression: ExpressionNode

@dataclass
class IncrementNode(StatementNode):
    variable: IdentifierNode

@dataclass
class DecrementNode(StatementNode):
    variable: IdentifierNode

@dataclass
class WhileNode(StatementNode):
    condition: ExpressionNode
    body: BlockNode

@dataclass
class ForNode(StatementNode):
    init: StatementNode
    condition: ExpressionNode
    update: StatementNode
    body: BlockNode

@dataclass
class IfNode(StatementNode):
    condition: ExpressionNode
    then_body: BlockNode
    else_body: Optional[BlockNode] = None

@dataclass
class ProcedureCallNode(StatementNode):
    name: str

# =========================================================
# EXPRESSIONS
# =========================================================

@dataclass
class ExpressionNode:
    pass

@dataclass
class BinaryOpNode(ExpressionNode):
    left: ExpressionNode
    operator: str
    right: ExpressionNode

@dataclass
class UnaryOpNode(ExpressionNode):
    operator: str
    operand: ExpressionNode

@dataclass
class IdentifierNode(ExpressionNode):
    name: str

# =========================================================
# LITERALS
# =========================================================

@dataclass
class LiteralNode(ExpressionNode):
    value: object

@dataclass
class IntegerNode(LiteralNode):
    value: int

@dataclass
class FloatNode(LiteralNode):
    value: float

@dataclass
class StringNode(LiteralNode):
    value: str

@dataclass
class CharNode(LiteralNode):
    value: str

@dataclass
class BoolNode(LiteralNode):
    value: bool