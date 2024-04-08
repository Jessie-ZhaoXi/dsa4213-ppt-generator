import re
from typing import List, Optional

"""
This code is a simple Markdown parser that is used to parse Markdown formatted text and build the corresponding data structure. It includes the following classes and functions:

    Element class: Represents an element in the parser. It has the following attributes and methods:
    
        source: The original text content of the element.
        children: A list of child elements.
        full_source: Returns the full source of the element, including its children.
        add_child(el): Adds a child element to the current element.
        add_source(source): Adds the source text to the current element.
        
    Out class (inherits from Element class): Represents the top-level element of the Markdown parser. It has the following attributes and methods:

        main: The main heading element.
        level: The current level of headings being parsed.
        title: Returns the text content of the main heading.
        full_source: Returns the full source of the Out element, including its source and children.
        
    Heading class (inherits from Element class): Represents a heading element in the Markdown parser. It has the following attributes and methods:

        parent: Points to the parent element.
        level: The level of the heading.
        text: The text content of the heading.
        text_source: The source text of the heading.
        full_source: Returns the full source of the Heading element, including its source and children.
        
    Parser class: Markdown parser class responsible for parsing Markdown text and building the parse result. It has the following attributes and methods:

        DEBUG: Debug level.
        parse(text): Parses the Markdown text and returns the parse result.
        _parse_heading_var_one(level, string, next_string): Helper method to parse the first type of heading format.
        _parse_heading_var_two(level, string): Helper method to parse the second type of heading format.
        _parse_heading_action(level, text, text_source): Handles the parsed heading element.
"""


class Element:
    """
    Represents an element in the parser.

    Attributes:
        source (str): The original text content of the element.
        children (List[Element]): A list of child elements.
    """

    def __init__(self) -> None:
        self.source: Optional[str] = None
        self.children: List[Element] = []

    @property
    def full_source(self) -> str:
        """
        Returns the full source of the element, including its children.
        """
        if len(self.children) == 0:
            return ""
        return "\n" + "\n".join([x.full_source for x in self.children])

    def add_child(self, el: "Element") -> None:
        """
        Adds a child element to the current element.
        """
        self.children.append(el)

    def add_source(self, source: str) -> None:
        """
        Adds the source text to the current element.
        """
        if self.source is None:
            self.source = source
        else:
            self.source += "\n" + source

    def __getitem__(self, item: int) -> "Element":
        """
        Returns the child element at the specified index.
        """
        return self.children[item]

    def __len__(self) -> int:
        """
        Returns the number of child elements.
        """
        return len(self.children)


class Out(Element):
    """
    Represents the top-level element of the Markdown parser.
    """

    main: Optional["Heading"] = None
    level: int = 0

    @property
    def title(self) -> Optional[str]:
        """
        Returns the title of the main heading.
        """
        if self.main is not None:
            return self.main.text

    @property
    def full_source(self) -> str:
        """
        Returns the full source of the Out element, including its source and children.
        """
        result = ""
        if self.source is not None:
            result += f"{self.source}\n"
        result += self.main.full_source
        result += super().full_source
        return result

    def __str__(self) -> str:
        return "Out"


class Heading(Element):
    """
    Represents a heading element in the Markdown parser.
    """

    def __init__(
        self,
        parent: Optional["Heading"],
        level: int,
        text: str,
        text_source: str,
    ):
        super().__init__()
        self.parent = parent
        self.level = level
        self._text = text
        self._text_source = text_source

    @property
    def text(self) -> str:
        """
        Returns the text content of the heading.
        """
        return self._text

    @text.setter
    def text(self, value: str) -> None:
        """
        Sets the text content of the heading.
        """
        self._text_source = self._text_source.replace(self._text, value)
        self._text = value

    @property
    def text_source(self) -> str:
        """
        Returns the source text of the heading.
        """
        return self._text_source

    @property
    def full_source(self) -> str:
        """
        Returns the full source of the Heading element, including its source and children.
        """
        result = f"{self._text_source}"
        if self.source is not None:
            result += f"\n{self.source}"
        result += super().full_source
        return result

    def __str__(self) -> str:
        return self._text


class Parser:
    """
    Markdown parser class responsible for parsing Markdown text and building the parse result.
    """

    def __init__(self, debug_level: int = 0):
        self.DEBUG = debug_level

    def parse(self, text: str) -> Out:
        """
        Parses the Markdown text and returns the parse result.
        """
        self.out = Out()
        self.current = None
        jump_to_next = False
        code_block = False
        strings = text.split("\n")
        len_strs = len(strings)
        for index in range(len_strs):
            if jump_to_next:
                jump_to_next = False
                continue
            string = strings[index]
            is_heading = False

            # match code block: a line that starts with optional \s followed by (```)
            if re.search(r"^\s*```.*$", string) is not None:
                code_block = not code_block

            """ Search and parse headings """
            if not code_block:
                next_string = strings[index + 1] if index + 1 < len_strs else None
                for level in range(1, 3):
                    is_heading = self._parse_heading_var_one(level, string, next_string)
                    if is_heading:
                        break
                if is_heading:
                    jump_to_next = True
                    continue
                for level in range(1, 7):
                    is_heading = self._parse_heading_var_two(level, string)
                    if is_heading:
                        break

            if not is_heading:
                if self.current is None:
                    self.out.add_source(string)
                else:
                    self.current.add_source(string)

        return self.out

    def _parse_heading_var_one(
        self, level: int, string: str, next_string: Optional[str]
    ) -> bool:
        """
        Helper method to parse the first type of heading format.
        """
        # matches any string that contains only whitespace characters or is empty
        if next_string is None or re.search(r"^\s*$", string) is not None:
            return False

        if self.DEBUG >= 2:
            print(
                f'- parse_heading_var_one with level: {level}, next_string: "{next_string}"'
            )

        if level == 1:
            tmpl = "="
        elif level == 2:
            tmpl = "-"
        else:
            raise Exception(f"Not support level: {level}")

        regex = (
            "^\s?%s{3,}\s*$" % tmpl
        )  # matches the template character (= or -) repeated 3 or more times.
        result = re.search(regex, next_string)
        if result is None:
            return False

        return self._parse_heading_action(
            level=level, text=string.strip(), text_source=f"{string}\n{next_string}"
        )

    def _parse_heading_var_two(self, level: int, string: str) -> bool:
        """
        Helper method to parse the second type of heading format.
        matches an optional whitespace character (\s?), followed by the # character,
        followed by the value of the level variable, and then followed by one or more whitespace characters (\s+).
        (.*) is another capturing group that matches any character (.) zero or more times (*).
        """
        if self.DEBUG >= 2:
            print(f'- parse_heading_var_two with level: {level}, string: "{string}"')

        regex = "^(\s?#{%s}\s+)(.*)$" % level
        result = re.search(regex, string)
        if result is None:
            return False

        return self._parse_heading_action(
            level=level, text=result[2], text_source=result[1] + result[2]
        )

    def _parse_heading_action(self, level: int, text: str, text_source: str) -> bool:
        """
        Handles the parsed heading element.
        """
        if self.current is None:
            parent = self.out
        elif level > self.current.level:
            parent = self.current
        else:
            parent = self.current.parent
            while parent.level >= level:
                parent = parent.parent

        self.current = Heading(parent, level, text, text_source)

        if level == 1 and self.out.main is None:
            self.out.main = self.current
        else:
            parent.add_child(self.current)

        if self.DEBUG >= 1:
            spaces = (
                "  ".join(["" for _ in range(parent.level + 1)])
                if parent != self.out
                else ""
            )
            print(f"{spaces}<{str(parent)}>")
            spaces = "  ".join(["" for _ in range(self.current.level + 1)])
            print(f"{spaces}(+) <{str(self.current)}>")

        return True


def parse_str(string: str, debug_level: int = 0) -> Out:
    """
    Parses the Markdown string and returns the parse result.
    """
    return Parser(debug_level).parse(string)


def parse_file(file_path: str, debug_level: int = 0, encoding: str = "utf-8") -> Out:
    """
    Parses the Markdown file and returns the parse result.
    """
    with open(file_path, encoding=encoding) as f:
        return parse_str(f.read(), debug_level)


if __name__ == "__main__":
    parse_file("./data/attention.md")
