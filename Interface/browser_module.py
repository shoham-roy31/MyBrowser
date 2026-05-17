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
        self.window.title(TITLE)
        self.window.resizable(True,True)

        # Search Bar
        self.search_frame = tkinter.Frame(self.window)
        self.search_frame.pack(side=tkinter.TOP, fill=tkinter.X)

        self.url_entry = tkinter.Entry(self.search_frame)
        self.url_entry.pack(side=tkinter.LEFT, fill=tkinter.X, expand=True, padx=5, pady=5)
        self.url_entry.bind("<Return>", self.navigate)

        self.go_button = tkinter.Button(self.search_frame, text="Go", command=self.navigate)
        self.go_button.pack(side=tkinter.LEFT, padx=5, pady=5)

        self.canvas = tkinter.Canvas(self.window,
                                     width = WIDTH,
                                     height = HEIGHT)
        self.canvas.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)

        self.scroll = 0
        self.display_list = []
        self.window.bind("<Down>",self.scroll_down)
        self.window.bind("<Up>",self.scroll_up)
        self.window.bind("<MouseWheel>",
                         lambda e : self.scroll_down(e) \
                            if e.delta < 0 \
                            else self.scroll_up(e))

        # Initial URL handling
        if len(sys.argv) > 1:
            self.url_entry.insert(0, sys.argv[1])
            self.navigate()

    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]

    def augment_url(self, url: str) -> str:
        url = url.strip().lower()
        if not url:
            return ""

        # 1. Correct Scheme
        schemes = ["http", "https"]
        if "://" in url:
            scheme, rest = url.split("://", 1)
            best_scheme = min(schemes, key=lambda s: self._levenshtein_distance(scheme, s))
            if self._levenshtein_distance(scheme, best_scheme) <= 2:
                url = f"{best_scheme}://{rest}"
        else:
            url = "https://" + url

        # Re-verify and handle www. addition
        if "://" in url:
            scheme_part, rest = url.split("://", 1)
            if 'www.' not in rest:
                url = f"{scheme_part}://www.{rest}"

        # 2. Correct TLD
        common_tlds = ["com", "org", "net", "edu", "gov", "io", "me", "uk", "ca", "de", "jp"]
        if "." in url:
            # Extract domain: everything between :// and the first /
            try:
                domain_end = url.find("/", url.find("://") + 3)
                if domain_end == -1:
                    domain_end = len(url)

                domain_start = url.find("://") + 3
                domain_part = url[domain_start:domain_end]

                if "." in domain_part:
                    domain_split = domain_part.split(".")
                    tld = domain_split[-1]
                    best_tld = min(common_tlds, key=lambda t: self._levenshtein_distance(tld, t))
                    if self._levenshtein_distance(tld, best_tld) <= 2:
                        domain_split[-1] = best_tld
                        corrected_domain = ".".join(domain_split)
                        url = url[:domain_start] + corrected_domain + url[domain_end:]
            except Exception:
                pass

        # 3. Ensure trailing slash
        if not url.endswith("/"):
            url += "/"

        return url

    def navigate(self, event=None) -> None:
        url_text = self.url_entry.get()
        if not url_text:
            return

        # URL Augmentation: ensure URL has a scheme
        url_text = self.augment_url(url_text)
        # if "://" not in url_text:
        #     url_text = "https://" + url_text
        self.url_entry.delete(0, tkinter.END)
        self.url_entry.insert(0, url_text)

        try:
            url_obj = URL(url_text)
            self.load(url_obj)
        except ValueError as e:
            print(f"Invalid URL: {e}")

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
    Browser()
    tkinter.mainloop()