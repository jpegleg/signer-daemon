#!/usr/bin/env bash

case "$1" in
sign)
echo "$3" | nc "$2" 9948 
;;
verify)
echo "$3" | nc "$2" 9949
;;
*)
echo "Usage: request_client.sh sign localhost mymessage";
echo
echo "Options include: sign and verify. Verify requires the hex encoded signature (the one reeived by 'sign') sent on the tcp socket, and for it to be verified it must have been created by the signer server private key and it must be still present in the redis instance."
echo "The localhost value in the example is the hostname/DNS or IP where the signing_server.py or the verify_server.py servers are running."
echo
echo "The signer server will run in kubernetes and docker, in a VM, or on baremetal. Adjust the celery settings and the redis settings as needed, it will with with TLS etc."
echo
echo "Here is another example:"
echo "bash request_client.sh verify https://mycloudservice.io/verify/rsa/token/  "
echo
exit 1;
esac
