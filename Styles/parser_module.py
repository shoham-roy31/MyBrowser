import sys
from typing import Tuple,Optional
from Network.connector_module import URL 
SELF_CLOSING_TAG = [
    "area","base","br","col","embed","hr","img","input",
    "link","meta","param","source","track","wbr"
]
HEAD_TAGS = [
    "base","basefont","bgsound","noscript","link",
    "meta","title","style","script",
]
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
                 attrs : dict[str,str],
                 parent : Node = None
                ) -> None:
        super().__init__(parent = parent)
        self.tag = tag
        self.attrs = attrs
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
                buffer = buffer[:-1] if buffer.endswith("/") else buffer
                self.add_tag(buffer)
                buffer = ""
            else:
                buffer += b
        if not in_tag and buffer:
            self.add_text(buffer)
        return self.finish()
    
    def add_text(self, text : str) -> None:
        if text.isspace() : return
        self.implicit_tags(None)
        parent = self.unfinished[-1]
        node = Text(text, parent)
        parent.children.append(node)
    
    def add_tag(self, tag : str) -> None:
        if tag.startswith('!'): return
        elif tag.startswith('/'):
            self.implicit_tags(tag)
            if len(self.unfinished) == 1 : return
            node = self.unfinished.pop()
            parent = self.unfinished[-1]
            parent.children.append(node)
        else:
            tag, attrs = self.get_attributes(tag)
            self.implicit_tags(tag)
            if tag in SELF_CLOSING_TAG:
                parent = self.unfinished[-1]
                node = Tag(tag,attrs,parent)
                parent.children.append(node)
            else:
                parent = self.unfinished[-1] if self.unfinished else None
                node = Tag(tag,attrs,parent)
                self.unfinished.append(node)
    def implicit_tags(self,
                      tag : Optional[str | None] = None
                      ) -> None:
        while True:
            open_tags = [node.tag for node in self.unfinished]
            if open_tags == [] and tag != 'html':
                self.add_tag("html")
            elif open_tags == ["html"] and tag \
            not in ["head","body","/html"]:
                if tag in HEAD_TAGS:
                    self.add_tag("head")
                else:
                    self.add_tag("body")
            elif open_tags == ["html","head"] and \
            tag not in ["/head"] + HEAD_TAGS:
                self.add_tag("/head")
            else: break
                            
    
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
        if isinstance(node,Tag) : print(f"Attrs : {node.attrs}")
        for child in node.children:
            self.print_tree(child, indent + 2)

    
    def get_attributes(self, text : str) -> Tuple[str,dict[str,str]]:
        attrs = {}
        def adjust_text(text : str,
                        seperator : str = '`~`'
                        ) -> str:
            word = ""
            body = ""
            in_quote = False
            for c in text:
                if c in ["'","\""]:
                    if word:
                        in_quote = False
                        body += word
                        word = ""
                    else:
                        in_quote = True
                elif in_quote:
                    if c == " ": word += seperator
                    else : word += c                    
                else:
                    body += c
            return body
        text = adjust_text(text)
        parts = text.split()
        tag = parts[0].casefold() if parts else ""
        for pair in parts[1:]:
            if "=" in pair:
                key,value = pair.split("=",1)
                value = value.replace("`~`"," ")
                attrs[key.casefold()] = value
            else:
                attrs[pair.casefold()] = ""
        return tag, attrs


if __name__ == "__main__":
    body = URL(sys.argv[1]).request(True if len(sys.argv) > 2 and sys.argv[2] == "-v" \
                                    else False)

    parser = HTMLParser(body)
    node = parser.parse()
    parser.print_tree(node)
    