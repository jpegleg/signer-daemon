import base64
import redis
import binascii
from base64 import b64encode, b64decode
from celery import Celery
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto import Random
from Crypto.Signature import PKCS1_PSS

app = Celery(
    'celeryRsa',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)
app.conf.update(
    security_key='files/celeryRsa.key',
    security_certificate='files/celeryRsa.pem',
    security_cert_store='files/caTrust.pem',
    task_serializer='auth',
    event_serializer='auth',
    accept_content=['auth'],
    result_accept_content=['json']
)
app.setup_security()

@app.task
def rsatn(message_in):
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    f = open('rsa.pem','r')
    keyPair = RSA.import_key(f.read())
    hash = SHA256.new(message_in)
    signer = PKCS1_PSS.new(keyPair)
    signature = signer.sign(hash)
    r.mset({binascii.hexlify(signature): message_in})
    print("Signature:", binascii.hexlify(signature))
    return(message_in, binascii.hexlify(signature))
def rsavf(message_in):
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    f = open('rsa.pem','r')
    keyPair = RSA.import_key(f.read())
    message = r.get(message_in)
    hash = SHA256.new(message)
    signer = PKCS1_PSS.new(keyPair)
    signature = binascii.unhexlify(message_in)
    print("Verification of data:",  message)
    try:
      validate = signer.verify(hash, signature)
      return('Validation result:', validate)
    except Exception as error:
      print('ERROR: ', error)
      return('No match for signature.')

if __name__ == '__main__':
    app.start()
