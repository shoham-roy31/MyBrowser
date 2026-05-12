import tkinter.font as tkFont
import Styles.parser_module as parser
from typing import Tuple
from tkinter import Canvas

BLOCK_ELEMENTS = [
    "html", "body", "article", "section", "nav", "aside",
    "h1", "h2", "h3", "h4", "h5", "h6", "hgroup", "header",
    "footer", "address", "p", "hr", "pre", "blockquote",
    "ol", "ul", "menu", "li", "dl", "dt", "dd", "figure",
    "figcaption", "main", "div", "table", "form", "fieldset",
    "legend", "details", "summary"
]
DEFAULT_STYLE = 'roman'
DEFAULT_SIZE = 16
DEFAULT_WEIGHT = 'normal'
WIDTH ,HEIGHT = 1024, 720
HSTEP, VSTEP = 10, 20
CODE_BOX_COLOR = 'red'
class Text:
    def __init__(self,
               text : str
               ) -> None:
        self.text = text

class Tag:
    def __init__(self,
                 tag : str
                ) -> None:
        self.tag = tag

class Layout:
    def __init__(self,
                 node : parser.Node,
                 parent : parser.Node,
                 previous : parser.Node
                 ) -> None:
        self.node = node
        self.parent = parent
        self.previous = previous
        self.children = []
    def layout(self) -> None:
        raise NotImplementedError
    
class DocumentLayout(Layout):
    def __init__(self,
                 node : parser.Node,
                 parent : parser.Node,
                 previous : parser.Node,
                ) -> None:
        super().__init__(node,parent,previous)

    def layout(self) -> None:
        child = BlockLayout(self.node,self,None)
        self.children.append(child)
        self.width = WIDTH - 2*HSTEP
        self.x = HSTEP
        self.y = VSTEP
        child.layout()
        self.height = child.height
        self.display_list = child.display_list
    
    def paint(self) -> list:
        return []

class BlockLayout(Layout):
    def __init__(self, 
                 node : parser.Node,
                 parent : parser.Node,
                 previous : parser.Node,
                 ) -> None:
        super().__init__(node,parent,previous)
        self.x = None
        self.y = None
        self.width = None
        self.height = None
        self.line = []
        self.display_list = []
        self.tokens = []
        self.style = DEFAULT_STYLE
        self.weight = DEFAULT_WEIGHT
        self.size = DEFAULT_SIZE
        self.flush()
    def layout_intermediate(self) -> None:
        previous = None
        for child in self.node.children:
            next = BlockLayout(child,self,previous)
            previous = next
    
    def layout_mode(self) -> str:
        if isinstance(self.node,parser.Text):
            return 'inline'
        elif any([isinstance(child, parser.Text) and\
                  child.tag in BLOCK_ELEMENTS for \
                    child in self.node.children]):
            return 'block'
        elif self.node.children:
            return 'inline'
        else:
            return 'block'
    
    def layout(self) -> None:
        self.x = self.parent.x
        self.width = self.parent.width
        self.y = self.previous.y + self.previous.height if self.previous \
                 else self.parent.y
        mode = self.layout_mode()
        if mode == 'block':
            self.height = sum([
                child.height for child in self.children
            ])
            previous = None
            for child in self.node.children:
                next = BlockLayout(child, self, previous)
                self.children.append(next)
                previous = next
        else:
            self.cursor_x = 0
            self.cursor_y = 0
            self.height = self.cursor_y
            self.weight = 'normal'
            self.style = 'roman'
            self.size = 12
            self.line = []
            self.recursion(self.node)
            self.flush()
        for child in self.children:
            child.layout()
        

    # def lex(self) -> None:
    #     buffer = ""
    #     in_tag = False
    #     for b in self.body:
    #         if b == "<":
    #             if buffer:
    #                 in_tag = True
    #                 self.tokens.append(Text(buffer))
    #                 buffer = ""
    #         elif b == ">":
    #             in_tag = False
    #             self.tokens.append(Tag(buffer))
    #             buffer = ""
    #         else:
    #             buffer += b
    #     if not in_tag and buffer:
    #         self.tokens.append(Text(buffer))
    
    def open_tag(self, 
                 tag : str,
                 style : str,
                 size : int,
                 weight : str
                 ) -> Tuple[str,str,str]:
        if tag == 'i': style = 'roman'
        elif tag == 'b': weight = "bold"
        elif tag == 'big' or tag == 'h1': size += 4
        elif tag == 'small' or tag == 'p': size -= 2
        elif tag == 'p' or tag == 'br' : 
            #self.flush()
            self.cursor_y += self.y
        return (style,size,weight)

    def close_tag(self, 
                  tag : str,
                  style : str,
                  size : int,
                  weight : str
                  ) -> Tuple[str,str,str]:
        if tag == 'i': style = DEFAULT_STYLE
        elif tag == 'b': weight = DEFAULT_WEIGHT
        elif tag == 'big' or tag == 'h1': size -= 4 
        elif tag == 'small' or tag == 'p': size += 2
        return (style,size,weight)

    def recursion(self, 
                  tree : parser.Node
                  ) -> None:
        if isinstance(tree, parser.Text):
            #print(f'Tree { tree.text }')
            for word in tree.text.split():
                self.word_processor(word,self.weight,
                                    self.style, self.size)
            self.flush()
        else:
            self.style, self.size,self.weight = self.open_tag(tree.tag,
                                                              self.style,
                                                              self.size,
                                                              self.weight)
            for child in tree.children:
                self.recursion(child)
            self.style, self.size, self.weight = self.close_tag(tree.tag,
                                                                self.style,
                                                                self.size,
                                                                self.weight)

    # def tokenize(self) -> None:
    #     self.lex()
    #     size = 16
    #     weight, style = "normal", "roman"
    #     for token in self.tokens:
    #         if isinstance(token, Text):
    #             for word in token.text.split():
    #                 self.word_processor(word, weight,
    #                                     style, size)
    #         elif token.tag == 'i':
    #             style = "italic"
    #         elif token.tag == '/i':
    #             style = "roman"
    #         elif token.tag == 'b':
    #             weight = "bold"
    #         elif token.tag == '/b':
    #             weight = "normal"
    #         elif token.tag == 'br':
    #             self.flush()
    #         elif token.tag == 'small':
    #             size -= 2
    #         elif token.tag == '/small':
    #             size += 2
    #         elif token.tag == 'big':
    #             size += 4
    #         elif token.tag == '/big':
    #             size -= 4
    #         elif token.tag == '/p':
    #             self.flush()
    #             self.cursor_y += self.vstep
    #     self.flush()

    def word_processor(self,
                       word : str,
                       weight : str,
                       style : str,
                       size : int
                       ) -> None:  
        font = tkFont.Font(size = size,
                           weight = weight,
                           slant = style)
        w = font.measure(word)
        #print(f'Cursor_x : {self.cursor_x} for node : {self.node} for word : {word} and width : {self.width}')
        if self.cursor_x + w > self.width:
            self.flush()
        self.line.append((self.cursor_x,word, font))
        self.cursor_x += w + font.measure(" ")
        
    
    def flush(self) -> None:
        if not self.line: return
        self.cursor_x = 0
        metrics = [font.metrics() for _,_,font in self.line]
        max_ascent = max(_['ascent'] for _ in metrics)
        max_descent = max(_['descent'] for _ in metrics)
        baseline = self.cursor_y + max_ascent * 1.25
        for rel_x, word, font in self.line:
            x = self.x + rel_x
            y = self.y + baseline - font.metrics('ascent')
            self.display_list.append((x,y,word,font)) 
        self.cursor_y = baseline + max_descent * 1.25
        self.cursor_x = self.x
        self.line = []
    
    def paint(self) -> list:
        cmds = []
        if isinstance(self.node, parser.Tag):
            print(f"The Node : {self.node} tag : {self.node.tag}")
            if self.node.tag:
                x2, y2 = self.x + self.width, self.y + self.height
                cmds.append(DrawRect(self.x,self.y,x2,y2,CODE_BOX_COLOR))
        if self.layout_mode() == 'inline':
            for x,y,word,font in self.display_list:
                cmds.append(DrawText(x,y,word,font))
        return cmds
    
class Draw:

    def __init__(self,
                 x : int,
                 y : int
                ) -> None:
        self.x = x
        self.y = y
    def execute(self) -> None:
        raise NotImplementedError
    
class DrawText(Draw):

    def __init__(self,
                 x : int,
                 y : int,
                 text : str,
                 font : tkFont
                 ) -> None:
        super().__init__(x,y)
        self.text = text
        self.font = font
        self.y2 = y + self.font.metrics('linespace')

    def execute(self,
                scroll : int,
                canvas : Canvas
                ) -> None:
        canvas.create_text(
            self.x, self.y - scroll,
            text = self.text,
            font = self.font,
            anchor = 'nw'
        )
        
class DrawRect(Draw):
    
    def __init__(self,
                 x1 : int,
                 y1 : int,
                 x2 : int,
                 y2 : int,
                 color : str
                ) -> None:
        super().__init__(x = x1, y = y1)
        self.x2 = x2
        self.y2 = y2
        self.color = color
    
    def execute(self,
                scroll : int,
                canvas : Canvas
               ) -> None:
        canvas.create_rectangle(
            self.x,self.y - scroll,
            self.x2,self.y2 - scroll,
            width = 0,
            fill = self.color
        )

def paint_tree(layout_object : parser.Node,
               display_list : list
              ) -> None:
    display_list.extend(layout_object.paint())
    for child in layout_object.children:
        paint_tree(child, display_list)
