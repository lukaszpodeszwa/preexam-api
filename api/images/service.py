"""This file contents simple "server" for saving, compressing,
decompressing and getting images witch can be used in questions."""

import imghdr
import os
import pathlib
import stat
import sys
import zlib
from typing import Dict

from api import database, errors
from api.common.service import ServiceRequest, ServiceResponse
from api.middlewares import require_auth

IMAGES_DIR: str = os.environ.get('API_IMAGES_DIR')  # type: ignore

if not IMAGES_DIR:
    sys.exit('API_IMAGES_DIR not set!')

if not os.path.isdir(IMAGES_DIR):
    sys.exit('API_IMAGES is not a directory or does not exist!')

if not os.access(IMAGES_DIR, os.W_OK):
    raise PermissionError(f'No write permissions to {IMAGES_DIR}!')

# Add trailing slash if necessery.
if IMAGES_DIR[:-1] != '/':
    IMAGES_DIR += '/'

listdir = os.listdir(IMAGES_DIR)
# Key is image id value is author id.
images: Dict[int, int] = {}

if listdir:
    images = {int(f.split('_')[0]): int(f.split('_')[1]) for f in listdir}
    # Not checking if image is dir because there will be no dirs.


def _get_next_image_id() -> int:
    return max(images.keys()) + 1 if images else 1


@require_auth('mod')
def save_image(r: ServiceRequest) -> ServiceResponse:
    if len(r.content) > 1024:
        ServiceResponse(422, errors=errors.api_error('image_too_big'))
    image_type = imghdr.what("", h=r.content)
    if image_type is None or image_type != 'png':
        return ServiceResponse(422,
                               errors=errors.api_error('image_is_not_raw_png'))

    next_image_id = _get_next_image_id()
    image_path = (IMAGES_DIR
                  + str(next_image_id)
                  + '_'
                  + str(r.user_session.user_id))

    with open(image_path, 'wb') as i:
        i.write(zlib.compress(r.content, 9))

    images[next_image_id] = r.user_session.user_id
    return ServiceResponse(201, {'_id': next_image_id})


def get(r: ServiceRequest, image_id: int) -> ServiceResponse:
    if image_id not in images:
        return ServiceResponse(404, errors=errors.api_error('image_not_found'))
    image_path = (IMAGES_DIR
                  + str(image_id)
                  + '_'
                  + str(images[image_id]))
    image_data = b''
    with open(image_path, 'rb') as i:
        image_data = i.read()
    return ServiceResponse(
        200,
        zlib.decompress(image_data),  # type: ignore
        content_type='image/png')


def get_author(r: ServiceRequest, image_id: int) -> ServiceResponse:
    if image_id not in images:
        return ServiceResponse(404, errors=errors.api_error('image_not_found'))
    return ServiceResponse(200, {'author_id': images[image_id]})


@require_auth('mod')
def delete(r: ServiceRequest, image_id: int) -> ServiceResponse:
    for f in pathlib.Path(IMAGES_DIR).glob(str(image_id) + '*'):
        os.remove(IMAGES_DIR + f.name)
    return ServiceResponse(204)
