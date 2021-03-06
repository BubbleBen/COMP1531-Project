'''channel functions'''
from flask import Flask, request, flash
from class_defines import data, Channel, User, Mesg, perm_admin, perm_member, perm_owner
from exception import ValueError, AccessError
from auth import auth_register
import json
from message import msg_send
from helper_functions import user_from_uid, max_20_characters, user_from_token, channel_index

app = Flask(__name__)

def channels_create(token, name, is_public):
    global data

    if max_20_characters(name) == False:
        raise ValueError(description = 'name is more than 20 characters')
    channel_id = data['channel_count']
    data['channel_count'] += 1
    data['channels'].append(Channel(name, is_public, channel_id))
    index = channel_index(channel_id) 
    acct = user_from_token(token)
    acct = data['accounts'][0]
    data['channels'][index].owners.append(acct.u_id)
    data['channels'][index].members.append(acct.u_id)

    # add channel to user's list of channels
    acct.in_channel.append(channel_id)
    
    return {
        'channel_id': channel_id
    }

def channel_invite(token, channel_id, u_id):
    global data

    # raise AccessError if authorised user not in channel
    # check if channel_id is part of User's in_channel list
    acct = user_from_token(token)
    if (channel_id in acct.in_channel) == False:
        raise AccessError(description = 'authorised user is not in channel')

    # raise ValueError if channel_id doesn't exist (channel_index)
    index = channel_index(channel_id)
    data['channels'][index].members.append(u_id)

    # add channel to user's list of channels 
    acct = user_from_uid(u_id)
    acct.in_channel.append(channel_id)

    return {}

def channel_join(token, channel_id):
    global data

    # raise ValueError if channel_id doesn't exist (channel_index)
    index = channel_index(channel_id)
    acct = user_from_token(token)
    # raise AccessError if channel is Private & authorised user is not an admin
    if data['channels'][index].is_public == False:
        # check if authorised user is an admin
        valid = 0
        if acct.perm_id < perm_member:
            valid = 1
            data['channels'][index].owners.append(acct.u_id)
        if valid == 0:
            raise AccessError(description = 'authorised user is not an admin of private channel')
    
    acct.in_channel.append(channel_id)
    data['channels'][index].members.append(acct.u_id)
    return {}
    
def channel_leave(token, channel_id):
    global data
    # raise ValueError if channel_id doesn't exist (channel_index)
    index = channel_index(channel_id)
    acct = user_from_token(token)
    
    # raise AccessError if authorised user not in channel
    if (channel_id in acct.in_channel) == False:
        raise AccessError('authorised user is not in channel')

    for j in data['channels'][index].members:
        if j == acct.u_id:
            # use .remove() instead of .pop() as .remove() takes in the actual element
            data['channels'][index].members.remove(j) 
    
    for j in data['channels'][index].owners:
        if j == acct.u_id:
            data['channels'][index].owners.remove(j)

    return {}

def channel_add_owner(token, channel_id, u_id):
    global data

    # raise ValueError if channel_id doesn't exist (channel_index)
    index = channel_index(channel_id)

    # check if user with u_id is already owner 
    if user_from_uid(u_id).u_id in data['channels'][index].owners:
        raise ValueError(description = 'User with u_id is already an owner')

    # check if authorised user is an owner of this channel
    if user_from_token(token).u_id not in data['channels'][index].owners:
        raise AccessError(description = 'Authorised user not an owner of this channel')
    
    data['channels'][index].owners.append(u_id)

    return {}

def channel_remove_owner(token, channel_id, u_id):
    global data

    # raise ValueError if channel_id doesn't exist (channel_index)
    index = channel_index(channel_id)

    # raise ValueError if u_id is not an owner
    if u_id not in data['channels'][index].owners:
        raise ValueError(description = 'u_id is not an owner of the channel')

    # raise AccessError if token is not an owner of this channel
    if user_from_token(token).u_id not in data['channels'][index].owners:
        raise AccessError(description = 'authorised user is not an owner of this channel')
    
    data['channels'][index].owners.remove(u_id)

    return {}

def channel_details(token, channel_id):
    global data

    # raise ValueError if channel_id doesn't exist (channel_index)
    index = channel_index(channel_id)

    # raise AccessError('authorised user is not in channel')
    acct = user_from_token(token)
    if not(channel_id in acct.in_channel):
        raise AccessError(description = 'authorised user is not in channel')

    channel_name = data['channels'][index].name

    owners_dict = []
    members_dict = []

    for i in data['channels'][index].owners:
        owner_member = user_from_uid(i)
        owners_dict.append({'u_id': i, 'name_first': owner_member.name_first, 'name_last': owner_member.name_last, 'profile_img_url': owner_member.prof_pic})
    
    for i in data['channels'][index].members:
        member = user_from_uid(i)
        members_dict.append({'u_id': i, 'name_first': member.name_first, 'name_last': member.name_last, 'profile_img_url': member.prof_pic})

    return {
        'name': channel_name,
        'owner_members': owners_dict,
        'all_members': members_dict
    }

def channels_list(token):
    global data

    channel_list = []
    for channel in data['channels']:
        for user_id in channel.members:
            if user_id == user_from_token(token).u_id:
                list_dict = {'channel_id':channel.channel_id, 'name':channel.name}
                channel_list.append(list_dict)
    return {
        'channels': channel_list
    }

def channels_listall(token):
    global data

    channel_list = []
    for channel in data['channels']:
        list_dict = {'channel_id': channel.channel_id, 'name': channel.name}
        channel_list.append(list_dict)
    return {
        'channels': channel_list
    }

def channel_messages(token, channel_id, start):
    global data

    # get the current user
    curr_user = user_from_token(token)

    # raise ValueError if channel_id doesn't exist (channel_index)
    index = channel_index(channel_id)

    # raise AccessError if authorised user isn't in channel
    if curr_user.u_id not in data['channels'][index].members:
        raise AccessError(description = 'authorised user is not in channel')

    # raise ValueError if start is greater than no. of total messages
    no_total_messages = len(data['channels'][index].messages)
    if start > no_total_messages:
        raise ValueError(description = 'start is greater than no. of total messages')
    
    end = -1
    list_messages = []
    i = start

    for item in data['channels'][index].messages[i:]:
        message = {}
        message['message_id'] = item.message_id
        message['u_id'] = item.sender
        message['message'] = item.message
        message['time_created'] = item.create_time
        message['is_pinned'] = item.is_pinned
        message['reacts'] = []
        for react in item.reactions:
            reacter_list = []
            reacter_list.append(react.reacter)
            message['reacts'].append({'react_id': react.react_id, 'u_ids': reacter_list, 'is_this_user_reacted': (curr_user.u_id in item.reacted_user)})

        i = i + 1
        list_messages.append(message)
        if i == no_total_messages:
            end = -1
            break
        if i == (start + 50):
            end = i
            break
    
    return {
        'messages': list_messages,
        'start': start,
        'end': end
    }

if __name__ == '__main__':
    app.run(port = 5022, debug=True)
