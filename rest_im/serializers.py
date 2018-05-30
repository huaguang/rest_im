from rest_framework import serializers
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_im.models import User,Message,Friend

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        # 指定序列化器需要作用的模型
        model = User
        # 指定序列化器的模型字段
        fields = (
            'user_id',
            'username',
            'password',
            'token',
            'created',
        )

class FriendSerializer(serializers.ModelSerializer):
    class Meta:
        # 指定序列化器需要作用的模型
        model = Friend
        # 指定序列化器的模型字段
        fields = (
            'sender_id',
            'receiver_id',
            'status',
        )

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = (
            'msg_content',
            'msg_content_type',
            'msg_notice_type',
            'msg_sender_id',
            'msg_receiver_id',
            'msg_status',
            'msg_create'
            )
