from django.shortcuts import render

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_im.models import User, Message, Friend
from rest_im.serializers import UserSerializer, MessageSerializer,FriendSerializer
from django.db.models import Q
from rest_im.token import *
from functools import wraps
import uuid

# Create your views here.
class JsonResponse(HttpResponse):
    def __init__(self, data, token = None, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JsonResponse, self).__init__(content, **kwargs)
        if token:
            super(JsonResponse, self).set_cookie('token', token)

class ErrorResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        super(ErrorResponse, self).__init__(data, status = status.HTTP_400_BAD_REQUEST)

def check_password(username, password):
    try:
        user = User.objects.get(username = username, password = password)
    except User.DoesNotExist:
        return None
    return user

def authenticate(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if 'token' in request.COOKIES:
            token = request.COOKIES['token']
            # print('Token is %s' % token)
            # print(check_token(token))
            user_id = check_token(token)
            if user_id:
                kwargs['user_id'] = user_id
                return func(request, **kwargs)
        return HttpResponse('登录界面显示')
    return wrapper

@csrf_exempt
def login(request):
    print(request.POST)
    if 'username' in request.POST and 'password' in request.POST:
        print('username is %s\t password is %s' %(request.POST['username'], request.POST['password']))
        user = check_password(request.POST['username'], request.POST['password'])
        if user:
            token = create_token(user.user_id)
            return JsonResponse({'login result':'login success'}, token)
        else:
            return ErrorResponse('arguments not right')
    else:
        print("需要username和password才能登录")
        return  HttpResponse('需要username和password才能登录')

@csrf_exempt
@authenticate
def logout(request, **kwargs):
    User.objects.filter(user_id = kwargs['user_id']).update(token = None)
    return HttpResponse("logout success")


@csrf_exempt
@authenticate
def user_list(request, **kwargs):
        users = User.objects.all()
        user_serializer = UserSerializer(users, many = True)
        return JsonResponse(user_serializer.data)

@csrf_exempt
@authenticate
def user(request, **kwargs):
    try:
        if request.method == 'GET':
            if 'user_id' in request.GET:
                user_id = request.GET['user_id'] 
            else:
                user_id = kwargs['user_id']
        else:
            user_data = JSONParser().parse(request)
            user_id = kwargs['user_id']

        user = User.objects.get(user_id = user_id)
    except User.DoesNotExist:
        if request.method == 'POST':
            # user_data['uuid'] = str(uuid.uuid5(uuid.NAMESPACE_DNS, user_data['username'])) #username可能不存在
            user_serializer = UserSerializer(data = user_data)
            if user_serializer.is_valid():
                user_serializer.save()
                return JsonResponse(user_serializer.data)
            return JsonResponse(user_serializer.errors, status = status.HTTP_400_BAD_REQUEST)
        else:
            return HttpResponse({'id为%d的用户不存在'.format(user_id)}, status = status.HTTP_404_NOT_FOUND)

    if request.method == 'POST':
        return HttpResponse({'error':'user has existed'}, status = status.HTTP_404_NOT_FOUND)

    elif request.method == 'GET':
        user_serializer = UserSerializer(user)
        return JsonResponse(user_serializer.data)

    elif request.method == 'PUT':
        user_serializer = UserSerializer(user, data = user_data)
        if user_serializer.is_valid():
            user_serializer.save()
            return JsonResponse(user_serializer.data)
        return JsonResponse(user_serializer.errors, status = status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        user.delete()
        return HttpResponse("delete success", status = status.HTTP_204_NO_CONTENT)


@csrf_exempt
@authenticate
def user_msg(request, **kwargs):
    if request.method == 'GET':
        if 'limit' in  request.GET and request.GET['limit'].isdigit():
            limit = request.GET['limit']
            msgs = Message.objects.filter(Q(msg_sender_id = kwargs['user_id'])| Q(msg_receiver_id = kwargs['user_id']) ).order_by('-id')[0:int(limit)]
        else:
            msgs = Message.objects.filter(user_id = kwargs['user_id'])
        # print(type(request.GET['limit']))
        msgs_serializer = MessageSerializer(msgs, many = True)
        return JsonResponse(msgs_serializer.data)

    elif request.method == 'POST':
        message_data = JSONParser().parse(request)
        print((message_data))
        message_data['msg_sender_id'] = kwargs['user_id']
        message_serializer = MessageSerializer(data = message_data)
        if message_serializer.is_valid():
            message_serializer.save()
            return JsonResponse(message_serializer.data)
        return JsonResponse(message_serializer.errors, status = status.HTTP_400_BAD_REQUEST)

@csrf_exempt
@authenticate
def user_friend(request, **kwargs):
    if request.method == 'GET': #query user's all friends
        friends = Friend.objects.filter(Q(sender_id = kwargs['user_id'])|Q(receiver_id = kwargs['user_id']), status = 'A' )
        friends_serializer = FriendSerializer(friends, many = True)
        return JsonResponse(friends_serializer.data)

    elif request.method == 'POST': #send a request for  add a new friend
        friend_data = JSONParser().parse(request)
        friend_data['status'] = 'W'
        friend_data['sender_id'] = kwargs['user_id']

        friend_serializer = FriendSerializer(data = friend_data)
        if friend_serializer.is_valid():
            friend_serializer.save()
            add_friend_msg = {
                "msg_content": "you have a request for adding friend from {}".format(102),
                "msg_notice_type": "S",
                "msg_sender_id": kwargs['user_id'],
                "msg_receiver_id": friend_data['receiver_id']
            }
            Message.objects.create(**add_friend_msg)
            return JsonResponse(friend_serializer.data)
        return JsonResponse(friend_serializer.errors, status = status.HTTP_400_BAD_REQUEST)

    elif request.method == 'PUT': # accept/decline new friend request
        friend_data = JSONParser().parse(request)
        response_add_friend_msg = {
                "msg_content": "you adding friend request has been ",
                "msg_notice_type": "S",
                "msg_sender_id": kwargs['user_id'],
                "msg_receiver_id": friend_data['sender_id']
        }
        if friend_data['accept'] == '1': #accept
            response_add_friend_msg['msg_content'] = response_add_friend_msg['msg_content'] + 'accepted'
            Message.objects.create(**response_add_friend_msg)

            friends = Friend.objects.filter(sender_id = friend_data['sender_id'], receiver_id = kwargs['user_id']).update(status = 'A')
            return JsonResponse(friend_data)
        else: #decline, 在给sender_id发送一次通知后，删除此条消息
            response_add_friend_msg['msg_content'] = response_add_friend_msg['msg_content'] + 'declined'
            Message.objects.create(**response_add_friend_msg)

            friends =  Friend.objects.filter(sender_id = friend_data['sender_id'], receiver_id = kwargs['user_id']).update(status = 'D')
            return JsonResponse(friend_data,status = status.HTTP_204_NO_CONTENT)

    elif request.method == 'DELETE':
        friend_data = JSONParser().parse(request)
        friends = Friend.objects.filter(Q(sender_id = kwargs['user_id'], receiver_id = friend_data['receiver_id']) | Q(receiver_id = kwargs['user_id'], sender_id = friend_data['receiver_id']))
        if len(friends) == 1:
            response_delete_friend_msg = {
                    "msg_content": "{} delete you from his friend list".format(kwargs['user_id']),
                    "msg_notice_type": "S",
                    "msg_sender_id": kwargs['user_id'],
                    "msg_receiver_id":friends[0].receiver_id if kwargs['user_id'] == friends[0].sender_id else friends[0].sender_id
            }
            Message.objects.create(**response_delete_friend_msg)
            friends[0].delete()
            return HttpResponse("delete success", status = status.HTTP_204_NO_CONTENT)
        else:
            return HttpResponse('(%d,%d) 数量为%d'%(user_id, friend_data['receiver_id'], len(friends)), status = status.HTTP_400_BAD_REQUEST)
