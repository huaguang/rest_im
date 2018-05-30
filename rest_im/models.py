from django.db import models

# Create your models here.
class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    username = models.CharField( max_length = 30)
    password = models.CharField(verbose_name = '用户密码', max_length = 30)
    # uuid = models.CharField(verbose_name= 'uuid', max_length = 40)
    token = models.CharField(verbose_name= 'token', max_length = 300, blank = True, null = True)
    # token_expired = models.DateTimeField(blank = True, null = True)
    # viewed = models.BooleanField(verbose_name = '观看状态', default = False)
    created = models.DateTimeField(verbose_name = '创建时间', auto_now_add=True)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = verbose_name
        ordering = ('user_id',)

class Friend(models.Model):
    FRIENDSHIP_TYPE = (
        ('W', 'wait'),
        ('A', 'Accept'),
        ('R', 'remove'),
        ('D', 'Decline')
    )
    # friendship_id = models.AutoField(primary_key = True)
    sender_id = models.IntegerField()
    receiver_id = models.IntegerField()
    status = models.CharField(default = 'W', max_length = 1,  choices=FRIENDSHIP_TYPE)  # 1:wait   2:done   3:remove

    class Meta:
        unique_together=("sender_id", "receiver_id")

class Message(models.Model):
    MESSAGE_CONTENT_TYPE = (
        ('T', 'Text'),
        ('I', 'Img'),
        ('A', 'Audio'),
        ('V', 'Medio'),
    )
    MESSAGE_NOTICE_TYPE = (
        ('P', 'Private'),
        ('S', 'System'),
        ('G', 'Group'),
    )
    msg_content = models.TextField(max_length = 1000)
    msg_content_type = models.CharField(default = 'T', max_length = 1,  choices=MESSAGE_CONTENT_TYPE)  #0: text; 1:img; 2:audio;  3:video
    msg_notice_type = models.CharField(default = 'P', max_length = 1,  choices=MESSAGE_NOTICE_TYPE) 
    msg_sender_id = models.IntegerField()
    msg_receiver_id = models.IntegerField()
    msg_status = models.BooleanField(default = False) # whether this message is read
    msg_create = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('msg_create',)

