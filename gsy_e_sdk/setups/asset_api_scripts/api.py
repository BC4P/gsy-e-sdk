from flask import Flask
from redis_basic_strategies import Oracle,register_asset_list
aggregator = Oracle(aggregator_name="MY ORACLE")
LOAD_NAMES = ["Load 1 L13", "Load 2 L21", "Load 3 L17"]
app = Flask(__name__)
@app.route("/")
def hello_world():
    print('hello world')
    asset_args = {"autoregister": True, "pubsub_thread": aggregator.pubsub}

    ok = register_asset_list([LOAD_NAMES[0]] ,asset_args, {}, aggregator)

    return ok