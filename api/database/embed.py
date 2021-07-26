from dataclasses import dataclass
from typing import Callable, Dict, NewType

EmbedName = NewType('EmbedName', str)

# Dict[EmbedName, Embed]
embeds_storage = {}  # type: ignore


@dataclass
class Embed:
    """Basic embed data with using to_query() can be
       translated to lookup aggregation.

       is_array defines if given embed embeds to array.
       Eg.
       >>> Embed('questions', 'questions_ids', 'questions', is_array=True)"""
    name: str
    local_filed: str
    from_collection: str
    is_array: bool = False
    forien_field: str = '_id'

    def __post_init__(self):
        embeds_storage[self.name] = self

    def to_query(self) -> Dict[str, str]:
        return {
            "from": self.from_collection,
            "localField": self.local_filed,
            "foreignField": self.forien_field,
            "as": self.name
        }


@dataclass
class FuncEmbed:
    """Like Embed, but accualy used to exec
       func with forien_field's value as argument on local_field"""
    name: str
    # FuncEmbed doesn't use local_field but it is needed for later projection.
    local_filed: str
    func: Callable
    forien_field: str = '_id'

    def __post_init__(self):
        embeds_storage[self.name] = self
