'''auth functions'''
import jwt
from uuid import uuid4
from exception import ValueError, AccessError
from class_defines import data, User, perm_owner
from helper_functions import check_email

def auth_login(email, password):
    global data
    valid = False
    i = 0
    check_email(email)
    for counter, acc in enumerate(data['accounts']):
        if acc.email == email and acc.password == password:
                i = counter
                user_id = acc.u_id
                valid = True
    if (not(valid)):
        raise ValueError(description = 'email and/or password does not match any account')
    token = jwt.encode({'email': email}, password, algorithm = 'HS256')
    data['accounts'][i].token = token.decode('utf-8')
    return {'u_id': user_id, 'token': token.decode('utf-8')}

def auth_logout(token):
    global data
    if token == '':
        return {'is_success': False}
    for acc in data['accounts']:
        if token == acc.token:
            acc.token = ''
            return {'is_success': True}
    return {'is_success': False}

def auth_register(email, password, first, last):
    global data

    check_email(email)

    if (len(password) <= 6): # if password is too short
        raise ValueError(description = 'Password too short')

    if (not(1 <= len(first) and len(first) <= 50)): # if name is not between 1 and 50 characters long
        raise ValueError(description = 'first name must be between 1 and 50 characters long')

    if (not(1 <= len(last) and len(last) <= 50)):   # if name is not between 1 and 50 characters long
        raise ValueError(description = 'last name must be between 1 and 50 characters long')

    handle = first + last
    if len(handle) > 20:
        handle = handle[:20]
    curr = 0
    new = 0
    for acc in data['accounts']:
        if acc.email == email:  # if email is already registered
            raise ValueError(description = 'email already matches an existing account')
        if acc.handle.startswith(first + last): # Checking exact name repetitions
            if handle == first + last:  # If handle is base concantate case
                handle += '0'   # Add zero on end
            else:   # If NOT base case, take off number on end and add 1
                new = int(acc.handle.split(first + last)[1]) + 1
                if curr <= new: # If new number is larger replace
                    handle = first + last + str(new)
                    curr = new
        elif acc.handle == (first + last)[:20]: # If name is truncate case and is already 20 characters
            handle += '0'
    if len(handle) > 20:    # If handle is too long make handle the hexadecimal number of account_count
        handle = hex(data['account_count'])
    user_id = data['account_count']
    data['account_count'] += 1
    handle.lower()
    token = jwt.encode({'email': email}, password, algorithm = 'HS256')
    token = token.decode('utf-8')
    data['accounts'].append(User(email, password, first, last, handle, token, user_id))
    if user_id == 0:
        data['accounts'][user_id].perm_id = perm_owner
    return {'u_id': user_id,'token': token}

def reset_request(email):
    global data
    for acc in data['accounts']:
        if acc.email == email:
            resetcode = str(uuid4())
            acc.reset_code = resetcode
    return {}

def reset_reset(code, password):
    global data
    for acc in data['accounts']:
        if code == acc.reset_code:
            if len(password) >= 6:
                acc.password = password
                acc.reset_code = ''
                acc.token = ''
                return {}
            else:
                raise ValueError(description = 'password is too short (min length of 6)')
    raise ValueError(description = 'reset code is not valid')
