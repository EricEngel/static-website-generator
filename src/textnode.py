from enum import Enum


class TextType(Enum):
    TEXT = "text",
    BOLD = "bold",
    ITALIC = "italic",
    CODE = "code",
    LINK = "link",
    IMAGE = "image"


class TextNode:
    def __init__(self, text, text_type, url=None):
        self.text = text
        self.text_type = text_type
        self.url = url
    
    def __eq__(self, other):
        # Return True if all object properties are equal, otherwise return False.
        return (self.text == other.text and self.text_type == other.text_type and self.url == other.url)
    
    def __repr__(self):
        return f"TextNode({self.text}, {self.text_type.value[0]}, {self.url})"
