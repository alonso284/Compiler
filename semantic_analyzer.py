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
    PostfixOpNode,
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


class SemanticCube:
    _NUMERIC_TYPES = {"int", "float"}
    _CHAR_STRING_TYPES = {"char", "string"}
    _BOOLEAN_TYPES = {"bool"}

    _ASSIGNMENT_PAIRS = {
        ("int", "int"),
        ("float", "float"),
        ("int", "float"),
        ("float", "int"),
        ("string", "string"),
        ("char", "char"),
        ("string", "char"),
        ("bool", "bool"),
    }

    _ARITHMETIC_TABLE = {
        "+": {
            ("int", "int"): "int",
            ("int", "float"): "float",
            ("float", "int"): "float",
            ("float", "float"): "float",
        },
        "-": {
            ("int", "int"): "int",
            ("int", "float"): "float",
            ("float", "int"): "float",
            ("float", "float"): "float",
        },
        "*": {
            ("int", "int"): "int",
            ("int", "float"): "float",
            ("float", "int"): "float",
            ("float", "float"): "float",
        },
        "/": {
            ("int", "int"): "float",
            ("int", "float"): "float",
            ("float", "int"): "float",
            ("float", "float"): "float",
        },
        "%": {
            ("int", "int"): "int",
        },
    }

    _RELATIONAL_PAIRS = {
        ("int", "int"),
        ("int", "float"),
        ("float", "int"),
        ("float", "float"),
        ("char", "char"),
        ("char", "string"),
        ("string", "char"),
        ("string", "string"),
        ("bool", "bool"),
    }

    @staticmethod
    def get_arithmetic_result(left_type: str, right_type: str, operator: str) -> str:
        table = SemanticCube._ARITHMETIC_TABLE.get(operator)
        if table is None:
            raise SemanticError(f"Unsupported arithmetic operator: '{operator}'")

        key = (left_type, right_type)
        if key not in table:
            raise SemanticError(
                f"Arithmetic operator '{operator}' not supported between '{left_type}' and '{right_type}'"
            )

        return table[key]

    @staticmethod
    def can_compare(left_type: str, right_type: str) -> bool:
        return (left_type, right_type) in SemanticCube._RELATIONAL_PAIRS

    @staticmethod
    def can_assign(left_type: str, right_type: str) -> bool:
        return (left_type, right_type) in SemanticCube._ASSIGNMENT_PAIRS


class SemanticAnalyzer:
    def __init__(self) -> None:
        self.symbol_table: dict[str, SymbolInfo] = {}
        self.function_table: dict[str, FunctionInfo] = {}
        self.cube = SemanticCube()

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
            variable_type = self._get_identifier_type(statement.variable)
            expression_type = self._infer_expression_type(statement.expression)
            if not self.cube.can_assign(variable_type, expression_type):
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

        if isinstance(statement, FunctionCallNode):
            if statement.name not in self.function_table:
                raise SemanticError(f"Undeclared function: '{statement.name}'")
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

        if isinstance(expression, BoolNode):
            return "bool"

        if isinstance(expression, CharNode):
            return "char"

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

        if isinstance(expression, PostfixOpNode):
            var_type = self._get_identifier_type(expression.variable)
            if var_type != "int":
                raise SemanticError(
                    f"Postfix '{expression.operator}' requires 'int' variable, got '{var_type}' "
                    f"for '{expression.variable.name}'"
                )
            return "int"

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
                return self.cube.get_arithmetic_result(left_type, right_type, operator)

            if operator in {"==", "!=", "<", "<=", ">", ">="}:
                if not self.cube.can_compare(left_type, right_type):
                    raise SemanticError(
                        f"Comparison operator '{operator}' not supported between '{left_type}' and '{right_type}'"
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

