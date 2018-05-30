import time
from django.core import signing
import hashlib
from django.core.cache import cache
from rest_im.models import User 

HEADER = {'typ': 'JWP', 'alg': 'default'}
KEY = 'this is a test key'
SALT = 'www.hahaha.com'
TIME_OUT = 30 * 60  # 30min


def encrypt(obj):
    """加密"""
    value = signing.dumps(obj, key=KEY, salt=SALT)
    value = signing.b64_encode(value.encode()).decode()
    return value

def decrypt(src):
    """解密"""
    src = signing.b64_decode(src.encode()).decode()
    raw = signing.loads(src, key=KEY, salt=SALT)
    # print(raw)
    # print(type(raw))
    return raw

def create_token(user_id):
    """生成token信息"""
    # 1. 加密头信息
    header = encrypt(HEADER)
    # 2. 构造Payload
    payload = {'user_id':user_id, "iat": time.time() + TIME_OUT}
    payload = encrypt(payload)
    # 3. 生成签名
    md5 = hashlib.md5()
    md5.update(("%s.%s" % (header, payload)).encode())
    signature = md5.hexdigest()
    token = "%s.%s.%s" % (header, payload, signature)
    # 存储到缓存中
    #cache.set(username, token, TIME_OUT)
    User.objects.filter(user_id = user_id).update(token = token)
    return token

def get_payload(token):
    payload = str(token).split('.')[1]
    payload = decrypt(payload)
    return payload

# 通过token获取用户名
def get_id(token):
    payload = get_payload(token)
    return payload['user_id']
    pass

def check_token(token):
    payload = get_payload(token)
    #last_token = cache.get(username)
    try:
        last_token = User.objects.get(user_id = payload['user_id']).token
        # print("last_token is %s\n token is %s" %(last_token, token))
        if time.time() < payload['iat'] and last_token == token:
            return payload['user_id']
    except User.DoesNotExist:
        return None


