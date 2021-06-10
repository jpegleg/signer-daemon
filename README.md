# signer-daemon
Signing daemon collection with redis backend.

OAEP PSS implemented to mitigate oracle/padding attacks on RSA.

If the data is to be secret/private, then is should be encrypted with (AES256) before being signed by this identity daemon.

Important note about the behavior of the rsa daemons and the ecdsa daemons currently:
The RSA verify server will always return a "valid" response if the signature was created by the private RSA key, regardless of whether it is in redis or not.
THe ECDSA verify server will always return a "valid" response if the signature is inside the redis instance and the verify with the public key returns no errors.

The max message length is defaulted to 2048 bytes. Adjust it if needed, in many implementations it may be safely increased.

What is included in this repo is a collection of concepts that would be 
further expanded on or combined with other applications when used in the real world.
I use these daemons on the loopback device and have other apps call them locally.
I want to use it behind a TLS proxy and firewall etc.


Example of setting up a single host for both sign and verify servers:

```
# We'll put the celery daemon's rsa files in files/
mkdir files/
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

TODO: make a desktop GUI client, exapand error handling, include example docker files, add curves 384 and 512 daemons, front-end client for HTTPS transport.
