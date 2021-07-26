import atexit
import os
import sys
from typing import Tuple

import pymongo


def _close(clinet):
    print("Closing database connection...")
    clinet.close()
    print("Successfully clossed databse connection!")


client: pymongo.MongoClient = None


def connect(uri: str) -> Tuple[pymongo.database.Database, pymongo.MongoClient]:
    print("Connecting to databse...")
    client = pymongo.MongoClient(uri)
    print("Successfully connected to databse!")
    atexit.register(_close, client)
    if "TheSchoolest" in uri:
        return client.TheSchoolest, client
    elif "PreExam" in uri:
        return client.PreExam, client
    return None, None


_db_uri: str
try:
    _db_uri = os.environ["DATABASE_URI"]
except KeyError as e:
    sys.exit(f"Env var {e} is not set!")

# Database instance for wrappers or executing queries without them.
db, client = connect(_db_uri)
if not client:
    sys.exit(f"Cannot connect to database!")