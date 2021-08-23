# signer-daemon collection
Signing daemon collection with redis backend.

These daemons do not provide any privacy as is, they simply provide signing and redis-based verification and storage.
Redis will need to be installed separately. The scripts can be safely edited to change the redis location as needed, and TLS "rediss" is supported as is.
The TCP socket servers provided are raw TCP, no security on that socket, that part is up to you.
Also by default, the secret keys for signing are plaintext files on the filesystem. Protect the disk, and/or be smart about
who can access any files used.

The files in the files/ directory are used for identity of the celery daemon itself, not for redis, and not for the tcp socket server.
The rsa.pem and secp384r1.pem respectively are to be created in the working directory of the daemon/server. Those are used for signing.
I recommend keeping that as a different key than the identity key used in files/. 

You will need to generate the required cryptographic components, see the celery daemon scripts.

For the RSA daemons, PSS is implemented to mitigate oracle/padding attacks on RSA (Bleichenbacher).

If the data is to be secret/private, then is should be encrypted with (AES256) before being signed by this identity daemon.

Static analysis note:
There is a false positive for Crypto being seen as the old pycrypto, when in this case it is using the pycryptdome.
This is caused by the old Crypto api syntax, but it is actually with pycryptdome, which continued what pycrypto started.
https://pycryptodome.readthedocs.io/en/latest/src/vs_pycrypto.html

Important design note:
Both ECDSA and RSA verify daemons will not return a valid result if the signature is not stored appropriately it the redis instance.
This allows for expiration and granular controls over which keys are valid via redis. 

So if you delete or expire the signature in redis, you expire that signature in runtime. If the signature data is loaded back into redis,
then it will become valid again.

The max message length is defaulted to 2048 bytes. Adjust it if needed, in many implementations it may be safely increased.
Otherwise, larger messages will be chunked and treated as independent messages to sign.

What is included in this repo is a collection of concepts that would be 
further expanded on or combined with other applications when used in the real world.
I use these daemons on the loopback device and have other apps call them locally.
I want to use it behind a TLS proxy and firewall etc.


Example of setting up a single host for both sign and verify servers:

```
# We'll put the celery daemon's rsa files in files/
Gmkdir files/
# Crate an RSA key, get it signed, put the certificate in
# files/celeryRsa.pem
# and the rsa private key in
# files/celeryRsa.key
# and the ca certs can be concatenated into
# files/caTrust.pem
# 
# create an rsa signing key or use an existing one
openssl genrsa 4096 > rsa.pem
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
nohup python3 signing_server.py > signer.log &
nohup python3 verify_server.py > verify.log &
```

Example client CLI usage:

```
(venv) 🟢 time bash request_client.sh sign localhost yeahthissomecooltokenthingwhatever
(b'yeahthissomecooltokenthingwhateve', b'abe9e883a9654e2265df3b7180d8c06b03b6aedd605665cf9a2c240a3f8b0fe9de617bc986e1078451678d49e7d983ff06259463a56e642c2497ff25d818e0d88bb0e571de15606437b54647071734094a715c7f0cc8b74d66fc0ef8c6057d2e42e159d78dccf9a240e0a3dea6a7ccd8968d9d6dffdf40e091cbf8b59c91b8b5408d9921b907a88d9a932d6fcd0d72fd18248ca9e064bfc9c34bf09117467d588edac987fb44f1fa6395f25376acea4e7cfad4333dea6b6c5fc787920b8e90da6f9fde3616dc29c8100b75396e91d819f6f30e2d70265d4724de856f69f184ef80f0742b057adbb4be75d341bac92bd86cf9ccc13fd5d71d74a466265c4aa89b072985aadc465b7ac4167fc54b52abcbbdde3807349b5bffea3d69df259d749d8afdc6fd174d79703921001bd98d75b119af8849817ff955f75a5e1f8cafb84192b07de133f808425f6469df7ddad4d1960698f61c054435289bd10ed1b8acb1a1354c1d33282143f7a14831bd825092e4b6c1c8947951e88169536496a8fdcd848f184ba9fd8c0048c08ac77f2cbe15facfae7926548597794fa8005e4d32c4e4a427058a863beb0c3ce65c75dd4bf934b8922c0d47add3e4c3b6076366753ecde762418d6d8e3daafc39f2b0d35c33f1ef935a619d4b41e2cee33ad4cd046bafcb05071a6c3206a9282c0d1e1f6d799bea9e1b4ee38ba396894160fd0fe760')
real    0m0.297s
user    0m0.039s
sys     0m0.007s

```

An example of making a verification request:

```
(venv) 🟢 time bash request_client.sh verify localhost abe9e883a9654e2265df3b7180d8c06b03b6aedd605665cf9a2c240a3f8b0fe9de617bc986e1078451678d49e7d983ff06259463a56e642c2497ff25d818e0d88bb0e571de15606437b54647071734094a715c7f0cc8b74d66fc0ef8c6057d2e42e159d78dccf9a240e0a3dea6a7ccd8968d9d6dffdf40e091cbf8b59c91b8b5408d9921b907a88d9a932d6fcd0d72fd18248ca9e064bfc9c34bf09117467d588edac987fb44f1fa6395f25376acea4e7cfad4333dea6b6c5fc787920b8e90da6f9fde3616dc29c8100b75396e91d819f6f30e2d70265d4724de856f69f184ef80f0742b057adbb4be75d341bac92bd86cf9ccc13fd5d71d74a466265c4aa89b072985aadc465b7ac4167fc54b52abcbbdde3807349b5bffea3d69df259d749d8afdc6fd174d79703921001bd98d75b119af8849817ff955f75a5e1f8cafb84192b07de133f808425f6469df7ddad4d1960698f61c054435289bd10ed1b8acb1a1354c1d33282143f7a14831bd825092e4b6c1c8947951e88169536496a8fdcd848f184ba9fd8c0048c08ac77f2cbe15facfae7926548597794fa8005e4d32c4e4a427058a863beb0c3ce65c75dd4bf934b8922c0d47add3e4c3b6076366753ecde762418d6d8e3daafc39f2b0d35c33f1ef935a619d4b41e2cee33ad4cd046bafcb05071a6c3206a9282c0d1e1f6d799bea9e1b4ee38ba396894160fd0fe760
('Validated as:', True)
real    0m0.270s
user    0m0.022s
sys     0m0.009s
```


Here is an example of using CLI directly with netcat. In this example, we'll use the ECDSA daemons:

```
$ time echo mytoken | nc localhost 9848
(b'mytoken', b'ad0a729c7270620be3ef379ed48da9ed7ed56762af6e24e0983a0a5882ab0d5e6bd25dbe900b1fcfc5be19c467eeedc76e434595c852cd642c3fbd8b20ee2a11deb2378ed40714d35b16fcb1322aa2f0f435192f2831a250ee4674ea739d6065')
real    0m0.029s
user    0m0.016s
sys     0m0.005s
$ time echo ad0a729c7270620be3ef379ed48da9ed7ed56762af6e24e0983a0a5882ab0d5e6bd25dbe900b1fcfc5be19c467eeedc76e434595c852cd642c3fbd8b20ee2a11deb2378ed40714d35b16fcb1322aa2f0f435192f2831a250ee4674ea739d6065 | nc localhost 9849
Valid entry found.
real    0m0.034s
user    0m0.021s
sys     0m0.006s
$ time echo ad0a729c7270620be3ef379ed48da9ed7ed56762af6e24e0983a0a5882ab0d5e6bd25dbe900b1fcfc5be19c467eeedc76e434595c852cd642c3fbd8b20ee2a11deb2378ed40714d35b16fcb1322aa2f0f435192f2831a250ee4674ea739d6064 | nc localhost 9849
No match for signature.
real    0m0.034s
user    0m0.022s
sys     0m0.003s
$
```

You can hold a surprising amount of data in RAM, and redis keeps up with the ops very well.

Using the ecdsa socket daemons locally, the default 4 celery workers on the signing daemon are doing 37 TPS easily, and could likely handle several times that rate of requests.

Note the important difference here between the DSS and PSS verification outputs (don't change these unless you know what you are doing):

ECDSA DSS
```
      validate = signer.verify(hash, signature)
      return('Valid entry found.')
```

RSA PSS
```
      validate = signer.verify(hash, signature)
      return('Validated as:', validate)
```

You will see the PSS (RSA) verify will return True for a valid signature, and False for a signature that is not signed by the private key. If the input is not a key, then it won't return there. And the correct signature+data entry must be in redis to allow True, as well.

With the DSS (ECDSA) verify, we see a False return on valid sign, and an error return for any not sign correctly, and empty response if not a valid key.

I like the DSS behavior better, other than how the bool is flipped to a False for some reason.

