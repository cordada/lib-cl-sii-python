# Generating a self-signed certificate in DER format using OpenSSL

## Documentation

- <https://www.openssl.org/docs/manmaster/man1/req.html>

## Parameters

- File to send the key to (`key_file_name`)
- Output file (`certificate_file_name`)
- Number of days cert is valid for (`number_of_days`)

```sh
key_file_name='key.pem'
certificate_file_name='certificate.der'
number_of_days=365
subject_rut_oid='1.3.6.1.4.1.8321.1'
subject_rut='13185095-K'
```

## Steps

### Generate the private key and public certificate

```sh
openssl req \
    -newkey rsa:2048 \
    -nodes \
    -keyout "$key_file_name" \
    -x509 \
    -days "$number_of_days" \
    -outform DER \
    -out "$certificate_file_name" \
    -extensions san -config <(cat /etc/ssl/openssl.cnf \
        <(printf "\n[san]\nsubjectAltName=otherName:$subject_rut_oid;UTF8:$subject_rut"))
```

```text
Generating a RSA private key
....................................................................................+++++
....................................................+++++
writing new private key to 'key.pem'
-----
You are about to be asked to enter information that will be incorporated
into your certificate request.
What you are about to enter is what is called a Distinguished Name or a DN.
There are quite a few fields but you can leave some blank
For some fields there will be a default value,
If you enter '.', the field will be left blank.
-----
Country Name (2 letter code) [AU]:CL
State or Province Name (full name) [Some-State]:Region Metropolitana
Locality Name (eg, city) []:Santiago
Organization Name (eg, company) [Internet Widgits Pty Ltd]:Acme Corporation
Organizational Unit Name (eg, section) []:Acme Explosive Tennis Balls
Common Name (e.g. server FQDN or YOUR name) []:John Doe
Email Address []:john.doe@acme.com
```

### Output

#### Review the created certificate

```sh
openssl x509 \
    -inform DER \
    -in "$certificate_file_name" \
    -text -noout
```

This will generate a self-signed certificate in DER format and allow you to review its contents
