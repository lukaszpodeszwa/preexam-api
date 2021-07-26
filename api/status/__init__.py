from typing import List

import api.common.rest as rest 
import api.status.service as status

endpoints: List[rest.ResourceEndpoint] = [
    rest.get('/status', status.get)
]
