import sys
from Network.connector_module import URL 
class Node:
    def __init__(self,
                 parent = None
                 ) -> None:
        self.parent = parent 
        self.children = []

class Text(Node):
    def __init__(self,
                 text : str,
                 parent : Node = None
                 ) -> None:
        super().__init__(parent = parent)
        self.text = text
    def __repr__(self) -> str:
        return f"<Text : {self.text}>"

class Tag(Node):
    def __init__(self,
                 tag : str,
                 parent : Node = None
                ) -> None:
        super().__init__(parent = parent)
        self.tag = tag
    def __repr__(self) -> str:
        return f"<Tag : {self.tag}>"

class HTMLParser:
    def __init__(self,
                 body : str
                 ) -> None:
        self.body = body
        self.unfinished = []
    
    def parse(self) -> None:
        buffer = ""
        in_tag = False
        for b in self.body:
            if b == "<":
                if buffer:
                    in_tag = True
                    self.add_text(buffer)
                    buffer = ""
            elif b == ">":
                in_tag = False
                self.add_tag(buffer)
                buffer = ""
            else:
                buffer += b
        if not in_tag and buffer:
            self.add_text(buffer)
        return self.finish()
    
    def add_text(self, text : str) -> None:
        parent = self.unfinished[-1]
        node = Text(text, parent)
        parent.children.append(node)
    
    def add_tag(self, tag : str) -> None:
        if tag.startswith('/'):
            if len(self.unfinished) == 1 : return
            node = self.unfinished.pop()
            parent = self.unfinished[-1]
            parent.children.append(node)
        else:
            parent = self.unfinished[-1] if self.unfinished else None
            node = Tag(tag, parent)
            self.unfinished.append(node)
    
    def finish(self) -> Node:
        while len(self.unfinished) > 1:
            node = self.unfinished.pop()
            parent = self.unfinished[-1]
            parent.children.append(node)
        return self.unfinished.pop()
    
    def print_tree(self,
                   node : Node,
                   indent : int = 0
                   ) -> None:
        print(" " * indent, node)
        for child in node.children:
            self.print_tree(child, indent + 2)

if __name__ == "__main__":
    body = URL(sys.argv[1]).request(True if len(sys.argv) > 2 and sys.argv[2] == "-v" \
                                    else False)
    parser = HTMLParser(body)
    node = parser.parse()
    parser.print_tree(node)
    