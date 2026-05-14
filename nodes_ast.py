from dataclasses import dataclass

@dataclass
class ProgramNode:
    declarations: List[Any]
    procedures: List[Any]
    block: Any


@dataclass
class VarDeclNode:
    name: str
    var_type: str


@dataclass
class ProcedureNode:
    name: str
    block: Any


@dataclass
class BlockNode:
    statements: List[Any]


@dataclass
class AssignmentNode:
    variable: Any
    expression: Any


@dataclass
class WritelnNode:
    expression: Any


@dataclass
class IncrementNode:
    name: str


@dataclass
class DecrementNode:
    name: str


@dataclass
class WhileNode:
    condition: Any
    body: List[Any]


@dataclass
class ForNode:
    init: Any
    condition: Any
    update: Any
    body: List[Any]


@dataclass
class IfNode:
    condition: Any
    then_body: List[Any]
    else_body: Optional[List[Any]] = None


# ==========================
# EXPRESSIONS
# ==========================

@dataclass
class BinaryOpNode:
    left: Any
    operator: str
    right: Any


@dataclass
class UnaryOpNode:
    operator: str
    value: Any


@dataclass
class VariableNode:
    name: str
    index: Optional[Any] = None


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