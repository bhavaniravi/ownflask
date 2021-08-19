from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from wsgiref.simple_server import WSGIServer
import urllib.parse as urlparse
from urllib.parse import parse_qs
import json 
routes = {}
route_method_map = {}

class Request:
    def __init__(self, request, method):
        self.request = request
        self.method = method
        self.path = urlparse.urlparse(request.path).path
        self.qs = urlparse.parse_qs(urlparse.urlparse(request.path).query)
        self.headers = request.headers
        self.content_length = int(self.headers.get('content-length', 0))
        self.body = request.rfile.read(self.content_length)
        try:
            self.json = json.loads(self.body)
        except json.decoder.JSONDecodeError: 
            self.json = {}

class HttpReqHandler(SimpleHTTPRequestHandler):
    def is_method_supported(self, request):
        return request.method not in route_method_map[request.path]

    
    def process_request(self, request):
        if request.path not in routes:
            return self.not_found(request)
        if self.is_method_supported(request):
            return self.method_not_supported(request)
        
        resp = routes[request.path](request)
        self.write_response(resp)

            
        
    def do_GET(self):
        request = Request(self, method='GET')
        return self.process_request(request)

    def do_POST(self):
        request = Request(self, method='POST')
        return self.process_request(request)
        
    def write_response(self, content, response_code=200):
        if isinstance(content, str):
            content = str.encode(content)
        if isinstance(content, dict):
            content = str.encode(json.dumps(content))
        self.send_response(response_code)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(content)
    
    def not_found(self, request):
        return self.write_response(f"{request.path} 404 NOT FOUND", 404)

    def method_not_supported(self, request):
        return self.write_response(f"{request.path} {request.method} not supported", 401)


class Web:
    def __init__(self, name):
        self.name = name
        self.server = None
        

    def run(self, debug=False, port=8001, host="localhost"):
        self.debug = debug
        self.port = port
        self.host = host
        self.server = WSGIServer((self.host, self.port), HttpReqHandler)
        print (f"Starting server {host}:{port} \nMode :: Debug = {debug}")
        self.server.serve_forever()

    def route(self, path, methods=["GET"], **options):
        print (f"decorating path {path}, {options}")
        def decorator(f):
            print ("calling route", f)
            routes[path] = f
            route_method_map[path] = methods
        return decorator


    