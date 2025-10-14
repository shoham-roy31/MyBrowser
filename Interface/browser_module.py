import sys
import tkinter
from Network.connector_module import URL
from typing import List, Tuple
WIDTH ,HEIGHT = 1024, 720
HSTEP, VSTEP = 10, 20,
NOT_FOUND = "404 NOT FOUND"
TITLE = "Portal"
SCROLL_STEP = 10

def layout(body : str) -> List[Tuple[int,int,str]]:
    display_list = []
    cursor_x, cursor_y = HSTEP, VSTEP
    for c in body:
        display_list.append((cursor_x,cursor_y,c))
        if cursor_x >= WIDTH - HSTEP:
            cursor_x = HSTEP
            cursor_y += VSTEP
        cursor_x += HSTEP
    return display_list

class Browser:
    def __init__(self) -> None:
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(self.window,
                                     width = WIDTH,
                                     height = HEIGHT)
        self.canvas.pack()
        self.window.title(TITLE)
        self.scroll = 0
        self.window.bind("<Down>",self.scroll_down)
        self.window.bind("<Up>",self.scroll_up)
        self.window.bind("<MouseWheel>",
                         lambda e : self.scroll_down(e) \
                            if e.delta < 0 \
                            else self.scroll_up(e))
        self.window.resizable(True,True)
    def draw(self) -> None:
        self.canvas.delete("all")
        for x,y,c in self.display_list:
            if y > self.scroll + HEIGHT : continue
            if y + VSTEP < self.scroll : continue
            self.canvas.create_text(x,y - self.scroll,text = c)
    def load(self,
             url : URL
            ) -> None:
        body = url.request()
        self.display_list = layout(body) if body != -1 \
                            else layout(NOT_FOUND)
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