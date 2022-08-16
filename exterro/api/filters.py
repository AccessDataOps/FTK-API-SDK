## /api/filters.py

"""
Utility module to aid in creating filter JSON objects for use within the
 AccessData API.
"""

from enum import IntEnum
from numbers import Number

## Declaring __all__

__all__ = (
	"generate_string_filter",
	"generate_number_filter",
	"StringOperator",
	"NumberOperator",
	"and_",
	"or_",
)

##

class StringOperator(IntEnum):
	EqualTo = 0
	NotEqualTo = 1
	Contains = 2
	StartsWith = 3
	EndsWith = 4

def generate_string_filter(attribute: str, operation: StringOperator,
		value: str) -> dict:
	return {
		"$type": "ADG.Service.Interfaces.DataContracts.Filtering.Grid." \
			"StringColumnFilter, ADG.Service.Interfaces",
		"staticAttributeName": attribute,
		"operator": operation.value,
		"operand": value
	}

## 

class NumberOperator(IntEnum):
	GreaterThan = 0
	GreaterThanEqualTo = 1
	LessThan = 2
	LessThanEqualTo = 3
	EqualTo = 4
	NotEqualTo = 5

	Includes = 6
	Excludes = 7

def generate_number_filter(attribute: str, operation: NumberOperator,
		value: Number) -> dict:
	if operation in (NumberOperator.Includes, NumberOperator.Excludes):
		return {
			"$type": "ADG.Service.Interfaces.DataContracts.Filtering.Grid." \
				"GridColumnFilter, ADG.Service.Interfaces",
			"staticAttributeName": attribute,
			"mode": operation.value - 6,
			"values": value
		}

	return {
		"$type": "ADG.Service.Interfaces.DataContracts.Filtering.Grid." \
			"GridColumnComparisonFilter, ADG.Service.Interfaces",
		"staticAttributeName": attribute,
		"operator": operation.value,
		"value": value
	}

##

def and_(filter1, filter2):
	return {
		"$type": "ADG.Service.Interfaces.DataContracts.Filtering." \
			"BinaryOperatorFilter, ADG.Service.Interfaces",
		"operator": "AND",
		"left": filter1,
		"right": filter2
	}

def or_(filter1, filter2):
	return {
		"$type": "ADG.Service.Interfaces.DataContracts.Filtering." \
			"BinaryOperatorFilter, ADG.Service.Interfaces",
		"operator": "OR",
		"left": filter1,
		"right": filter2
	}
