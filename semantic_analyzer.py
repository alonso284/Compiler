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
    ProcedureCallNode,
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
    scope: str = "global"


@dataclass
class ProcedureInfo:
    name: str


class SemanticAnalyzer:
    def __init__(self) -> None:
        self.symbol_table: dict[str, SymbolInfo] = {}
        self.procedure_table: dict[str, ProcedureInfo] = {}

    def analyze(self, program: ProgramNode) -> None:
        self.symbol_table.clear()
        self.procedure_table.clear()

        self._collect_global_variables(program)
        self._collect_procedures(program)

        for procedure in program.procedures:
            self._analyze_block(procedure.block)

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

    def _collect_procedures(self, program: ProgramNode) -> None:
        for procedure in program.procedures:
            if procedure.name in self.procedure_table:
                raise SemanticError(
                    f"Duplicate procedure declaration: '{procedure.name}'"
                )
            if procedure.name in self.symbol_table:
                raise SemanticError(
                    f"Procedure '{procedure.name}' conflicts with a global variable name"
                )

            self.procedure_table[procedure.name] = ProcedureInfo(name=procedure.name)

    def _analyze_block(self, block: BlockNode) -> None:
        for statement in block.statements:
            self._analyze_statement(statement)

    def _analyze_statement(self, statement: StatementNode) -> None:
        if isinstance(statement, AssignmentNode):
            variable_type = self._get_identifier_type(statement.variable)
            expression_type = self._infer_expression_type(statement.expression)

            if variable_type != expression_type:
                raise SemanticError(
                    f"Cannot assign '{expression_type}' to variable '{statement.variable.name}' "
                    f"of type '{variable_type}'"
                )
            return

        if isinstance(statement, WriteNode):
            self._infer_expression_type(statement.expression)
            return

        if isinstance(statement, IncrementNode):
            variable_type = self._get_identifier_type(statement.variable)
            if variable_type != "int":
                raise SemanticError(
                    f"Increment requires 'int' variable, got '{variable_type}' "
                    f"for '{statement.variable.name}'"
                )
            return

        if isinstance(statement, DecrementNode):
            variable_type = self._get_identifier_type(statement.variable)
            if variable_type != "int":
                raise SemanticError(
                    f"Decrement requires 'int' variable, got '{variable_type}' "
                    f"for '{statement.variable.name}'"
                )
            return

        if isinstance(statement, ProcedureCallNode):
            if statement.name not in self.procedure_table:
                raise SemanticError(f"Undeclared procedure: '{statement.name}'")
            return

        if isinstance(statement, WhileNode):
            condition_type = self._infer_expression_type(statement.condition)
            if condition_type != "bool":
                raise SemanticError(
                    f"While condition must be 'bool', got '{condition_type}'"
                )
            self._analyze_block(statement.body)
            return

        if isinstance(statement, ForNode):
            self._analyze_statement(statement.init)

            condition_type = self._infer_expression_type(statement.condition)
            if condition_type != "bool":
                raise SemanticError(f"For condition must be 'bool', got '{condition_type}'")

            self._analyze_statement(statement.update)
            self._analyze_block(statement.body)
            return

        if isinstance(statement, IfNode):
            condition_type = self._infer_expression_type(statement.condition)
            if condition_type != "bool":
                raise SemanticError(f"If condition must be 'bool', got '{condition_type}'")

            self._analyze_block(statement.then_body)
            if statement.else_body is not None:
                self._analyze_block(statement.else_body)
            return

    def _get_identifier_type(self, identifier: IdentifierNode) -> str:
        symbol = self.symbol_table.get(identifier.name)
        if symbol is None:
            raise SemanticError(f"Undeclared variable: '{identifier.name}'")
        return symbol.symbol_type

    def _infer_expression_type(self, expression: ExpressionNode) -> str:
        if isinstance(expression, IdentifierNode):
            return self._get_identifier_type(expression)

        if isinstance(expression, IntegerNode):
            return "int"
        if isinstance(expression, FloatNode):
            return "float"
        if isinstance(expression, StringNode):
            return "string"
        if isinstance(expression, CharNode):
            return "char"
        if isinstance(expression, BoolNode):
            return "bool"

        if isinstance(expression, UnaryOpNode):
            operand_type = self._infer_expression_type(expression.operand)
            operator = self._normalize_operator(expression.operator)

            if operator == "not":
                if operand_type != "bool":
                    raise SemanticError(
                        f"Unary 'not' requires 'bool', got '{operand_type}'"
                    )
                return "bool"

            if operator in {"+", "-"}:
                if operand_type not in {"int", "float"}:
                    raise SemanticError(
                        f"Unary '{operator}' requires numeric type, got '{operand_type}'"
                    )
                return operand_type

            raise SemanticError(f"Unsupported unary operator: '{expression.operator}'")

        if isinstance(expression, BinaryOpNode):
            left_type = self._infer_expression_type(expression.left)
            right_type = self._infer_expression_type(expression.right)
            operator = self._normalize_operator(expression.operator)

            if operator in {"and", "or"}:
                if left_type != "bool" or right_type != "bool":
                    raise SemanticError(
                        f"Logical operator '{operator}' requires 'bool' operands, "
                        f"got '{left_type}' and '{right_type}'"
                    )
                return "bool"

            if operator in {"+", "-", "*", "/", "%"}:
                if left_type != right_type:
                    raise SemanticError(
                        f"Arithmetic operator '{operator}' requires matching operand types, "
                        f"got '{left_type}' and '{right_type}'"
                    )

                if left_type not in {"int", "float", "string"}:
                    raise SemanticError(
                        f"Arithmetic operator '{operator}' not supported for type '{left_type}'"
                    )

                if operator != "+" and left_type == "string":
                    raise SemanticError(
                        f"Operator '{operator}' not supported for type 'string'"
                    )

                return left_type

            if operator in {"==", "!="}:
                if left_type != right_type:
                    raise SemanticError(
                        f"Comparison operator '{operator}' requires matching operand types, "
                        f"got '{left_type}' and '{right_type}'"
                    )
                return "bool"

            if operator in {"<", "<=", ">", ">="}:
                if left_type != right_type:
                    raise SemanticError(
                        f"Comparison operator '{operator}' requires matching operand types, "
                        f"got '{left_type}' and '{right_type}'"
                    )

                if left_type not in {"int", "float", "char", "string"}:
                    raise SemanticError(
                        f"Comparison operator '{operator}' not supported for type '{left_type}'"
                    )

                return "bool"

            raise SemanticError(f"Unsupported binary operator: '{expression.operator}'")

        raise SemanticError(f"Unsupported expression node: '{type(expression).__name__}'")

    @staticmethod
    def _normalize_operator(operator: str) -> str:
        normalized = operator.strip().lower()

        mapping = {
            "&&": "and",
            "||": "or",
            "!": "not",
        }
        return mapping.get(normalized, normalized)
