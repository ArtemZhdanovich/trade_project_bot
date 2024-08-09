from OpenSSL import crypto
import os


class CreateSSLSertificate:
    def __init__(self, dns_name='webportal.loc'):
        self.dns_name = dns_name


    def generate_key(self):
        key = crypto.PKey()
        key.generate_key(crypto.TYPE_RSA, 4096)
        return key


    def create_csr(self, key):
        req = crypto.X509Req()
        req.get_subject().CN = self.dns_name
        req.set_pubkey(key)
        req.sign(key, 'sha256')
        return req


    def create_self_signed_certificate(self, req, key):
        cert = crypto.X509()
        cert.set_serial_number(1)
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(365 * 24 * 60 * 60)
        cert.set_issuer(req.get_subject())
        cert.set_subject(req.get_subject())
        cert.set_pubkey(key)
        cert.sign(key, 'sha256')
        return cert


    def save_to_files(self, key, cert):
        with open(f'ssl_key_{self.dns_name}.key', 'wb') as key_file:
            key_file.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))
        with open(f'ssl_cert_{self.dns_name}.crt', 'wb') as cert_file:
            cert_file.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))


    def __create_self_signed_ssl_certificate(self):
        key = self.generate_key()
        req = self.create_csr(key)
        cert = self.create_self_signed_certificate(req, key)
        self.save_to_files(key, cert)
        print("Самоподписанный сертификат создан!")


    def create_ssl_certificate(self):
        key_path = f'ssl_key_{self.dns_name}.key'
        cert_path = f'ssl_cert_{self.dns_name}.crt'
        if os.path.exists(key_path) and os.path.exists(cert_path):
            print(f"Сертификат для {self.dns_name} уже существует.")
        else:
            self.__create_self_signed_ssl_certificate()


if __name__ == "__main__":
    ssl_creator = CreateSSLSertificate(dns_name="mywebportal.loc")
    ssl_creator.create_ssl_certificate()
