openssl req -new -x509 -key key.pem -out cert.pem -days 365 \
  -subj "/C=AU/ST=SomeState/L=SomeCity/O=YourOrg/OU=YourUnit/CN=localhost"
