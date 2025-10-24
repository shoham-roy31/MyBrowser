import tkinter.font as tkFont
import Styles.parser_module as parser
from typing import Tuple

DEFAULT_STYLE = 'roman'
DEFAULT_SIZE = 16
DEFAULT_WEIGHT = 'normal'

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
                 body : str,
                 hstep : int,
                 vstep : int,
                 height : int,
                 width : int,) -> None:
        self.body = body
        self.hstep = hstep
        self.vstep = vstep
        self.height = height
        self.width = width
        self.line = []
        self.display_list = []
        self.cursor_x = self.hstep
        self.cursor_y = self.vstep
        self.tokens = []
        self.style = DEFAULT_STYLE
        self.weight = DEFAULT_WEIGHT
        self.size = DEFAULT_SIZE
        self.flush()

    def lex(self) -> None:
        buffer = ""
        in_tag = False
        for b in self.body:
            if b == "<":
                if buffer:
                    in_tag = True
                    self.tokens.append(Text(buffer))
                    buffer = ""
            elif b == ">":
                in_tag = False
                self.tokens.append(Tag(buffer))
                buffer = ""
            else:
                buffer += b
        if not in_tag and buffer:
            self.tokens.append(Text(buffer))
    
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
            self.flush()
            self.cursor_y += self.vstep
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
            for word in tree.text.split():
                self.word_processor(word,self.weight,
                                    self.style, self.size)
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

    def tokenize(self) -> None:
        self.lex()
        size = 16
        weight, style = "normal", "roman"
        for token in self.tokens:
            if isinstance(token, Text):
                for word in token.text.split():
                    self.word_processor(word, weight,
                                        style, size)
            elif token.tag == 'i':
                style = "italic"
            elif token.tag == '/i':
                style = "roman"
            elif token.tag == 'b':
                weight = "bold"
            elif token.tag == '/b':
                weight = "normal"
            elif token.tag == 'br':
                self.flush()
            elif token.tag == 'small':
                size -= 2
            elif token.tag == '/small':
                size += 2
            elif token.tag == 'big':
                size += 4
            elif token.tag == '/big':
                size -= 4
            elif token.tag == '/p':
                self.flush()
                self.cursor_y += self.vstep
        self.flush()

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
        if self.cursor_x + w > self.width - self.hstep:
            self.flush()
        self.line.append((self.cursor_x,word, font))
        self.cursor_x += w + font.measure(" ")
        
    
    def flush(self) -> None:
        if not self.line: return
        metrics = [font.metrics() for _,_,font in self.line]
        max_ascent = max(_['ascent'] for _ in metrics)
        max_descent = max(_['descent'] for _ in metrics)
        baseline = self.cursor_y + max_ascent * 1.25
        for x, word, font in self.line:
            y = baseline - font.metrics('ascent')
            self.display_list.append((x,y,word,font))
        self.cursor_y = baseline + max_descent * 1.25
        self.cursor_x = self.hstep
        self.line = []
