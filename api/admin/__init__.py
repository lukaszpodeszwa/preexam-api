import api.common.rest as rest
import api.admin.schema as schema
import api.admin.accounts as accounts
from typing import List

endpoints: List[rest.ResourceEndpoint] = [
    rest.post(
        '/admin/accounts/<int:account_id>/block',
        accounts.block,
    ),
    rest.post(
        '/admin/accounts/<int:account_id>/unblock',
        accounts.unblock,
    ),
    rest.get('/admin/accounts',
             accounts.query,
             query_schema=schema.ACCOUNTS_QUERY),
    rest.post('/admin/accounts/<int:account_id>/init_password_change',
              accounts.init_password_change),
    rest.delete('/admin/accounts/<int:account_id>', accounts.delete),
    rest.patch('/admin/accounts/<int:account_id>/role', accounts.change_role)
]