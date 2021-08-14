""" rsa cryptodome sign and verify with redis storage """
import binascii
import redis

from celery import Celery
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
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
    """ rsa sign and store in redis """
    re_dis = redis.StrictRedis(host='localhost', port=6379, db=0)
    f_key = open('rsa.pem', 'r')
    key_pair = RSA.import_key(f_key.read())
    hashd = SHA256.new(message_in)
    signer = PKCS1_PSS.new(key_pair)
    signature = signer.sign(hashd)
    re_dis.mset({binascii.hexlify(signature): message_in})
    print("Signature:", binascii.hexlify(signature))
    return(message_in, binascii.hexlify(signature))
def rsavf(message_in):
    """ rsa verify """
    re_dis = redis.StrictRedis(host='localhost', port=6379, db=0)
    f_key = open('rsa.pem', 'r')
    key_pair = RSA.import_key(f_key.read())
    message = re_dis.get(message_in)
    hashd = SHA256.new(message)
    signer = PKCS1_PSS.new(key_pair)
    signature = binascii.unhexlify(message_in)
    print("Verification of data:",  message)
    try:
        validate = signer.verify(hashd, signature)
        return 'Validated as:', validate
    except Exception as error:
        print('ERROR: ', error)
        return 'No match for signature.'

if __name__ == '__main__':
    app.start()
