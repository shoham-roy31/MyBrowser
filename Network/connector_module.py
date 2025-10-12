import sys
import ssl
import socket
PORT_HTTP = 80
PORT_HTTPS = 443
NOT_FOUND = "URL Not Found"
PROTOCOLS = ["http","https"]
HTTP_VERSION = "1.0"
def assert_params(**args):
    if args['url'] is None:
        raise ValueError("URL cannot be None")
    else:
        if not isinstance(args['url'],str):
            raise TypeError("URL must be a string")
class URL:
    def __init__(self, url : str) -> None:
        args = locals()
        assert_params(**args)
        self.url = url
        try:
            self.scheme,url= url.split("://",1)
            assert self.scheme in PROTOCOLS, f'Unsupported Protocol : {self.scheme}'
            if "/" not in url:
                url += "/"
            self.host, url = url.split("/",1)
            self.path = "/" + url
            if ":" in self.host:
                self.host, self.port = self.host.split(":",1)
                self.post = int(self.port)
            else: self.port = PORT_HTTP if self.scheme == PROTOCOLS[0] else PORT_HTTPS
        except Exception as e:
            raise ValueError(f"Invalid URL : {url} : {e}")
    def request(self) -> str | int:
        s = socket.socket(family = socket.AF_INET,
                          type = socket.SOCK_STREAM,
                          proto = socket.IPPROTO_TCP)
        if self.scheme == PROTOCOLS[1]:
            context = ssl.create_default_context()
            s = context.wrap_socket(s, server_hostname = self.host)
        try:
            s.connect((self.host,self.port))
            request = f"GET {self.path} HTTP/{HTTP_VERSION}\r\nHost: {self.host}\r\n\r\n"
            s.send(request.encode("utf-8"))
            response = s.makefile("r",encoding = "utf-8", newline = "\r\n")
            version,status,explanation = response.readline().split(" ",2)
            response_headers = {}
            while True:
                line = response.readline()
                if line == "\r\n": break
                header, value = line.split(":",1)
                response_headers[header.casefold()] = value.strip()
            assert "transer-encoding" not in response_headers
            assert "content-encoding" not in response_headers
            content = response.read()
            s.close()
            return content
        except Exception as e:
            print(f"Couldn't Connect to the host : {self.url} and port : {self.port} derived from URL {self.url} : {e}")
            return -1
        
def show(content : str) -> str:
    in_tag = False
    body = ""
    for c in content:
        if c == "<" : in_tag = True
        elif c == ">": in_tag = False
        elif not in_tag:
            body += c
    print(body)

def load(url : str) -> None:
    body = url.request()
    if body != -1: show(body)
            
    else: show(NOT_FOUND)

if __name__ == "__main__":
    url = URL(sys.argv[1])
    load(url)    
