""" ecdsa dsa dss cryptodome sign and verify with redis storage """
import binascii
import redis

from celery import Celery
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Hash import SHA384

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
    """ dsa signature create and insert into redis """
    re_dis = redis.StrictRedis(host='localhost', port=6379, db=0)
    f_key = open('secp384r1.pem', 'r')
    key_pair = ECC.import_key(f_key.read())
    hash = SHA384.new(message_in)
    signer = DSS.new(key_pair, 'fips-186-3')
    signature = signer.sign(hash)
    re_dis.mset({binascii.hexlify(signature): message_in})
    print("Signature:", binascii.hexlify(signature))
    return(message_in, binascii.hexlify(signature))
def dsavf(message_in):
    """ dsa signature verify """
    re_dis = redis.StrictRedis(host='localhost', port=6379, db=0)
    f_key = open('secp384r1.pub', 'r')
    key_pair = ECC.import_key(f_key.read())
    message = re_dis.get(message_in)
    hashd = SHA384.new(message)
    signer = DSS.new(key_pair, 'fips-186-3')
    signature = binascii.unhexlify(message_in)
    print("Verification of data:", message)
    try:
        validate = signer.verify(hashd, signature)
        return 'Valid entry found.'
    except Exception as error:
        print('ERROR: ', error)
        return 'No match for signature.'

if __name__ == '__main__':
    app.start()
