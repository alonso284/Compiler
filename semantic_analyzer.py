from __future__ import annotations

from dataclasses import dataclass

from nodes_ast import (
    AssignmentNode,
    BinaryOpNode,
    BlockNode,
    BoolNode,
    CharNode,
    DecrementNode,
    ExpressionNode,
    FloatNode,
    ForNode,
    IdentifierNode,
    IfNode,
    IncrementNode,
    IntegerNode,
    FunctionCallNode,
    ProgramNode,
    StatementNode,
    StringNode,
    UnaryOpNode,
    WhileNode,
    WriteNode,
)


class SemanticError(Exception):
    pass


@dataclass
class SymbolInfo:
    name: str
    symbol_type: str
    kind: str = "variable"

@dataclass
class FunctionInfo:
    name: str

class SemanticAnalyzer:
    def __init__(self) -> None:
        self.symbol_table: dict[str, SymbolInfo] = {}
        self.function_table: dict[str, FunctionInfo] = {}

    def analyze(self, program: ProgramNode) -> None:
        self.symbol_table.clear()
        self.function_table.clear()

        self._collect_global_variables(program)
        self._collect_functions(program)

        for function in program.functions:
            self._analyze_block(function.block)

        self._analyze_block(program.block)

    def _collect_global_variables(self, program: ProgramNode) -> None:
        for declaration in program.variables:
            if declaration.name in self.symbol_table:
                raise SemanticError(
                    f"Duplicate global variable declaration: '{declaration.name}'"
                )

            self.symbol_table[declaration.name] = SymbolInfo(
                name=declaration.name,
                symbol_type=declaration.var_type,
            )

    def _collect_functions(self, program: ProgramNode) -> None:
        for function in program.functions:
            if function.name in self.function_table:
                raise SemanticError(
                    f"Duplicate function declaration: '{function.name}'"
                )
            if function.name in self.symbol_table:
                raise SemanticError(
                    f"Function '{function.name}' conflicts with a global variable name"
                )

            self.function_table[function.name] = FunctionInfo(name=function.name)

    def _analyze_block(self, block: BlockNode) -> None:
        for statement in block.statements:
            self._analyze_statement(statement)

    def _analyze_statement(self, statement: StatementNode) -> None:
        if isinstance(statement, AssignmentNode):
            return

        if isinstance(statement, WriteNode):
            return

        if isinstance(statement, IncrementNode):
            return

        if isinstance(statement, DecrementNode):
            return

        if isinstance(statement, FunctionCallNode):
            return

        if isinstance(statement, WhileNode):
            return

        if isinstance(statement, ForNode):
            return

        if isinstance(statement, IfNode):
            return

