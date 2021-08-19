from ownflask import Web

app = Web(__name__)

@app.route("/")
def home(request):
    return "Hello, World!"

@app.route("/hello", methods=["GET"])
def hello(request):
    return {"status": "Hello"}

@app.route("/post", methods=["POST"])
def post(request):
    return request.json


app.run()