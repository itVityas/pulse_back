from enum import Enum


class FilterOperators(str, Enum):
    EQ = "eq"                       # равно
    NE = "ne"                       # не равно
    GT = "gt"                       # больше
    GTE = "gte"                     # больше или равно
    LT = "lt"                       # меньше
    LTE = "lte"                     # меньше или равно
    ICONTAINS = "icontains"         # содержит (регистронезависимый)
    ISTARTSWITH = "istartswith"       # начинается с
    IENDSWITH = "iendswith"           # заканчивается на
    IS_NULL = "is_null"             # is null
    IS_NOT_NULL = "is_not_null"     # is not null
