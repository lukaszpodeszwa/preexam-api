"""Starts conntection, imports wrappers for backwards compatibility."""

import atexit
import os
import sys
from typing import Optional

import pymongo

from api.database.embed import embeds_storage, Embed, FuncEmbed
from api.database.wrappers import (delete_one, find, find_one, find_one_by_id,
                                   find_with_query, insert_one, update_one)
from api.database.connect import db
from api.database.cleaner import Cleaner
