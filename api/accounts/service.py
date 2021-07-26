import hashlib
import random
import time
from typing import Dict, Union

import argon2

import api.accounts.schema as schema
import api.database as database
import api.mailing as mailing
from api.common import ServiceRequest, ServiceResponse
from api.errors import api_error
from api.middlewares import require_auth, validate

ph = argon2.PasswordHasher()

database.Embed('author', 'author_id', 'accounts')


def _get_password_reset_code(email: str) -> str:
    expire_time = int(time.time()) + 1 * 3600
    hash_string = email + str(time) + ''.join(
        [str(x) for x in random.sample(range(0, 20), 20)])
    password_reset_token = hashlib.sha1(hash_string.encode()).hexdigest()
    return password_reset_token


def _get_registration_code() -> str:
    code_digits = [
        str(random.randint(0, 9)) if counter not in [3, 7] else '-'
        for counter in range(11)
    ]
    return ''.join(code_digits)


@validate(schema.ACCOUNT)
def register(r: ServiceRequest) -> ServiceResponse:
    account = r.content
    existing_email = database.db.accounts.find_one({'email': account['email']})
    if existing_email:
        return ServiceResponse(403, errors=api_error('account_already_exists'))

    existing_username = database.db.accounts.find_one(
        {'username': account['username']})
    if existing_username:
        return ServiceResponse(403, errors=api_error('username_taken'))

    account['role'] = 'user'
    account['password'] = ph.hash(account['password'])

    code = _get_registration_code()
    response = database.insert_one('registers', {
        'code': code,
        'account': account,
        'exp': int(time.time()) + 3600,
    })
    error = mailing.send_mail(account['email'], 'Rejestracja w PreExam',
                              mailing.REGISTER, {'register_code': code})
    if error:
        return ServiceResponse(50002, errors=error)

    return response


@validate(schema.ACTIVATE_ACCOUNT)
def activate(r: ServiceRequest, account_id: int) -> ServiceResponse:
    code = r.content['code']
    register = database.db.registers.find_one({
        'code': code,
        '_id': account_id,
    })

    if not register:
        return ServiceResponse(403,
                               errors=api_error('invalid_registration_code'))

    if int(time.time()) >= register['exp']:
        database.delete_one('registers', account_id)
        return ServiceResponse(403,
                               errors=api_error('registration_code_expired'))

    database.delete_one('registers', account_id)
    mailing.send_mail(register['account']['email'],
                      'Aktywacja konta w PreExam', mailing.ACCOUNT_ACTIVATED)
    return database.insert_one('accounts', register['account'])


@validate(schema.FORGOT_PASSWORD)
def forgot_password(r: ServiceRequest) -> ServiceResponse:
    """Sends link to reset password to given email.
       I don't know how to name it correctly."""
    email = r.content['email']
    account = database.find_one('accounts', {'email': email})
    if not account:
        return ServiceResponse(204)

    token = _get_password_reset_code(email)
    response = database.insert_one('password_changes', {
        'token': token,
        'exp': int(time.time()) + 3600,
        'email': email
    })
    if response.errors:
        return response
    reset_link = f"www.preexam.pl/app/reset-password/{token}/{email}"
    error = mailing.send_mail(email, 'Przypomnienie hasła PreExam',
                              mailing.RESET_PASSWORD,
                              {'reset_password_link': reset_link})
    return ServiceResponse(204) if not error else ServiceResponse(500,
                                                                  errors=error)


@validate(schema.CONFIRM_FORGOT_PASWORD_CHANGE)
def confirm_password_change(r: ServiceRequest) -> ServiceResponse:
    email = r.content['email']
    code = r.content['code']
    password_reset = database.db.password_changes.find_one({
        'email': email,
        'token': code
    })
    if not password_reset:
        return ServiceResponse(
            403, errors=api_error('invalid_password_reset_code_or_email'))

    if int(time.time()) >= password_reset['exp']:
        database.delete_one('password_changes', password_reset['_id'])
        return ServiceResponse(403,
                               errors=api_error('password_reset_code_expired'))

    database.db.accounts.find_one_and_update(
        {'email': email},
        {'$set': {
            'password': ph.hash(r.content['new_password'])
        }})
    database.delete_one('password_changes', password_reset['_id'])
    error = mailing.send_mail(email, 'Zmiana hasła w PreExam.',
                              mailing.PASSWORD_CHANGED)
    return ServiceResponse(204) if not error else ServiceResponse(500,
                                                                  errors=error)


@require_auth()
def find_my_account(r: ServiceRequest) -> ServiceResponse:
    return database.find_one_by_id('accounts', r.user_session.user_id, {
        'password': False,
        'history': False,
        'current_quiz': False
    })


@require_auth()
def find(r: ServiceRequest, account_id: int) -> ServiceResponse:
    return database.find_one_by_id('accounts', account_id, {
        'password': False,
        'history': False,
        'current_quiz': False
    })


@validate(schema.UPDATE_ACCOUNT)
@require_auth()
def update_my_account(r: ServiceRequest) -> ServiceResponse:
    if r.content.get('username'):
        existing_username = database.db.accounts.find_one(
            {'username': r.content['username']})

        if existing_username:
            return ServiceResponse(403, errors=api_error('username_taken'))
    return database.update_one('accounts', r.user_session.user_id, r.content)


@validate(schema.UPDATE_ACCOUNT)
@require_auth('admin', 'account')
def update(r: ServiceRequest, account_id: int) -> ServiceResponse:
    if r.content.get('username'):
        existing_username = database.db.accounts.find_one(
            {'username': r.content['username']})

        if existing_username:
            return ServiceResponse(403, errors=api_error('username_taken'))
    return database.update_one('accounts', account_id, r.content)


@validate(schema.QUICK_PASSWORD_CHANGE)
@require_auth()
def quick_password_change(req: ServiceRequest) -> ServiceResponse:
    user_id = req.user_session.user_id
    account = database.db.accounts.find_one({
        '_id': user_id,
    })

    try:
        ph.verify(account['password'], req.content['old_password'])
    except argon2.exceptions.VerifyMismatchError:
        return ServiceResponse(403, errors=api_error('invalid_old_password'))

    error = mailing.send_mail(account['email'], 'Zmiana hasła w PreExam.',
                              mailing.PASSWORD_CHANGED)
    return database.update_one('accounts', user_id, {
        'password': ph.hash(req.content['new_password'])
    }) if not error else ServiceResponse(500, errors=error)
