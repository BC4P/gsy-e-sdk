import os
MAX_WORKER_THREADS = 5

SETUP_FILE_PATH = None

DEFAULT_DOMAIN_NAME = "https://d3aweb.gridsingularity.com"
DEFAULT_WEBSOCKET_DOMAIN = "wss://d3aweb.gridsingularity.com/external-ws"
API_CLIENT_SIMULATION_ID = ""
CUSTOMER_WEBSOCKET_DOMAIN_NAME = "ws://localhost:4000"
LOCAL_REDIS_URL = os.getenv('REDIS_URL', "redis://localhost:6379")
MIN_SLOT_COMPLETION_TICK_TRIGGER_PERCENTAGE = 10
