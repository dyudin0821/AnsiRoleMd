#!/usr/bin/env python3
from ansirolemd.exception import AnsiRoleMdException


class TableMarkdown:
    __headers: list = None
    __matrix: list = None

    def __init__(self, headers: list, matrix: list) -> None:
        self.__headers = headers
        self.__matrix = matrix

    def get_headers(self) -> list:
        """return a list of headers"""
        return self.__headers

    def get_separators(self) -> list:
        """return a list of separators"""
        values = []
        for column in self.__headers:
            align = getattr(column, "align", "left")
            value = dict(left="-", center=":-:", right="-:").get(align, "-")
            values.append(value)
        return values

    def get_matrix(self) -> list:
        """return a table with data"""
        return self.__matrix

    def render(self):
        """return a string with markdown table (if data not empty)"""
        matrix = self.get_matrix()
        if not matrix:
            raise AnsiRoleMdException("The table vars is null or empty!")
        lines = [
            "|".join(self.get_headers()),
            "|".join(self.get_separators()),
        ] + list(map(lambda r: " |".join(r), self.get_matrix()))
        return "\n".join(lines)

    def __bool__(self):
        return len(self.get_matrix()) > 0

    def __nonzero__(self):
        return self.__bool__()

    def __str__(self):
        return self.render()

    def __repr__(self):
        return self.__str__()
