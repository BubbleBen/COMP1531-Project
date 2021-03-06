import pytest
import jwt
from auth import auth_login, auth_logout, auth_register, reset_request, reset_reset
from channel import channels_create, channel_invite, channel_join, channel_leave, channel_add_owner, channel_remove_owner, channel_details, channels_list, channels_listall, channel_messages
from message import send_later, msg_send, msg_remove, msg_edit, msg_react, msg_unreact, msg_pin, msg_unpin
from profile import user_profile, user_profile_setname, user_profile_email, user_profile_sethandle, user_profile_uploadphoto, users_all, standup_start, standup_active, standup_send, search, admin_userpermission_change
from helper_functions import check_email, user_from_token, user_from_uid, max_20_characters, channel_index, find_channel, find_msg, check_channel_owner, check_channel_member, check_slackr_owner, check_slackr_admin, check_in_channel, get_reacts
from class_defines import User, Channel, Mesg, Reacts, data
from exception import ValueError, AccessError
from datetime import datetime, timedelta, timezone
from time import time

def test_user_profile():
    # set up
    # user1(admin)
    registerDict1 = auth_register("kenny@gmail.com", "password", "kenny", "han")
    userID1 = registerDict1['u_id']
    token1 = registerDict1['token']
    # user2
    registerDict2 = auth_register("ken@gmail.com", "password2", "ken", "han")
    userID2 = registerDict2['u_id']
    token2 = registerDict2['token']
    # end of set up

    # testing
    # raises ValueError when user with u_id is not a valid user
    with pytest.raises(ValueError):
        userProfile = user_profile(token1, userID2)
    with pytest.raises(ValueError):
        userProfile = user_profile(token2, userID1)
    # with pytest,raises(AttributeError):
    #     userProfile = user_profile(token1, "@#$%^&*!")

def test_user_profile_setname():
    #user_profile_setname(token, firstname, lastname), no return value
    #SETUP TESTS BEGIN
    #create token:
    authRegDict = auth_register("benjamin.kah@student.unsw.edu.au", "password", "Ben", "Kah")
    userId = authRegDict["u_id"]
    token = authRegDict["token"]
    #SETUP TESTS END
    user_profile_setname(token, "Jeffrey", "Oh") #this function should pass
    userDict = user_profile(token, userId)
    assert userDict["name_first"] == "Jeffrey" #test that name has been changed
    assert userDict["name_last"] == "Oh"
    with pytest.raises(ValueError): #following should raise exceptions
        user_profile_setname(token, "This is a really long first name, more than 50 characters", "lmao")
    with pytest.raises(ValueError):
        user_profile_setname(token, "lmao", "This is a really long last name, more than 50 characters")
    with pytest.raises(ValueError):
        user_profile_setname(token, "This is a really long first name, more than 50 characters", "This is a really long last name, more than 50 characters")

def test_user_profile_email():
    #user_profile_setemail(token, email), no return value
    #SETUP TESTS BEGIN
    #create token:
    authRegDict = auth_register("benjamin.kah1@student.unsw.edu.au", "password", "Ben", "Kah")
    userId = authRegDict["u_id"]
    token = authRegDict["token"]
    #create second person's email:
    authRegDict2 = auth_register("jeffrey.oh@student.unsw.edu.au", "password", "Jeffrey", "Oh")
    userDict2 = user_profile(authRegDict2["token"], authRegDict2["u_id"])
    email2 = userDict2["email"]
    #SETUP TESTS END
    user_profile_email(token, "goodemail@student.unsw.edu.au") #this function should pass
    userDict = user_profile(token, userId)
    assert userDict["email"] == "goodemail@student.unsw.edu.au" #test that email has been changed
    with pytest.raises(ValueError): #following should raise exceptions
        user_profile_email(token, "bad email")
    with pytest.raises(ValueError):
        user_profile_email(token, email2) #using another user's email

def test_user_profile_sethandle():
    #user_profile_sethandle(token, handle_str), no return value
    #SETUP TESTS BEGIN
    #create token:
    authRegDict = auth_register("benjamin.kah2@student.unsw.edu.au", "password", "Ben", "Kah")
    userId = authRegDict["u_id"]
    token = authRegDict["token"]
    #SETUP TESTS END
    user_profile_sethandle(token, "good handle")
    userDict = user_profile(token, userId)
    assert userDict["handle_str"] == "good handle"
    with pytest.raises(ValueError):
        user_profile_sethandle(token, "This handle is way too long")

def test_standup_start():
    #standup_start(token, channel_id), returns time_finish
    #SETUP TESTS BEGIN
    #create new users:
    authRegDict = auth_register("benjamin.kah4@student.unsw.edu.au", "password", "Ben", "Kah")
    token = authRegDict["token"]
    authRegDict2 = auth_register("jeffrey.oh1@student.unsw.edu.au", "password", "Jeffrey", "Oh")
    token2 = authRegDict2["token"]
    #create channel
    chanCreateDict = channels_create(token, "test channel", True)
    chanId = chanCreateDict["channel_id"]
    channel_join(token, chanId)
    #SETUP TESTS END
    # low = datetime.now() + timedelta(seconds=4)
    # up = datetime.now() + timedelta(seconds=6)
    low_bound = time() + float(4.8)
    up_bound = time() + float(5.2)
    finish = standup_start(token, chanId, 5)
    standup_finish = finish["time_finish"]
    # low_bound = low.replace(tzinfo=timezone.utc).timestamp()
    # up_bound = up.replace(tzinfo=timezone.utc).timestamp()
    assert low_bound < standup_finish
    assert up_bound > standup_finish

    with pytest.raises(ValueError):
        assert standup_start(token, 5555, 5)    # channel_id is not a valid channel
    with pytest.raises(ValueError):
        assert standup_start(token2, chanId, 5) # token is invalid

def test_standup_send():
    #standup_send(token, channel_id, message), no return value
    #SETUP TESTS BEGIN
    #create new users:
    authRegDict = auth_register("benjamin.kah5@student.unsw.edu.au", "password", "Ben", "Kah")
    token = authRegDict["token"]
    authRegDict2 = auth_register("jeffrey.oh2@student.unsw.edu.au", "password", "Jeffrey", "Oh")
    token2 = authRegDict2["token"]
    #create channels:
    chanCreateDict = channels_create(token, "test channel", True)
    chanId = chanCreateDict["channel_id"]
    channel_join(token, chanId)
    chanCreateDict2 = channels_create(token, "test channel 2", True)
    chanId2 = chanCreateDict2["channel_id"]
    channel_join(token, chanId2)
    #SETUP TESTS END

    with pytest.raises(ValueError):
        assert standup_send(token, chanId, "this is sent before standup_start is called")

    #create time_finish
    finish = standup_start(token, chanId, 5)
    standup_finish = finish["time_finish"]

    standup_send(token, chanId, "Standup message")
    with pytest.raises(AccessError):
        assert standup_send(token2, chanId, "Standup message with user not a member of the channel")
    strOver1000 = "yeah bo" + "i"*1000
    with pytest.raises(ValueError):
        assert standup_send(token, chanId, strOver1000)
    with pytest.raises(ValueError):
        assert standup_send(token, chanId2, "Standup message with wrong chanId")

def test_search():
    #search(token, query_str), returns messages
    #SETUP TESTS BEGIN
    #create new users:
    authRegDict = auth_register("benjamin.kah6@student.unsw.edu.au", "password", "Ben", "Kah")
    token = authRegDict["token"]
    #create channel
    chanCreateDict = channels_create(token, "test channel", True)
    chanId = chanCreateDict["channel_id"]
    channel_join(token, chanId)
    #create messages
    msg_send(token, "New message sent", chanId)
    msg_send(token, "Another message", chanId)
    msg_send(token, "A completely different string", chanId)
    #SETUP TESTS END
    searchResultsList = search(token, "message") #first search query
    searchResultsList2 = search(token, "nothing to find") #second search query
    assert searchResultsList["messages"][1]["message"] == "New message sent" #search results should contain these strings
    assert searchResultsList["messages"][0]["message"] == "Another message"
    assert len(searchResultsList["messages"]) == 2
    assert len(searchResultsList2["messages"]) == 0 #list should be empty

def test_admin_userpermission_change():
    #admin_userpermission_change(token, u_id, permission_id), no return value
    #SETUP TESTS BEGIN
    #create new admin:
    authRegDict = auth_login("kenny@gmail.com", "password")
    token = authRegDict["token"]
    userId = authRegDict["u_id"]
    #create regular user:
    authRegDict2 = auth_register("jeffrey.oh3@student.unsw.edu.au", "password", "Jeffrey", "Oh")
    token2 = authRegDict2["token"]
    userId2 = authRegDict2["u_id"]
    #create channel from admin:
    chanCreateDict = channels_create(token, "test channel", True)
    chanId = chanCreateDict["channel_id"]
    channel_join(token, chanId)
    #add regular user to first channel:
    channel_invite(token, chanId, userId2)
    #SETUP TESTS END
    with pytest.raises(ValueError):
        assert admin_userpermission_change(token, userId, 0) #invalid permission_id
    with pytest.raises(ValueError):
        assert admin_userpermission_change(token, userId, 4)
    with pytest.raises(AccessError):
        assert admin_userpermission_change(token, 55555, 3) #invalid user ID

    user2 = user_from_token(token2)
    # check user2 is a member (not an owner or admin)
    assert check_slackr_owner(user2) == False
    assert check_slackr_admin(user2) == False

    # check user2 is an owner
    admin_userpermission_change(token, userId2, 1)
    assert check_slackr_owner(user2) == True
    assert check_slackr_admin(user2) == False

    # check user2 is an admin
    admin_userpermission_change(token, userId2, 2)
    assert check_slackr_owner(user2) == False
    assert check_slackr_admin(user2) == True

    # change user2 back to member
    admin_userpermission_change(token, userId2, 3)
    # check user2 cannot change permission of user1
    with pytest.raises(AccessError):
        admin_userpermission_change(token2, userId, 3)

    user = user_from_token(token)
    # check slackr owner can be made admin
    admin_userpermission_change(token, userId, 2)
    assert check_slackr_admin(user)
