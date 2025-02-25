import uuid
import time

def generate_unique_hash():
    random_hash = str(uuid.uuid4().int)[:6]
    timestamp = str(int(time.time()))
    unique_hash = F"{random_hash}_{timestamp}"
    return unique_hash