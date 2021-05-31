FROM debian
LABEL maintainer="carefuldata@protonmail.com"
LABEL version="0.1"
LABEL description="RSA Signing Microservice"

RUN apt-get update && apt-get install -y apt-transport-https aptitude && aptitude install -y python3 python3-venv pip openssl curl haproxy redis
RUN ln -sf /dev/stdout signer.log
RUN mkdir files/ && openssl genrsa 4096 > files/celeryRsa.key

# RUN curl https://somevault/pki/root_ca.pem -o files/ca.pem
# RUN curl https://somevault/pki/certificate/things -o files/celeryRsa.pem

COPY SIGNER /usr/local/sbin/
COPY haproxy.cfg /etc/haproxy/haproxy.cfg
COPY rsa.pem /root/rsa.pem

RUN ln -sf /root/rsa.pem /rsa.pem
RUN chmod +x /usr/local/sbin/SIGNER

EXPOSE 443

CMD SIGNER
