from typing import List, Optional, Dict, Tuple

from typing_extensions import TypedDict


class ApiError(TypedDict):
    code: int
    name: str
    description: str
    field: Optional[str]
    entities: Optional[List[int]]


def api_error(name: str,
              extra_info: List[str] = None,
              field: str = None,
              entities: List[int] = None) -> ApiError:
    """Items in extra_info are put to placeholders in error's description"""
    code = ERRORS[name][0]
    if extra_info:
        description = ERRORS[name][1].format(*extra_info)
    else:
        description = ERRORS[name][1]
    api_error: ApiError = {
        'code': code,
        'name': name,
        'description': description,
        'field': field,
        'entities': entities,
    }
    return api_error


def to_polish(error: ApiError) -> ApiError:
    """Returns name with description in Polish."""
    orginal_dsc = ERRORS[error['name']][1]
    # Find words not present in orginal_dsc but present in formated text.
    # These worlds are extra info.
    # In addicion strip them from unwanted chars.
    extra_info = [
        w.strip('{}.,') for w in error['description'].split(' ')
        if w not in orginal_dsc.split(' ')
    ]
    if extra_info:
        error['description'] = ERRORS[error['name']][2].format(*extra_info)
    else:
        error['description'] = ERRORS[error['name']][2]
    return error


ERRORS: Dict[str, Tuple[int, str, str]] = {
    'invalid_json':                         (40001, 'JSON docuemt is invalid.', 'Nie poprawna składnia dokumentu JSON.'),
    'invalid_login_or_password':            (40101, 'Invalid authorization data.', 'Niepoprawne dane logowania.'),
    'login_required':                       (40102, 'Login is required.', 'Wymagane zalogowanie.'),
    'invalid_session_token':                (40103, 'Invalid session token.', 'Niepoprawny token sesji.'),
    'session_expired':                      (40104, 'Session expired.', 'Sesja wygasła.'),
    'account_blocked':                      (40105, 'Account blocked.', 'Konto zablokowane.'),
    'invalid_registration_code':            (40301, 'Invalid registration code.', 'Niepoprawny kod potwierdzenia rejestracji.'),
    'account_already_exists':               (40302, 'Account already exists.', 'Konto już istnieje.'),
    'registration_code_expired':            (40303, 'Registration code expired.', 'Kod potwierdzenia rejestracji wygasł.'),
    'invalid_password_reset_code_or_email': (40304, 'Invalid password reset code or email.', 'Niepoprawny email lub kod resetu hasła.'),
    'password_reset_code_expired':          (40305, 'Password change code expired.', 'Kod zminay hasła wygasł.'),
    'invalid_role':                         (40306, 'Not enought privileges.', 'Brak wystarczających uprawnień.'),
    'username_taken':                       (40307, 'Username taken.', 'Taka nazwa użytkownika już istnieje.'),
    'quiz_session_not_started':             (40308, 'Quiz not started.', 'Nierozpocząto quziu.'),
    'question_already_answered':            (40309, 'Question already answered.', 'Już udzielono odpowiedzi na pytanie.'),
    'invalid_old_password':                 (40310, 'Invalid old password.', 'Niepoprawne stare hasło.'),
    'invalid_state_or_nonce':               (40311, 'Invalid oauth state or nonce.', 'Niepoprawny parametr state lub nonce.'),
    'cannot_block_admin':                   (40312, 'You cannot block admin\'s account.', 'Nie można zablokować konta admina.'),
    'cannot_delete_admin':                  (40315, 'You cannot delete admin\'s account.', 'Nie można usunąć konta admina.'),
    'cannot_change_admins_role':            (40316, 'You cannot change admin\'s account role', 'Nie można zmienić roli konta admina.'),
    'question_not_found':                   (40401, 'Question was not found.', 'Nie odnalezino pytania.'),
    'account_not_found':                    (40402, 'Account not found.', 'Nie odnalezino konta.'),
    'questions_not_found':                  (40403, 'Questions not found.', 'Nie odnalezino pytania.'),
    'quizze_not_found':                     (40404, 'Quiz not found.', 'Nie odnalezino quizu.'),
    'quiz_not_found':                       (40405, 'Quiz not found.', 'Nie odnalezino quizu.'),
    'history_not_found':                    (40406, 'History not found.', 'Nie odnalezino historii.'),
    'image_not_found':                      (40407, 'Image not found.', 'Nie odnalezino obrazu.'),
    'categorie_not_found':                  (40408, 'Category not found.', 'Nie odnalezino kategorii.'),
    'resource_not_found':                   (40409, 'API resource not found.', 'Nie odnaleziono zasobu API.'),
    'quiz_is_not_long':                     (40901, 'Given quiz is not long one.', 'Ten quiz nie jest długim quizem.'),
    'quiz_is_not_short':                    (40902, 'Given quiz is not short one.', 'Ten quiz nie jest krótkim quizem.'),
    'not_enough_answers':                   (40903, 'Not all questions are answered.', 'Nie odpowiedziano na wszystkie pytania.'),
    'question_index_out_of_range':          (40904, 'Question index is out of range.', 'Indeks pytania spoza zakresu.'),
    'too_many_answers':                     (40905, 'To many answers for a given quiz.', 'Podano zbyt dużo odpowiedzi na quiz.'),
    'wrong_number_of_answers':              (40906, 'Wrong number of answers', 'Nieprawidłowa ilość odpowiedzi na pytanie.'),
    'question_answer_mismatch':             (40906, 'This question is answered with {} field in answer body.', 'Na to pytanie należy odpowiedzieć polem {} w treści odpowiedzi.'),
    'missing_answers':                      (40907, 'Missing answers for some questions(look to entities).', 'Brakuje odpowiedzi na parę pytań. Patrz pole entities.'),
    'unsupported_media_type':               (41501, 'Content-Type header is diffrent than {}.', 'Nagłówek Content-Type jest różny od {}.'),
    'invalid_type':                         (42201, 'Invalid data type. Expected {}, but got {}.', 'Nieprawidłowy typ wartości ostrzymano {}, ale spodziewano się {}.'),
    'required_key_missing':                 (42202, 'Field is required.', 'Pole jest wymagane.'),
    'unknown_field':                        (42203, 'Unknown field.', 'Nieznane pole.'),
    'string_too_long':                      (42204, 'String is too long. Maximum {}.', 'Napis za długi. Maksimum {}.'),
    'string_too_short':                     (42205, 'String is too short. Minimum {}.', 'Napis za krótki. Minimum {}.'),
    'number_too_low':                       (42206, 'Number is too low. Minimum {}.', 'Liczba zbyt niska. Minumum {}.'),
    'number_too_high':                      (42207, 'Number is too high. Maximum {}.', 'Liczba zbyt wysoka. Maksimum {}.'),
    'pattern_mismatch':                     (42208, 'String does not mach pattern. Pattern: {}.', 'Napis nie pasuje do wyrażenia regularnego. Wyrażenie: {}.'),
    'invalid_value':                        (42209, 'Invalid value. Expected be one of {}.', 'Niepoprawna wartość. Spodziwano się jednej z {}.'),
    'list_too_big':                         (42210, 'Too many list elements. Maxumim {}.', 'Lista jest zbyt duża. Maksimum elementów {}.'),
    'image_too_big':                        (42212, 'Image is bigger than 1 MB.', 'Obraz jest większy niż 1 MB'),
    'image_is_not_raw_png':                 (42213, 'Request content is not png file.', 'Podany plik nie ma formatu png.'),
    'duplicate_entry':                      (42214, 'Field is a duplicate.', 'Pole jest duplikatem.'),
    'required_key_missing_unless':          (42215, 'Field is required unless defined {}.', 'Pole jest wymagane jeśli nie zdefiniowano {}.'),
    'internal_error':                       (50001, 'Internal API eror.', 'Wewnętrzny błąd API.'),
    'email_api_error':                      (50002, 'Email API name.', 'Błąd przy wysyłaniu maila.'),
}
