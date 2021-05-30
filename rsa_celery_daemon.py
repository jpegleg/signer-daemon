import rsa
import base64
from base64 import b64encode, b64decode
from celery import Celery

app = Celery(
    'celeryRsa',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)
app.conf.update(
    security_key='files/celeryRsa.key',
    security_certificate='files/celeryRsa.pem',
    security_cert_store='files/*.pem',
    task_serializer='auth',
    event_serializer='auth',
    accept_content=['auth'],
    result_accept_content=['json']
)
app.setup_security()


@app.task
def rsatn(self, token_crypto):
    tag = bytes("RSA",encoding="utf8")
    with open('rsa.pem','r') as f:
        privkey = rsa.PrivateKey.load_pkcs1(f.read().encode())
    token_message = token_crypto
    token_crypto = bytes(token_crypto, encoding='utf8') + tag
    signature = rsa.sign(token_message.encode(), privkey, 'SHA-256')
    print("token message encode = ", token_message.encode())
    signature = base64.encodebytes(signature)
    print (signature)
    return (token_crypto, signature)

if __name__ == '__main__':
    app.start()
