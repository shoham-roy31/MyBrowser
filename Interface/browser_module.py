import sys
import tkinter
import tkinter.font
from typing import List, Tuple
from Network.connector_module import URL
from Styles.parser_module import HTMLParser
from Styles.format_module import Text, Tag, DocumentLayout, paint_tree, DrawRect, DrawText

WIDTH ,HEIGHT = 1024, 720
HSTEP, VSTEP = 10, 20,
NOT_FOUND = "<i>404 Not Found</i>"
TITLE = "Portal"
SCROLL_STEP = 10

def layout(tokens : List[Text | Tag]) -> List[Tuple[int,int,str,tkinter.font.Font]]:
    display_list = []
    font = tkinter.font.Font()
    cursor_x, cursor_y = HSTEP, VSTEP
    weight,style = "normal", "roman"
    for token in tokens:
        if isinstance(token, Text):
            for c in token.text.split():
                font = tkinter.font.Font(size = 16,
                                         weight = weight,
                                         slant = style)
                w = font.measure(c)
                if cursor_x + w > WIDTH - HSTEP:
                    cursor_x = HSTEP
                    cursor_y += font.metrics("linespace") * 1.25
                display_list.append((cursor_x,cursor_y,c,font))
                cursor_x += w + font.measure(" ")
        elif token.tag == 'i':
            style = "italic"
        elif token.tag == '/i':
            style = "roman"
        elif token.tag == 'b':
            weight = "bold"
        elif token.tag == '/b':
            weight = "normal"
        elif token.tag == 'br':
            cursor_x = HSTEP
            cursor_y += font.metrics("linespace") * 1.25
    return display_list

def lex(body : str) -> List[Text | Tag]:
    tokens = []
    buffer = ""
    in_tag = False
    for c in body:
        if c == "<":
            if buffer:
                in_tag = True
                tokens.append(Text(buffer))
                buffer = ""
        elif c == ">":
            in_tag = False
            tokens.append(Tag(buffer))
            buffer = ""
        else:
            buffer += c
    if not in_tag and buffer:
        tokens.append(Text(buffer))
    return tokens

class Browser:
    def __init__(self) -> None:
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(self.window,
                                     width = WIDTH,
                                     height = HEIGHT)
        self.canvas.pack()
        self.window.title(TITLE)
        self.scroll = 0
        self.display_list = []
        self.window.bind("<Down>",self.scroll_down)
        self.window.bind("<Up>",self.scroll_up)
        self.window.bind("<MouseWheel>",
                         lambda e : self.scroll_down(e) \
                            if e.delta < 0 \
                            else self.scroll_up(e))
        self.window.resizable(True,True)
    def draw(self) -> None:
        self.canvas.delete("all")
        for cmd in self.display_list:
            if cmd.y > self.scroll + HEIGHT : continue
            if cmd.y2 + VSTEP < self.scroll : continue
            cmd.execute(self.scroll, self.canvas)
    def load(self,
             url : URL
            ) -> None:
        body = url.request()
        #print(f"Body : {body}")

        parser = HTMLParser(body if (body != -1 and body != "") \
                          else NOT_FOUND)
        node = parser.parse()
        print(f"Node : {parser.print_tree(node)}")
        layout = DocumentLayout(node,None,None)
        layout.layout()
        paint_tree(layout, self.display_list)
        print(f"Total DrawText : {sum([isinstance(d,DrawText)  for d in self.display_list])} Total DrawRect : {sum([isinstance(d,DrawRect) for d in self.display_list])}")
        #layout.tokenize()
        #layout.recursion(node)
        #self.display_list = layout.display_list
        #print(self.display_list)
        self.draw()
    
    def scroll_down(self,
                    event : object
                    ) -> None:
        self.scroll += SCROLL_STEP
        self.draw()

    def scroll_up(self,
                  event : object
                  ) -> None:
        self.scroll -= SCROLL_STEP if self.scroll >= SCROLL_STEP \
                        else 0
        self.draw()


if __name__ == "__main__":
    Browser().load(URL(sys.argv[1]))
    tkinter.mainloop()