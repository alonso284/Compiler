from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Literal, TypeAlias


TypeName: TypeAlias = Literal["string", "int", "float", "bool", "char"]
UnaryOperator: TypeAlias = Literal["PLUS", "MINUS", "NOT"]
BinaryOperator: TypeAlias = Literal[
    "PLUS",
    "MINUS",
    "TIMES",
    "DIVIDE",
    "MOD",
    "AND",
    "OR",
    "EQ",
    "NE",
    "LE",
    "GE",
    "LT",
    "GT",
]


@dataclass
class TypeNode:
    name: TypeName


@dataclass
class ProgramNode:
    declarations: list[VarDeclNode]
    procedures: list[ProcedureNode]
    block: BlockNode


@dataclass
class VarDeclNode:
    # (name, optional_length). length is only used for arrays.
    names: list[tuple[str, Optional[int]]]
    var_type: TypeNode


@dataclass
class ProcedureNode:
    name: str
    block: BlockNode


@dataclass
class BlockNode:
    statements: list[Statement]


@dataclass
class AssignmentNode:
    variable: VariableNode
    expression: ExpressionNode


@dataclass
class WritelnNode:
    expression: ExpressionNode


@dataclass
class IncrementNode:
    variable: VariableNode


@dataclass
class DecrementNode:
    variable: VariableNode


@dataclass
class WhileNode:
    condition: ExpressionNode
    body: BlockNode


@dataclass
class ForNode:
    init: ActionNode
    condition: ExpressionNode
    update: ActionNode
    body: BlockNode


@dataclass
class IfNode:
    condition: ExpressionNode
    then_body: BlockNode
    else_body: Optional[BlockNode] = None


# ==========================
# EXPRESSIONS
# ==========================

@dataclass
class ExpressionNode:
    value: Expr


@dataclass
class BinaryOpNode:
    left: Expr
    operator: BinaryOperator
    right: Expr


@dataclass
class UnaryOpNode:
    operator: UnaryOperator
    operand: Expr


@dataclass
class VariableNode:
    name: str
    index: Optional[ExpressionNode] = None


@dataclass
class IntegerNode:
    value: int


@dataclass
class FloatNode:
    value: float


@dataclass
class StringNode:
    value: str


@dataclass
class CharNode:
    value: str


@dataclass
class BoolNode:
    value: bool


LiteralNode: TypeAlias = IntegerNode | FloatNode | StringNode | CharNode | BoolNode
Expr: TypeAlias = BinaryOpNode | UnaryOpNode | VariableNode | LiteralNode
ActionNode: TypeAlias = AssignmentNode | WritelnNode | IncrementNode | DecrementNode
Statement: TypeAlias = ActionNode | WhileNode | ForNode | IfNode