import threading
import time

from api.database import db


class Cleaner:
    """Deamon for deleting expired entaties from database."""
    def __init__(self, interval=5 * 60):
        self.interval = interval

        thread = threading.Thread(target=self.run, daemon=True)
        thread.start()

    def run(self):
        while True:
            for collection in db.list_collection_names():
                db[collection].delete_many({'exp': {'$lt': int(time.time())}})
            time.sleep(self.interval)