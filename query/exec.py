def exec_bool_unary_operator(operator, right):
    """
    Execute a boolean unary operator.
    """
    # print("#### exec_bool_unary_operator", operator, right)
    if operator == "not":
        return not right
    else:
        raise ValueError(f"Unknown bool_unary_operator {operator}")


def exec_bool_binary_operator(operator, left, right):
    """
    Execute a boolean binary operator.
    """
    # print("#### exec_bool_binary_operator", operator, left, right)
    operator = operator.lower()
    if operator == "and" or operator == "&&":
        return left and right
    elif operator == "or" or operator == "||":
        return left or right
    elif operator == "not" or operator == "!":
        return not right
    else:
        raise ValueError(f"Unknown bool_binary_operator {operator}")


def exec_cmp_operator(operator, left, right):
    """
    Execute a comparison operator.
    """
    # print("#### exec_cmp_operator", operator, left, right)
    if operator == "==":
        return left == right
    elif operator == "!=":
        return left != right
    elif operator == "<":
        return left < right
    elif operator == "<=":
        return left <= right
    elif operator == ">":
        return left > right
    elif operator == ">=":
        return left >= right
    else:
        raise ValueError(f"Unknown operator {operator}")
