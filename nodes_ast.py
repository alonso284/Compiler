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