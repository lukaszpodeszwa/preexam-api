from typing import List

from api.accounts.current_quiz import mine_current_quiz
from api.accounts import history
from api.accounts.service import (activate, confirm_password_change, find,
                                  find_my_account, forgot_password, register,
                                  update, update_my_account, quick_password_change)
from api.accounts.schema import HISTORY_QUERY
from api.common.rest import ResourceEndpoint, get, patch, post


endpoints: List[ResourceEndpoint] = [
    get('/accounts/<int:account_id>', find),
    patch('/accounts/<int:account_id>', update),
    get('/accounts/my_account', find_my_account),
    patch('/accounts/my_account', update_my_account),
    post('/accounts/my_account/change_password', quick_password_change),
    get('/accounts/my_account/history', history.find_many_mine, HISTORY_QUERY),
    get('/accounts/<int:account_id>/history', history.find, HISTORY_QUERY),
    get('/accounts/my_account/current_quiz', mine_current_quiz),
    post('/accounts/register', register),
    post('/accounts/<int:account_id>/activate', activate),
    post('/accounts/forgot_password', forgot_password),
    post('/accounts/forgot_password/confirm', confirm_password_change),
]
