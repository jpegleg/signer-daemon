import rsa
import base64
from base64 import b64encode, b64decode
from celery import Celery
from Crypto.PublicKey import RSA
from hashlib import sha512

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
def rsatn(message_in):
    f = open('rsa.pem','r')
    keyPair = RSA.import_key(f.read())
    print(f"Public key:  (n={hex(keyPair.n)}, e={hex(keyPair.e)})")
    hash = int.from_bytes(sha512(message_in).digest(), byteorder='big')
    signature = pow(hash, keyPair.d, keyPair.n)
    print("Signature:", hex(signature))
    return (message_in, signature)
def rsavf(message_in):
    f = open('rsa.pem','r')
    keyPair = RSA.import_key(f.read())
    print(f"Public key:  (n={hex(keyPair.n)}, e={hex(keyPair.e)})")
    hash = int.from_bytes(sha512(message_in).digest(), byteorder='big')
    fromsignature = pow(hash, keyPair.e, keyPair.n)
    print("Signature valid:", hash == fromsignature)
    return (hash == fromsignature)

if __name__ == '__main__':
    app.start()
