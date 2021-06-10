import base64
import redis
import binascii
from typing import Tuple, TypeVar
from base64 import b64encode, b64decode
from celery import Celery
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Hash import SHA384

MsgTypes = TypeVar('MsgTypes', str, bytes, bytearray)
SigType = Tuple[int, int]

app = Celery(
    'celeryDsa',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)
app.conf.update(
    security_key='files/celeryDsa.key',
    security_certificate='files/celeryDsa.pem',
    security_cert_store='files/ECCcaTrust.pem',
    task_serializer='auth',
    event_serializer='auth',
    accept_content=['auth'],
    result_accept_content=['json']
)
app.setup_security()

@app.task
def dsatn(message_in):
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    f = open('secp384r1.pem','r')
    private_key = ECC.import_key(f.read())
    keyPair = private_key
    hash = SHA384.new(message_in)
    signer = DSS.new(keyPair, 'fips-186-3')
    signature = signer.sign(hash)
    r.mset({binascii.hexlify(signature): message_in})
    print("Signature:", binascii.hexlify(signature))
    try:
      return(message_in, binascii.hexlify(signature))
    except Exception as error:
      print('ERROR: ', error)
      return('No match for signature.')
def dsavf(message_in):
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    f = open('secp384r1.pub','r')
    keyPair = ECC.import_key(f.read())
    message = r.get(message_in)
    hash = SHA384.new(message)
    signer = DSS.new(keyPair, 'fips-186-3')
    signature = binascii.unhexlify(message_in)
    print("Verification of data:", message)
    try:
      validate = signer.verify(hash, signature)
      return('Valid Signature.')
    except Exception as error:
      print('ERROR: ', error)
      return('No match for signature.')

if __name__ == '__main__':
    app.start()
