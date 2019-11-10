from flask import Flask, request, flash
from datetime import datetime
from json import dumps
from class_defines import data, Channel, User
from Error import AccessError
#from helper_functions import check_in_channel
from uuid import uuid4

#TESTING:
import pytest
from Error import AccessError

app = Flask(__name__)

# given a token, returns acc with that token
def user_from_token(token):
    global data
    for acc in data['accounts']:
        # print(acc.token)
        # print(type(acc.token))
        # print(type(token))
        # print(token)
        if acc.token == token:
            return acc
    raise AccessError('token does not exist for any user')

# given u_id, returns acc with that u_id
def user_from_uid(u_id):
    global data
    for acc in enumerate(data['accounts']):
        if int(acc.user_id) == int(u_id):
            return acc
    raise AccessError('u_id does not exist for any user')

def max_20_characters(name):
    if len(name) <= 20:
        return True 
    else:
        return False

def channel_index(channel_id):
    global data
    index = 0
    for i in data['channels']:
        #TESTING:
        #print(i.channel_id)
        if int(i.channel_id) == int(channel_id):
            return index
        index = index + 1
    
    raise ValueError('channel does not exist')

def channel_create(token, name, is_public):
    global data

    if max_20_characters(name) == False:
        raise ValueError('name is more than 20 characters')
    else: 
        channel_id = int(uuid4())
        data['channels'].append(Channel(name, is_public, channel_id, False))
        index = channel_index(channel_id)
        data['channels'][index].owners.append(user_from_token(token))
        data['channels'][index].members.append(user_from_token(token))

        # add channel to user's list of channels 
        acct = user_from_token(token)
        acct.in_channel.append(channel_id)
    
    return dumps({
        'channel_id' : channel_id
    })

def test_channels_create():
    channel_create(1234, 'Mychannel', True)
    with pytest.raises(Exception): # Following should raise exceptions
        channels_create('valid token', 'This is a string that is much longer than the max length', True)

@app.route('/channel/invite', methods = ['POST'])
def channel_invite():
    #token, channel_id, u_id
    global data
    token = request.form.get('token')
    channel_id = int(request.form.get('channel_id'))
    u_id = int(request.form.get('u_id'))

    # raise AccessError if authorised user not in channel, check if token is in user class
    

    # raise ValueError if channel_id doesn't exist (channel_index)
    #check_in_channel(token, channel_index(channel_id)) # use Ben's funct.

    # raise ValueError if u_id doesnt refer to a valid user:TODO

    index = channel_index(channel_id)
    data['channels'][index].members.append(u_id)
    print(data['channels'][index].members)
    return dumps({
    })

@app.route('/channel/join', methods = ['POST'])
def channel_join():
    global data
    token = request.form.get('token')
    channel_id = int(request.form.get('channel_id'))

    # raise ValueError if channel_id doesn't exist (channel_index)
    index = channel_index(channel_id)

    # raise AccessError if channel is Private & authorised user is not an admin
    if data['channels'][index].is_public == False:
        # check if authorised user is an admin
        valid = 0
        for admin_acc in data['channels'][index].admins: 
            if admin_acc.token == token:
                valid = 1
        if valid == 0:
            raise AccessError('authorised user is not an admin of private channel')

    acct = user_from_token(token)
    data['channels'][index].members.append(acct)

    #print(data['channels'][index].members[1].token) #returns token of 2nd member (1st member is one who created channel)

    return dumps({
    })

@app.route('/channel/leave', methods = ['POST'])
def channel_leave():
    global data
    token = request.form.get('token')
    channel_id = int(request.form.get('channel_id'))

    # raise ValueError if channel_id doesn't exist (channel_index)
    index = channel_index(channel_id)

    acct = user_from_token(token)
    data['channels'][index].members.pop(acct)

    if acct in data['channels'][index].owners:
        data['channels'][index].owners.pop(acct)
    if acct in data['channels'][index].admins:
        data['channels'][index].admins.pop(acct)

    return dumps({
    })

@app.route('/channel/addowner', methods = ['POST'])
def channel_add_owner():
    global data
    token = request.form.get('token')
    channel_id = int(request.form.get('channel_id'))
    u_id = int(request.form.get('u_id'))

    # raise ValueError if channel_id doesn't exist (channel_index)
    index = channel_index(channel_id)

    # check if user with u_id is already owner 
    if user_from_uid(u_id) in data['channels'][index].owners:
        raise ValueError('User with u_id is already an owner')

    # check if authorised user is an owner of this channel
    if user_from_token(token) not in data['channels'][index].owners:
        raise AccessError('Authorised user not an owner of this channel')
    
    acct = user_from_uid(u_id)
    data['channels'][index].owners.append(acct)

    return dumps({
    })

@app.route('/channel/removeowner', methods = ['POST'])
def channel_remove_owner():
    global data
    token = request.form.get('token')
    channel_id = int(request.form.get('channel_id'))
    u_id = int(request.form.get('u_id'))

    # raise ValueError if channel_id doesn't exist (channel_index)
    index = channel_index(channel_id)

    # raise ValueError if u_id is not an owner
    if user_from_uid(u_id) not in data['channels'][index].owners:
        raise ValueError('u_id is not an owner of the channel')

    # raise AccessError if token is not an owner of this channel
    if user_from_token(token) not in data['channels'][index].owners:
        raise AccessError('authorised user is not an owner of this channel')
    
    acct = user_from_uid(u_id)
    data['channels'][index].owners.pop(acct)

    return dumps({
    })

@app.route('/channel/details', methods = ['GET'])
def channel_details():
    global data
    token = request.args.get('token')
    channel_id = request.args.get('channel_id')


    #TESTING
    print("token: "+token)
    print("channel_id: "+channel_id)
    #TESTING

    # raise ValueError if channel_id doesn't exist (channel_index)
    index = channel_index(channel_id)

    # raise AccessError if authorised user isn't in channel
    #if user_from_token(token) not in data['channels'][index].members or user_from_token(token) not in data['channels'][index].owners or user_from_token(token) not in data['channels'][index].admins:
    #    raise AccessError('authorised user is not in channel')

    #TODO:
    #create a list of names of users of owners & all members, then append to it from the user class. 
    #user class itself is not JSON serialisable 

    channel_name = data['channels'][index].name

    owners_uid = []
    members_uid = []

    
    for i in data['channels'][index].owners:
        owners_uid.append(i.handle)
    
    #for i in data['channels'][index].members:
    #   members_uid.append(i.handle)
    
    #owner_members = data['channels'][index].owners
    #all_members = data['channels'][index].members

    return dumps({
        'name': channel_name,
        'owners': owners_uid,
        'members': members_uid
    })

@app.route('/channel/list', methods = ['GET'])
def channel_list():
    global data
    token = request.args.get('token')

    # testing set up
    #data['channels'][0].members.append(user_from_token(token))
    # testing set up

    channel_list = []
    for channel in data['channels']:
        for acct in channel.members:
            if acct.token == token:
                channel_list.append(channel.name)

    return dumps({
        'channels': channel_list
    })

@app.route('/channel/listall', methods = ['GET'])
def channel_listall():
    global data
    token = request.args.get('token')

    channel_list = []
    for channel in data['channels']:
        channel_list.append('Name: '+channel.name +' Public? '+ channel.is_public)

    return dumps({
        'channels': channel_list
    })

@app.route('/channel/messages', methods = ['GET'])
def channel_messages():
    global data
    token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))
    start = int(request.args.get('start'))

    # raise ValueError if channel_id doesn't exist (channel_index)
    index = channel_index(channel_id)

    # raise AccessError if authorised user isn't in channel
    if user_from_token(token) not in data['channels'][index].members or user_from_token(token) not in data['channels'][index].owners or user_from_token(token) not in data['channels'][index].admins:
        raise AccessError('authorised user is not in channel')

    # raise ValueError if start is greater than no. of total messages
    no_total_messages = len(data['channels'][index].messages)
    if start > no_total_messages:
        raise ValueError('start is greater than no. of total messages')
    
    messages = []
    i = start
    for i in data['channels'][index].messages[i]:
        message = {}
        message['message_id'] = data['channels'][index].messages[i].message_id
        message['u_id'] = data['channels'][index].messages[i].sender
        message['message'] = data['channels'][index].messages[i].message
        message['time_created'] = data['channels'][index].messages[i].create_time
        message['reacts'] = data['channels'][index].messages[i].reaction
        message['is_pinned'] = data['channels'][index].messages[i].is_pinned

        messages.append(message)
        if i == (start + 50):
            end = i
            break
        if i == no_total_messages:
            end = -1
            break
    
    return dumps({
        'messages': messages,
        'start': start,
        'end': end
    })

if __name__ == '__main__':
    app.run(port = 5022, debug=True)
