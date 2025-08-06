class HTMLNode:
    def __init__(self, tag=None, value=None, children=None, props=None):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props
    

    def __repr__(self):
        return f"TAG: {self.tag}, VALUE: {self.value}, CHILDREN: {self.children}, PROPS: {self.props}"
    

    def to_html(self):
        raise NotImplementedError
    

    def props_to_html(self):
        result = ""
        if self.props is not None:
            for prop in self.props:
                result += f" {prop}=\"{self.props[prop]}\""
        return result


class LeafNode(HTMLNode):
    def __init__(self, tag, value, props=None):
        super().__init__(tag, value, None, props=props)
    

    def to_html(self):
        if self.value is None:
            raise ValueError("A value must be supplied!")
        if self.tag is None:
            return self.value
        elif self.tag == "hr":
            return "<hr>\n"
        elif self.tag == "img":
            return f"<{self.tag}{self.props_to_html()}>"
        return f"<{self.tag}{self.props_to_html()}>{self.value}</{self.tag}>"


class ParentNode(HTMLNode):
    def __init__(self, tag, children, props=None):
        super().__init__(tag, None, children, props=props)


    def to_html(self):
        result = ""
        if self.children is None:
            raise ValueError("ParentNode missing children")
        if self.tag is None:
            raise ValueError("A tag must be supplied!")
        elif self.tag == "ul" or self.tag == "ol":
            result = f"<{self.tag}{self.props_to_html()}>\n"
        else:
            result = f"<{self.tag}{self.props_to_html()}>"

        for child in self.children:
            result += child.to_html()
        
        result += f"</{self.tag}>\n"
        return result