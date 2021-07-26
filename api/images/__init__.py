from typing import List

from api.common import rest
from api.images.service import save_image, get, get_author, delete

endpoints: List[rest.ResourceEndpoint] = [
    rest.post('/images', save_image, 'image/png'),
    rest.get('/images/<int:image_id>', get),
    rest.get('/images/<int:image_id>/author', get_author),
    rest.delete('/images/<int:image_id>', delete),
]
