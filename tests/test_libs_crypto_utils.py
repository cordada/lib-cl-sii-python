import unittest
from binascii import a2b_hex
from datetime import datetime

import cryptography.hazmat.primitives.hashes
import cryptography.x509
from cryptography.x509 import oid

from cl_sii.libs.crypto_utils import (  # noqa: F401
    X509Cert,
    add_pem_cert_header_footer,
    load_der_x509_cert,
    load_pem_x509_cert,
    remove_pem_cert_header_footer,
    x509_cert_der_to_pem,
    x509_cert_pem_to_der,
)
from cl_sii.rut.constants import SII_CERT_TITULAR_RUT_OID
from . import utils


# TODO: get fake certificates, keys, and all the variations from
#   https://github.com/urllib3/urllib3/tree/1.24.2/dummyserver/certs

# TODO: move me into 'cl_sii/crypto/constants.py'
# - Organismo: MINISTERIO DE ECONOMÍA / SUBSECRETARIA DE ECONOMIA
# - Decreto 181 (Julio-Agosto 2002)
#   "APRUEBA REGLAMENTO DE LA LEY 19.799 SOBRE DOCUMENTOS ELECTRONICOS, FIRMA ELECTRONICA
#   Y LA CERTIFICACION DE DICHA FIRMA"
# - ref: https://www.leychile.cl/Consulta/m/norma_plana?org=&idNorma=201668
# dice:
# > RUT de la certificadora emisora : 1.3.6.1.4.1.8321.2
_SII_CERT_CERTIFICADORA_EMISORA_RUT_OID = oid.ObjectIdentifier("1.3.6.1.4.1.8321.2")


class FunctionsTest(unittest.TestCase):
    def test_add_pem_cert_header_footer(self) -> None:
        # TODO: implement for function 'add_pem_cert_header_footer'.
        pass

    def test_remove_pem_cert_header_footer(self) -> None:
        # TODO: implement for function 'remove_pem_cert_header_footer'.
        pass


class LoadPemX509CertTest(unittest.TestCase):
    def test_load_der_x509_cert_ok(self) -> None:
        cert_der_bytes = utils.read_test_file_bytes(
            'test_data/crypto/wildcard-google-com-cert.der',
        )

        x509_cert = load_der_x509_cert(cert_der_bytes)

        self.assertIsInstance(x509_cert, X509Cert)

        #######################################################################
        # main properties
        #######################################################################

        self.assertEqual(
            x509_cert.version,
            cryptography.x509.Version.v3,
        )
        self.assertIsInstance(
            x509_cert.signature_hash_algorithm,
            cryptography.hazmat.primitives.hashes.SHA256,
        )
        self.assertEqual(
            x509_cert.signature_algorithm_oid,
            oid.SignatureAlgorithmOID.RSA_WITH_SHA256,
        )

        self.assertEqual(
            x509_cert.serial_number,
            122617997729991213273569581938043448870,
        )
        self.assertEqual(
            x509_cert.not_valid_after,
            datetime(2019, 6, 18, 13, 24),
        )
        self.assertEqual(
            x509_cert.not_valid_before,
            datetime(2019, 3, 26, 13, 40, 40),
        )

        #######################################################################
        # issuer
        #######################################################################

        self.assertEqual(len(x509_cert.issuer.rdns), 3)
        self.assertEqual(
            x509_cert.issuer.get_attributes_for_oid(oid.NameOID.COUNTRY_NAME)[0].value,
            'US',
        )
        self.assertEqual(
            x509_cert.issuer.get_attributes_for_oid(oid.NameOID.ORGANIZATION_NAME)[0].value,
            'Google Trust Services',
        )
        self.assertEqual(
            x509_cert.issuer.get_attributes_for_oid(oid.NameOID.COMMON_NAME)[0].value,
            'Google Internet Authority G3',
        )

        #######################################################################
        # subject
        #######################################################################

        self.assertEqual(len(x509_cert.subject.rdns), 5)
        self.assertEqual(
            x509_cert.subject.get_attributes_for_oid(oid.NameOID.COUNTRY_NAME)[0].value,
            'US',
        )
        self.assertEqual(
            x509_cert.subject.get_attributes_for_oid(oid.NameOID.STATE_OR_PROVINCE_NAME)[0].value,
            'California',
        )
        self.assertEqual(
            x509_cert.subject.get_attributes_for_oid(oid.NameOID.LOCALITY_NAME)[0].value,
            'Mountain View',
        )
        self.assertEqual(
            x509_cert.subject.get_attributes_for_oid(oid.NameOID.ORGANIZATION_NAME)[0].value,
            'Google LLC',
        )
        self.assertEqual(
            x509_cert.subject.get_attributes_for_oid(oid.NameOID.COMMON_NAME)[0].value,
            '*.google.com',
        )

        #######################################################################
        # extensions
        #######################################################################

        cert_extensions = x509_cert.extensions
        self.assertEqual(len(cert_extensions._extensions), 9)

        # BASIC_CONSTRAINTS
        basic_constraints_ext = cert_extensions.get_extension_for_class(
            cryptography.x509.extensions.BasicConstraints
        )
        self.assertEqual(basic_constraints_ext.critical, True)
        self.assertEqual(basic_constraints_ext.value.ca, False)
        self.assertIs(basic_constraints_ext.value.path_length, None)

        # KEY_USAGE
        key_usage_ext = cert_extensions.get_extension_for_class(
            cryptography.x509.extensions.KeyUsage
        )
        self.assertEqual(key_usage_ext.critical, True)
        self.assertEqual(key_usage_ext.value.content_commitment, False)
        self.assertEqual(key_usage_ext.value.crl_sign, False)
        self.assertEqual(key_usage_ext.value.data_encipherment, False)
        self.assertEqual(key_usage_ext.value.digital_signature, True)
        self.assertEqual(key_usage_ext.value.key_agreement, False)
        self.assertEqual(key_usage_ext.value.key_cert_sign, False)
        self.assertEqual(key_usage_ext.value.key_encipherment, False)

        # EXTENDED_KEY_USAGE
        extended_key_usage_ext = cert_extensions.get_extension_for_class(
            cryptography.x509.extensions.ExtendedKeyUsage
        )
        self.assertEqual(extended_key_usage_ext.critical, False)
        self.assertEqual(
            extended_key_usage_ext.value._usages,
            [oid.ExtendedKeyUsageOID.SERVER_AUTH],
        )

        # SUBJECT_ALTERNATIVE_NAME
        subject_alt_name_ext = cert_extensions.get_extension_for_class(
            cryptography.x509.extensions.SubjectAlternativeName
        )
        self.assertEqual(subject_alt_name_ext.critical, False)
        self.assertEqual(len(subject_alt_name_ext.value._general_names._general_names), 67)
        self.assertEqual(
            subject_alt_name_ext.value._general_names._general_names[0].value,
            '*.google.com',
        )

        # AUTHORITY_INFORMATION_ACCESS
        authority_information_access_ext = cert_extensions.get_extension_for_class(
            cryptography.x509.extensions.AuthorityInformationAccess
        )
        self.assertEqual(authority_information_access_ext.critical, False)
        self.assertEqual(len(authority_information_access_ext.value._descriptions), 2)

        # SUBJECT_KEY_IDENTIFIER
        subject_key_identifier_ext = cert_extensions.get_extension_for_class(
            cryptography.x509.extensions.SubjectKeyIdentifier
        )
        self.assertEqual(subject_key_identifier_ext.critical, False)
        self.assertEqual(
            subject_key_identifier_ext.value.digest,
            b'\xcf\x02\xda\x1aM\x80\x92\xff\x04E\xff\xcb7\x81\xe3O\x1d\x85\xb6\xb6',
        )

        # AUTHORITY_KEY_IDENTIFIER
        authority_key_identifier_ext = cert_extensions.get_extension_for_class(
            cryptography.x509.extensions.AuthorityKeyIdentifier
        )
        self.assertEqual(authority_key_identifier_ext.critical, False)
        self.assertIs(authority_key_identifier_ext.value.authority_cert_issuer, None)
        self.assertIs(authority_key_identifier_ext.value.authority_cert_serial_number, None)
        self.assertEqual(
            authority_key_identifier_ext.value.key_identifier,
            b'w\xc2\xb8P\x9agvv\xb1-\xc2\x86\xd0\x83\xa0~\xa6~\xbaK',
        )

        # CERTIFICATE_POLICIES
        certificate_policies_ext = cert_extensions.get_extension_for_class(
            cryptography.x509.extensions.CertificatePolicies
        )
        self.assertEqual(certificate_policies_ext.critical, False)
        self.assertSetEqual(
            {
                policy_info.policy_identifier.dotted_string
                for policy_info in certificate_policies_ext.value._policies
            },
            {
                # 'Google Trust Services'
                #   https://github.com/zmap/constants/blob/0816f6f/x509/certificate_policies.csv#L34
                '1.3.6.1.4.1.11129.2.5.3',
                # 'CA/B Forum Organization Validated'
                #   https://github.com/zmap/constants/blob/0816f6f/x509/certificate_policies.csv#L193
                '2.23.140.1.2.2',
            },
        )

        # CRL_DISTRIBUTION_POINTS
        crl_distribution_points_ext = cert_extensions.get_extension_for_class(
            cryptography.x509.extensions.CRLDistributionPoints
        )
        self.assertEqual(crl_distribution_points_ext.critical, False)
        self.assertEqual(len(crl_distribution_points_ext.value._distribution_points), 1)
        self.assertEqual(
            crl_distribution_points_ext.value._distribution_points[0].full_name[0].value,
            'http://crl.pki.goog/GTSGIAG3.crl',
        )
        self.assertIs(crl_distribution_points_ext.value._distribution_points[0].crl_issuer, None)
        self.assertIs(crl_distribution_points_ext.value._distribution_points[0].reasons, None)
        self.assertIs(crl_distribution_points_ext.value._distribution_points[0].relative_name, None)

    def test_load_der_x509_cert_ok_cert_real_dte_1(self) -> None:
        cert_der_bytes = utils.read_test_file_bytes(
            'test_data/sii-crypto/DTE--76354771-K--33--170-cert.der'
        )

        x509_cert = load_der_x509_cert(cert_der_bytes)

        self.assertIsInstance(x509_cert, X509Cert)

        #######################################################################
        # main properties
        #######################################################################

        self.assertEqual(
            x509_cert.version,
            cryptography.x509.Version.v3,
        )
        self.assertIsInstance(
            x509_cert.signature_hash_algorithm,
            cryptography.hazmat.primitives.hashes.SHA1,
        )
        self.assertEqual(
            x509_cert.signature_algorithm_oid,
            oid.SignatureAlgorithmOID.RSA_WITH_SHA1,
        )

        self.assertEqual(
            x509_cert.serial_number,
            232680798042554446173213,
        )
        self.assertEqual(
            x509_cert.not_valid_after,
            datetime(2020, 9, 3, 21, 11, 12),
        )
        self.assertEqual(
            x509_cert.not_valid_before,
            datetime(2017, 9, 4, 21, 11, 12),
        )

        #######################################################################
        # issuer
        #######################################################################

        self.assertEqual(len(x509_cert.issuer.rdns), 7)
        self.assertEqual(
            x509_cert.issuer.get_attributes_for_oid(oid.NameOID.COUNTRY_NAME)[0].value,
            'CL',
        )
        self.assertEqual(
            x509_cert.issuer.get_attributes_for_oid(oid.NameOID.STATE_OR_PROVINCE_NAME)[0].value,
            'Region Metropolitana',
        )
        self.assertEqual(
            x509_cert.issuer.get_attributes_for_oid(oid.NameOID.LOCALITY_NAME)[0].value,
            'Santiago',
        )
        self.assertEqual(
            x509_cert.issuer.get_attributes_for_oid(oid.NameOID.ORGANIZATION_NAME)[0].value,
            'E-CERTCHILE',
        )
        self.assertEqual(
            x509_cert.issuer.get_attributes_for_oid(oid.NameOID.ORGANIZATIONAL_UNIT_NAME)[0].value,
            'Autoridad Certificadora',
        )
        self.assertEqual(
            x509_cert.issuer.get_attributes_for_oid(oid.NameOID.COMMON_NAME)[0].value,
            'E-CERTCHILE CA FIRMA ELECTRONICA SIMPLE',
        )
        self.assertEqual(
            x509_cert.issuer.get_attributes_for_oid(oid.NameOID.EMAIL_ADDRESS)[0].value,
            'sclientes@e-certchile.cl',
        )

        #######################################################################
        # subject
        #######################################################################

        self.assertEqual(len(x509_cert.subject.rdns), 7)
        self.assertEqual(
            x509_cert.subject.get_attributes_for_oid(oid.NameOID.COUNTRY_NAME)[0].value,
            'CL',
        )
        self.assertEqual(
            x509_cert.subject.get_attributes_for_oid(oid.NameOID.STATE_OR_PROVINCE_NAME)[0].value,
            'VALPARAISO ',
        )
        self.assertEqual(
            x509_cert.subject.get_attributes_for_oid(oid.NameOID.LOCALITY_NAME)[0].value,
            'Quillota',
        )
        self.assertEqual(
            x509_cert.subject.get_attributes_for_oid(oid.NameOID.ORGANIZATION_NAME)[0].value,
            'Servicios Bonilla y Lopez y Cia. Ltda.',
        )
        self.assertEqual(
            x509_cert.subject.get_attributes_for_oid(oid.NameOID.ORGANIZATIONAL_UNIT_NAME)[0].value,
            'Ingeniería y Construcción',
        )
        self.assertEqual(
            x509_cert.subject.get_attributes_for_oid(oid.NameOID.COMMON_NAME)[0].value,
            'Ramon humberto Lopez  Jara',
        )
        self.assertEqual(
            x509_cert.subject.get_attributes_for_oid(oid.NameOID.EMAIL_ADDRESS)[0].value,
            'enaconltda@gmail.com',
        )

        #######################################################################
        # extensions
        #######################################################################

        cert_extensions = x509_cert.extensions
        self.assertEqual(len(cert_extensions._extensions), 9)

        # KEY_USAGE
        key_usage_ext = cert_extensions.get_extension_for_class(
            cryptography.x509.extensions.KeyUsage
        )
        self.assertEqual(key_usage_ext.critical, False)
        self.assertEqual(key_usage_ext.value.content_commitment, True)
        self.assertEqual(key_usage_ext.value.crl_sign, False)
        self.assertEqual(key_usage_ext.value.data_encipherment, True)
        self.assertEqual(key_usage_ext.value.digital_signature, True)
        self.assertEqual(key_usage_ext.value.key_agreement, False)
        self.assertEqual(key_usage_ext.value.key_cert_sign, False)
        self.assertEqual(key_usage_ext.value.key_encipherment, True)

        # ISSUER_ALTERNATIVE_NAME
        issuer_alt_name_ext = cert_extensions.get_extension_for_class(
            cryptography.x509.extensions.IssuerAlternativeName
        )
        self.assertEqual(issuer_alt_name_ext.critical, False)
        self.assertEqual(len(issuer_alt_name_ext.value._general_names._general_names), 1)
        self.assertEqual(
            issuer_alt_name_ext.value._general_names._general_names[0].type_id,
            _SII_CERT_CERTIFICADORA_EMISORA_RUT_OID,
        )
        self.assertEqual(
            issuer_alt_name_ext.value._general_names._general_names[0].value,
            b'\x16\n96928180-5',
        )

        # SUBJECT_ALTERNATIVE_NAME
        subject_alt_name_ext = cert_extensions.get_extension_for_class(
            cryptography.x509.extensions.SubjectAlternativeName
        )
        self.assertEqual(subject_alt_name_ext.critical, False)
        self.assertEqual(len(subject_alt_name_ext.value._general_names._general_names), 1)
        self.assertEqual(
            subject_alt_name_ext.value._general_names._general_names[0].type_id,
            SII_CERT_TITULAR_RUT_OID,
        )
        self.assertEqual(
            subject_alt_name_ext.value._general_names._general_names[0].value,
            b'\x16\n13185095-6',
        )

        # AUTHORITY_INFORMATION_ACCESS
        authority_information_access_ext = cert_extensions.get_extension_for_class(
            cryptography.x509.extensions.AuthorityInformationAccess
        )
        self.assertEqual(authority_information_access_ext.critical, False)
        self.assertEqual(len(authority_information_access_ext.value._descriptions), 1)
        self.assertEqual(
            authority_information_access_ext.value._descriptions[0].access_location.value,
            'http://ocsp.ecertchile.cl/ocsp',
        )
        self.assertEqual(
            authority_information_access_ext.value._descriptions[0].access_method,
            oid.AuthorityInformationAccessOID.OCSP,
        )

        # SUBJECT_KEY_IDENTIFIER
        subject_key_identifier_ext = cert_extensions.get_extension_for_class(
            cryptography.x509.extensions.SubjectKeyIdentifier
        )
        self.assertEqual(subject_key_identifier_ext.critical, False)
        self.assertEqual(
            subject_key_identifier_ext.value.digest,
            a2b_hex('D5:D5:47:84:5D:14:55:EE:D1:5C:8C:F8:72:39:77:FD:57:B0:FA:AA'.replace(':', '')),
        )

        # AUTHORITY_KEY_IDENTIFIER
        authority_key_identifier_ext = cert_extensions.get_extension_for_class(
            cryptography.x509.extensions.AuthorityKeyIdentifier
        )
        self.assertEqual(authority_key_identifier_ext.critical, False)
        self.assertIs(authority_key_identifier_ext.value.authority_cert_issuer, None)
        self.assertIs(authority_key_identifier_ext.value.authority_cert_serial_number, None)
        self.assertEqual(
            authority_key_identifier_ext.value.key_identifier,
            a2b_hex('78:E1:3E:9F:D2:12:B3:7A:3C:8D:CD:30:0E:53:B3:43:29:07:B3:55'.replace(':', '')),
        )

        # CERTIFICATE_POLICIES
        certificate_policies_ext = cert_extensions.get_extension_for_class(
            cryptography.x509.extensions.CertificatePolicies
        )
        self.assertEqual(certificate_policies_ext.critical, False)
        self.assertEqual(len(certificate_policies_ext.value._policies), 1)
        # note: parent of OID '1.3.6.1.4.1.8658.5' is '1.3.6.1.4.1.42346'
        #   ("Empresa Nacional de Certificacion Electronica ").
        #   http://oidref.com/1.3.6.1.4.1.8658
        #   http://oid-info.com/get/1.3.6.1.4.1.8658
        self.assertEqual(
            certificate_policies_ext.value._policies[0].policy_identifier,
            oid.ObjectIdentifier("1.3.6.1.4.1.8658.5"),
        )
        self.assertEqual(len(certificate_policies_ext.value._policies[0].policy_qualifiers), 2)
        self.assertEqual(
            certificate_policies_ext.value._policies[0].policy_qualifiers[0],
            "http://www.e-certchile.cl/CPS.htm",
        )
        self.assertEqual(
            certificate_policies_ext.value._policies[0].policy_qualifiers[1],
            cryptography.x509.extensions.UserNotice(
                notice_reference=None,
                explicit_text=(
                    "Certificado Firma Simple. Ha sido validado en forma presencial, "
                    "quedando habilitado el Certificado para uso tributario"
                ),
            ),
        )

        # CRL_DISTRIBUTION_POINTS
        crl_distribution_points_ext = cert_extensions.get_extension_for_class(
            cryptography.x509.extensions.CRLDistributionPoints
        )
        self.assertEqual(crl_distribution_points_ext.critical, False)
        self.assertEqual(len(crl_distribution_points_ext.value._distribution_points), 1)
        self.assertEqual(
            crl_distribution_points_ext.value._distribution_points[0].full_name[0].value,
            'http://crl.e-certchile.cl/ecertchilecaFES.crl',
        )
        self.assertIs(crl_distribution_points_ext.value._distribution_points[0].crl_issuer, None)
        self.assertIs(crl_distribution_points_ext.value._distribution_points[0].reasons, None)
        self.assertIs(crl_distribution_points_ext.value._distribution_points[0].relative_name, None)

        #######################################################################
        # extra extensions
        #######################################################################

        # "Microsoft" / "Microsoft CertSrv Infrastructure" / "szOID_CERTIFICATE_TEMPLATE"
        # See:
        #   http://oidref.com/1.3.6.1.4.1.311.21.7
        #   https://support.microsoft.com/en-ae/help/287547/object-ids-associated-with-microsoft-cryptography
        some_microsoft_extension_oid = oid.ObjectIdentifier("1.3.6.1.4.1.311.21.7")
        some_microsoft_ext = cert_extensions.get_extension_for_oid(some_microsoft_extension_oid)
        self.assertEqual(some_microsoft_ext.critical, False)
        self.assertTrue(isinstance(some_microsoft_ext.value.value, bytes))

    def test_load_der_x509_cert_ok_cert_real_dte_3(self) -> None:
        cert_der_bytes = utils.read_test_file_bytes(
            'test_data/sii-crypto/DTE--60910000-1--33--2336600-cert.der'
        )

        x509_cert = load_der_x509_cert(cert_der_bytes)

        self.assertIsInstance(x509_cert, X509Cert)

        #######################################################################
        # main properties
        #######################################################################

        self.assertEqual(
            x509_cert.version,
            cryptography.x509.Version.v3,
        )
        self.assertIsInstance(
            x509_cert.signature_hash_algorithm,
            cryptography.hazmat.primitives.hashes.SHA256,
        )
        self.assertEqual(
            x509_cert.signature_algorithm_oid,
            oid.SignatureAlgorithmOID.RSA_WITH_SHA256,
        )

        self.assertEqual(
            x509_cert.serial_number,
            6504844188525727926,
        )
        self.assertEqual(
            x509_cert.not_valid_after,
            datetime(2019, 9, 6, 21, 13, 0),
        )
        self.assertEqual(
            x509_cert.not_valid_before,
            datetime(2018, 9, 6, 21, 13, 0),
        )

        #######################################################################
        # issuer
        #######################################################################

        self.assertEqual(len(x509_cert.issuer.rdns), 5)
        self.assertEqual(
            x509_cert.issuer.get_attributes_for_oid(oid.NameOID.COUNTRY_NAME)[0].value,
            'CL',
        )
        self.assertEqual(
            x509_cert.issuer.get_attributes_for_oid(oid.NameOID.ORGANIZATION_NAME)[0].value,
            'E-Sign S.A.',
        )
        self.assertEqual(
            x509_cert.issuer.get_attributes_for_oid(oid.NameOID.ORGANIZATIONAL_UNIT_NAME)[0].value,
            'Terms of use at www.esign-la.com/acuerdoterceros',
        )
        self.assertEqual(
            x509_cert.issuer.get_attributes_for_oid(oid.NameOID.COMMON_NAME)[0].value,
            'E-Sign Class 2 Firma Tributaria CA',
        )
        self.assertEqual(
            x509_cert.issuer.get_attributes_for_oid(oid.NameOID.EMAIL_ADDRESS)[0].value,
            'e-sign@esign-la.com',
        )

        #######################################################################
        # subject
        #######################################################################

        self.assertEqual(len(x509_cert.subject.rdns), 5)
        self.assertEqual(
            x509_cert.subject.get_attributes_for_oid(oid.NameOID.COUNTRY_NAME)[0].value,
            'CL',
        )
        self.assertEqual(
            x509_cert.subject.get_attributes_for_oid(oid.NameOID.ORGANIZATION_NAME)[0].value,
            'E-Sign S.A.',
        )
        self.assertEqual(
            x509_cert.subject.get_attributes_for_oid(oid.NameOID.ORGANIZATIONAL_UNIT_NAME)[0].value,
            'Terms of use at www.esign-la.com/acuerdoterceros',
        )
        self.assertEqual(
            x509_cert.subject.get_attributes_for_oid(oid.NameOID.COMMON_NAME)[0].value,
            'Jorge Enrique Cabello Ortiz',
        )
        self.assertEqual(
            x509_cert.subject.get_attributes_for_oid(oid.NameOID.EMAIL_ADDRESS)[0].value,
            'jcabello@nic.cl',
        )

        #######################################################################
        # extensions
        #######################################################################

        cert_extensions = x509_cert.extensions
        self.assertEqual(len(cert_extensions._extensions), 10)

        # KEY_USAGE
        key_usage_ext = cert_extensions.get_extension_for_class(
            cryptography.x509.extensions.KeyUsage
        )
        self.assertEqual(key_usage_ext.critical, True)
        self.assertEqual(key_usage_ext.value.content_commitment, False)
        self.assertEqual(key_usage_ext.value.crl_sign, False)
        self.assertEqual(key_usage_ext.value.data_encipherment, False)
        self.assertEqual(key_usage_ext.value.digital_signature, True)
        self.assertEqual(key_usage_ext.value.key_agreement, False)
        self.assertEqual(key_usage_ext.value.key_cert_sign, False)
        self.assertEqual(key_usage_ext.value.key_encipherment, True)

        # ISSUER_ALTERNATIVE_NAME
        issuer_alt_name_ext = cert_extensions.get_extension_for_class(
            cryptography.x509.extensions.IssuerAlternativeName
        )
        self.assertEqual(issuer_alt_name_ext.critical, False)
        self.assertEqual(len(issuer_alt_name_ext.value._general_names._general_names), 1)
        self.assertEqual(
            issuer_alt_name_ext.value._general_names._general_names[0].type_id,
            _SII_CERT_CERTIFICADORA_EMISORA_RUT_OID,
        )
        self.assertEqual(
            issuer_alt_name_ext.value._general_names._general_names[0].value,
            b'\x16\n99551740-K',
        )

        # SUBJECT_ALTERNATIVE_NAME
        subject_alt_name_ext = cert_extensions.get_extension_for_class(
            cryptography.x509.extensions.SubjectAlternativeName
        )
        self.assertEqual(subject_alt_name_ext.critical, False)
        self.assertEqual(len(subject_alt_name_ext.value._general_names._general_names), 1)
        self.assertEqual(
            subject_alt_name_ext.value._general_names._general_names[0].type_id,
            SII_CERT_TITULAR_RUT_OID,
        )
        self.assertEqual(
            subject_alt_name_ext.value._general_names._general_names[0].value,
            b'\x16\t8480437-1',
        )

        # AUTHORITY_INFORMATION_ACCESS
        authority_information_access_ext = cert_extensions.get_extension_for_class(
            cryptography.x509.extensions.AuthorityInformationAccess
        )
        self.assertEqual(authority_information_access_ext.critical, False)
        self.assertEqual(len(authority_information_access_ext.value._descriptions), 2)
        self.assertEqual(
            authority_information_access_ext.value._descriptions[0].access_location.value,
            'http://pki.esign-la.com/cacerts/pkiClass2FirmaTributariaCA.crt',
        )
        self.assertEqual(
            authority_information_access_ext.value._descriptions[0].access_method,
            oid.AuthorityInformationAccessOID.CA_ISSUERS,
        )
        self.assertEqual(
            authority_information_access_ext.value._descriptions[1].access_location.value,
            'http://ocsp.esign-la.com',
        )
        self.assertEqual(
            authority_information_access_ext.value._descriptions[1].access_method,
            oid.AuthorityInformationAccessOID.OCSP,
        )

        # SUBJECT_KEY_IDENTIFIER
        subject_key_identifier_ext = cert_extensions.get_extension_for_class(
            cryptography.x509.extensions.SubjectKeyIdentifier
        )
        self.assertEqual(subject_key_identifier_ext.critical, False)
        self.assertEqual(
            subject_key_identifier_ext.value.digest,
            a2b_hex('E9:FE:44:7A:91:0A:F0:40:F2:9D:86:B4:E2:4C:F6:FA:1D:07:5B:C7'.replace(':', '')),
        )

        # AUTHORITY_KEY_IDENTIFIER
        authority_key_identifier_ext = cert_extensions.get_extension_for_class(
            cryptography.x509.extensions.AuthorityKeyIdentifier
        )
        self.assertEqual(authority_key_identifier_ext.critical, False)
        self.assertIs(authority_key_identifier_ext.value.authority_cert_issuer, None)
        self.assertIs(authority_key_identifier_ext.value.authority_cert_serial_number, None)
        self.assertEqual(
            authority_key_identifier_ext.value.key_identifier,
            a2b_hex('F9:4A:FA:C2:C7:6E:C2:E7:12:9C:57:45:35:84:1A:6D:28:E9:4A:A4'.replace(':', '')),
        )

        # CERTIFICATE_POLICIES
        certificate_policies_ext = cert_extensions.get_extension_for_class(
            cryptography.x509.extensions.CertificatePolicies
        )
        self.assertEqual(certificate_policies_ext.critical, False)
        self.assertEqual(len(certificate_policies_ext.value._policies), 1)
        # note: parent of OID '1.3.6.1.4.1.42346.1.4.1.2' is '1.3.6.1.4.1.42346' ("E-SIGN S.A.").
        #   http://oidref.com/1.3.6.1.4.1.42346
        #   http://oid-info.com/get/1.3.6.1.4.1.42346
        self.assertEqual(
            certificate_policies_ext.value._policies[0].policy_identifier,
            oid.ObjectIdentifier("1.3.6.1.4.1.42346.1.4.1.2"),
        )
        self.assertEqual(len(certificate_policies_ext.value._policies[0].policy_qualifiers), 2)
        self.assertEqual(
            certificate_policies_ext.value._policies[0].policy_qualifiers[0],
            cryptography.x509.extensions.UserNotice(
                notice_reference=None,
                explicit_text='Certificado para uso Tributario, Comercio, Pagos y Otros',
            ),
        )
        self.assertEqual(
            certificate_policies_ext.value._policies[0].policy_qualifiers[1],
            "http://www.esign-la.com/cps",
        )

        # CRL_DISTRIBUTION_POINTS
        crl_distribution_points_ext = cert_extensions.get_extension_for_class(
            cryptography.x509.extensions.CRLDistributionPoints
        )
        self.assertEqual(crl_distribution_points_ext.critical, False)
        self.assertEqual(len(crl_distribution_points_ext.value._distribution_points), 1)
        self.assertEqual(
            crl_distribution_points_ext.value._distribution_points[0].full_name[0].value,
            'http://pki.esign-la.com/crl/pkiClass2FirmaTributaria/enduser.crl',
        )
        self.assertIs(crl_distribution_points_ext.value._distribution_points[0].crl_issuer, None)
        self.assertIs(crl_distribution_points_ext.value._distribution_points[0].reasons, None)
        self.assertIs(crl_distribution_points_ext.value._distribution_points[0].relative_name, None)

    def test_load_der_x509_cert_ok_prueba_sii(self) -> None:
        cert_der_bytes = utils.read_test_file_bytes('test_data/sii-crypto/prueba-sii-cert.der')

        x509_cert = load_der_x509_cert(cert_der_bytes)

        self.assertIsInstance(x509_cert, X509Cert)

        #######################################################################
        # main properties
        #######################################################################

        self.assertEqual(
            x509_cert.version,
            cryptography.x509.Version.v3,
        )
        self.assertIsInstance(
            x509_cert.signature_hash_algorithm,
            cryptography.hazmat.primitives.hashes.MD5,
        )
        self.assertEqual(
            x509_cert.signature_algorithm_oid,
            oid.SignatureAlgorithmOID.RSA_WITH_MD5,
        )

        self.assertEqual(
            x509_cert.serial_number,
            131466,
        )
        self.assertEqual(
            x509_cert.not_valid_after,
            datetime(2003, 10, 2, 0, 0),
        )
        self.assertEqual(
            x509_cert.not_valid_before,
            datetime(2002, 10, 2, 19, 11, 59),
        )

        #######################################################################
        # issuer
        #######################################################################

        self.assertEqual(len(x509_cert.issuer.rdns), 6)
        self.assertEqual(
            x509_cert.issuer.get_attributes_for_oid(oid.NameOID.COUNTRY_NAME)[0].value,
            'CL',
        )
        self.assertEqual(
            x509_cert.issuer.get_attributes_for_oid(oid.NameOID.STATE_OR_PROVINCE_NAME)[0].value,
            'Region Metropolitana',
        )
        self.assertEqual(
            x509_cert.issuer.get_attributes_for_oid(oid.NameOID.LOCALITY_NAME)[0].value,
            'Santiago',
        )
        self.assertEqual(
            x509_cert.issuer.get_attributes_for_oid(oid.NameOID.ORGANIZATION_NAME)[0].value,
            'E-CERTCHILE',
        )
        self.assertEqual(
            x509_cert.issuer.get_attributes_for_oid(oid.NameOID.ORGANIZATIONAL_UNIT_NAME)[0].value,
            'Empresa Nacional de Certificacion Electronica',
        )
        self.assertEqual(
            x509_cert.issuer.get_attributes_for_oid(oid.NameOID.COMMON_NAME)[0].value,
            'E-Certchile CA Intermedia',
        )

        #######################################################################
        # subject
        #######################################################################

        self.assertEqual(len(x509_cert.subject.rdns), 7)
        self.assertEqual(
            x509_cert.subject.get_attributes_for_oid(oid.NameOID.COUNTRY_NAME)[0].value,
            'CL',
        )
        self.assertEqual(
            x509_cert.subject.get_attributes_for_oid(oid.NameOID.STATE_OR_PROVINCE_NAME)[0].value,
            'Region Metropolitana',
        )
        self.assertEqual(
            x509_cert.subject.get_attributes_for_oid(oid.NameOID.LOCALITY_NAME)[0].value,
            'Santiago',
        )
        self.assertEqual(
            x509_cert.subject.get_attributes_for_oid(oid.NameOID.ORGANIZATION_NAME)[0].value,
            'Servicio de Impuestos Internos',
        )
        self.assertEqual(
            x509_cert.subject.get_attributes_for_oid(oid.NameOID.ORGANIZATIONAL_UNIT_NAME)[0].value,
            'Servicio de Impuestos Internos',
        )
        self.assertEqual(
            x509_cert.subject.get_attributes_for_oid(oid.NameOID.COMMON_NAME)[0].value,
            'Wilibaldo Gonzalez Cabrera',
        )
        self.assertEqual(
            x509_cert.subject.get_attributes_for_oid(oid.NameOID.EMAIL_ADDRESS)[0].value,
            'wgonzalez@sii.cl',
        )

        #######################################################################
        # extensions
        #######################################################################

        cert_extensions = x509_cert.extensions
        self.assertEqual(len(cert_extensions._extensions), 5)

        # KEY_USAGE
        key_usage_ext = cert_extensions.get_extension_for_class(
            cryptography.x509.extensions.KeyUsage
        )
        self.assertEqual(key_usage_ext.critical, False)
        self.assertEqual(key_usage_ext.value.content_commitment, True)
        self.assertEqual(key_usage_ext.value.crl_sign, False)
        self.assertEqual(key_usage_ext.value.data_encipherment, True)
        self.assertEqual(key_usage_ext.value.digital_signature, True)
        self.assertEqual(key_usage_ext.value.key_agreement, False)
        self.assertEqual(key_usage_ext.value.key_cert_sign, False)
        self.assertEqual(key_usage_ext.value.key_encipherment, True)

        # ISSUER_ALTERNATIVE_NAME
        issuer_alt_name_ext = cert_extensions.get_extension_for_class(
            cryptography.x509.extensions.IssuerAlternativeName
        )
        self.assertEqual(issuer_alt_name_ext.critical, False)
        self.assertEqual(len(issuer_alt_name_ext.value._general_names._general_names), 1)
        self.assertEqual(
            issuer_alt_name_ext.value._general_names._general_names[0].type_id,
            _SII_CERT_CERTIFICADORA_EMISORA_RUT_OID,
        )
        self.assertEqual(
            issuer_alt_name_ext.value._general_names._general_names[0].value,
            b'\x16\n96928180-5',
        )

        # SUBJECT_ALTERNATIVE_NAME
        subject_alt_name_ext = cert_extensions.get_extension_for_class(
            cryptography.x509.extensions.SubjectAlternativeName
        )
        self.assertEqual(subject_alt_name_ext.critical, False)
        self.assertEqual(len(subject_alt_name_ext.value._general_names._general_names), 1)
        # TODO: find out where did OID '1.3.6.1.4.1.8658.1' come from.
        #   Shouldn't it have been equal to 'cl_sii.rut.constants.SII_CERT_TITULAR_RUT_OID'?
        self.assertEqual(
            subject_alt_name_ext.value._general_names._general_names[0].type_id,
            oid.ObjectIdentifier("1.3.6.1.4.1.8658.1"),
        )
        self.assertEqual(
            subject_alt_name_ext.value._general_names._general_names[0].value,
            b'\x16\n07880442-4',
        )

        # CERTIFICATE_POLICIES
        certificate_policies_ext = cert_extensions.get_extension_for_class(
            cryptography.x509.extensions.CertificatePolicies
        )
        self.assertEqual(certificate_policies_ext.critical, False)
        self.assertEqual(len(certificate_policies_ext.value._policies), 1)
        # TODO: find out where did OID '1.3.6.1.4.1.8658.0' come from.
        #   Perhaps it was '1.3.6.1.4.1.8658'?
        #   https://oidref.com/1.3.6.1.4.1.8658
        self.assertEqual(
            certificate_policies_ext.value._policies[0].policy_identifier,
            oid.ObjectIdentifier("1.3.6.1.4.1.8658.0"),
        )
        self.assertEqual(len(certificate_policies_ext.value._policies[0].policy_qualifiers), 2)
        self.assertEqual(
            certificate_policies_ext.value._policies[0].policy_qualifiers[0],
            "http://www.e-certchile.cl/politica/cps.htm",
        )
        self.assertEqual(
            certificate_policies_ext.value._policies[0].policy_qualifiers[1].explicit_text,
            "El titular ha sido validado en forma presencial, quedando habilitado el Certificado "
            "para uso tributario, pagos, comercio u otros",
        )

        # CRL_DISTRIBUTION_POINTS
        crl_distribution_points_ext = cert_extensions.get_extension_for_class(
            cryptography.x509.extensions.CRLDistributionPoints
        )
        self.assertEqual(crl_distribution_points_ext.critical, False)
        self.assertEqual(len(crl_distribution_points_ext.value._distribution_points), 1)
        self.assertEqual(
            crl_distribution_points_ext.value._distribution_points[0].full_name[0].value,
            'http://crl.e-certchile.cl/EcertchileCAI.crl',
        )
        self.assertIs(crl_distribution_points_ext.value._distribution_points[0].crl_issuer, None)
        self.assertIs(crl_distribution_points_ext.value._distribution_points[0].reasons, None)
        self.assertIs(crl_distribution_points_ext.value._distribution_points[0].relative_name, None)

    def test_load_der_x509_cert_fail_type_error(self) -> None:
        with self.assertRaises(TypeError) as cm:
            load_der_x509_cert(1)
        self.assertEqual(cm.exception.args, ("Value must be bytes.",))

    def test_load_der_x509_cert_fail_value_error(self) -> None:
        with self.assertRaises(ValueError) as cm:
            load_der_x509_cert(b'hello')
        self.assertEqual(
            cm.exception.args, ("error parsing asn1 value: ParseError { kind: ShortData }",)
        )

    def test_load_pem_x509_cert_ok(self) -> None:
        cert_der_bytes = utils.read_test_file_bytes(
            'test_data/crypto/wildcard-google-com-cert.der',
        )
        cert_pem_bytes = utils.read_test_file_bytes(
            'test_data/crypto/wildcard-google-com-cert.pem',
        )

        x509_cert_from_der = load_der_x509_cert(cert_der_bytes)
        x509_cert_from_pem = load_pem_x509_cert(cert_pem_bytes)

        self.assertIsInstance(x509_cert_from_pem, X509Cert)
        self.assertEqual(x509_cert_from_der, x509_cert_from_pem)

    def test_load_pem_x509_cert_ok_cert_real_dte_1(self) -> None:
        cert_der_bytes = utils.read_test_file_bytes(
            'test_data/sii-crypto/DTE--76354771-K--33--170-cert.der'
        )
        cert_pem_bytes = utils.read_test_file_bytes(
            'test_data/sii-crypto/DTE--76354771-K--33--170-cert.pem'
        )

        x509_cert_from_der = load_der_x509_cert(cert_der_bytes)
        x509_cert_from_pem = load_pem_x509_cert(cert_pem_bytes)

        self.assertIsInstance(x509_cert_from_pem, X509Cert)
        self.assertEqual(x509_cert_from_der, x509_cert_from_pem)

    def test_load_pem_x509_cert_ok_cert_real_dte_3(self) -> None:
        cert_der_bytes = utils.read_test_file_bytes(
            'test_data/sii-crypto/DTE--60910000-1--33--2336600-cert.der'
        )
        cert_pem_bytes = utils.read_test_file_bytes(
            'test_data/sii-crypto/DTE--60910000-1--33--2336600-cert.pem'
        )

        x509_cert_from_der = load_der_x509_cert(cert_der_bytes)
        x509_cert_from_pem = load_pem_x509_cert(cert_pem_bytes)

        self.assertIsInstance(x509_cert_from_pem, X509Cert)
        self.assertEqual(x509_cert_from_der, x509_cert_from_pem)

    def test_load_pem_x509_cert_ok_prueba_sii(self) -> None:
        cert_der_bytes = utils.read_test_file_bytes(
            'test_data/sii-crypto/prueba-sii-cert.der',
        )
        cert_pem_bytes = utils.read_test_file_bytes(
            'test_data/sii-crypto/prueba-sii-cert.pem',
        )

        x509_cert_from_der = load_der_x509_cert(cert_der_bytes)
        x509_cert_from_pem = load_pem_x509_cert(cert_pem_bytes)

        self.assertIsInstance(x509_cert_from_pem, X509Cert)
        self.assertEqual(x509_cert_from_der, x509_cert_from_pem)

    def test_load_pem_x509_cert_ok_str_ascii(self) -> None:
        cert_pem_str_ascii = utils.read_test_file_str_ascii(
            'test_data/crypto/wildcard-google-com-cert.pem'
        )

        x509_cert = load_pem_x509_cert(cert_pem_str_ascii)
        self.assertIsInstance(x509_cert, X509Cert)

    def test_load_pem_x509_cert_ok_str_utf8(self) -> None:
        cert_pem_str_utf8 = utils.read_test_file_str_utf8(
            'test_data/crypto/wildcard-google-com-cert.pem'
        )

        x509_cert = load_pem_x509_cert(cert_pem_str_utf8)
        self.assertIsInstance(x509_cert, X509Cert)

    def test_load_pem_x509_cert_fail_type_error(self) -> None:
        with self.assertRaises(TypeError) as cm:
            load_pem_x509_cert(1)
        self.assertEqual(cm.exception.args, ("Value must be str or bytes.",))

    def test_load_pem_x509_cert_fail_value_error(self) -> None:
        with self.assertRaises(ValueError) as cm:
            load_pem_x509_cert('hello')
        self.assertEqual(
            cm.exception.args,
            (
                "Unable to load PEM file. See "
                "https://cryptography.io/en/latest/faq/#why-can-t-i-import-my-pem-file "
                "for more details. InvalidData(InvalidLength)",
            ),
        )

    def test_x509_cert_der_to_pem_pem_to_der_ok_1(self) -> None:
        cert_der_bytes = utils.read_test_file_bytes(
            'test_data/crypto/wildcard-google-com-cert.der',
        )
        cert_pem_bytes = utils.read_test_file_bytes(
            'test_data/crypto/wildcard-google-com-cert.pem',
        )

        # note: we test the function with a double call because the input PEM data
        #   may have different line lengths and different line separators.
        self.assertEqual(
            x509_cert_pem_to_der(x509_cert_der_to_pem(cert_der_bytes)),
            x509_cert_pem_to_der(cert_pem_bytes),
        )

    def test_x509_cert_der_to_pem_pem_to_der_ok_cert_real_dte_1(self) -> None:
        cert_der_bytes = utils.read_test_file_bytes(
            'test_data/sii-crypto/DTE--76354771-K--33--170-cert.der'
        )
        cert_pem_bytes = utils.read_test_file_bytes(
            'test_data/sii-crypto/DTE--76354771-K--33--170-cert.pem'
        )

        # note: we test the function with a double call because the input PEM data
        #   may have different line lengths and different line separators.
        self.assertEqual(
            x509_cert_pem_to_der(x509_cert_der_to_pem(cert_der_bytes)),
            x509_cert_pem_to_der(cert_pem_bytes),
        )

    def test_x509_cert_der_to_pem_pem_to_der_ok_cert_real_dte_3(self) -> None:
        cert_der_bytes = utils.read_test_file_bytes(
            'test_data/sii-crypto/DTE--60910000-1--33--2336600-cert.der'
        )
        cert_pem_bytes = utils.read_test_file_bytes(
            'test_data/sii-crypto/DTE--60910000-1--33--2336600-cert.pem'
        )

        # note: we test the function with a double call because the input PEM data
        #   may have different line lengths and different line separators.
        self.assertEqual(
            x509_cert_pem_to_der(x509_cert_der_to_pem(cert_der_bytes)),
            x509_cert_pem_to_der(cert_pem_bytes),
        )

    def test_x509_cert_der_to_pem_pem_to_der_ok_prueba_sii(self) -> None:
        cert_der_bytes = utils.read_test_file_bytes(
            'test_data/sii-crypto/prueba-sii-cert.der',
        )
        cert_pem_bytes = utils.read_test_file_bytes(
            'test_data/sii-crypto/prueba-sii-cert.pem',
        )

        # note: we test the function with a double call because the input PEM data
        #   may have different line lengths and different line separators.
        self.assertEqual(
            x509_cert_pem_to_der(x509_cert_der_to_pem(cert_der_bytes)),
            x509_cert_pem_to_der(cert_pem_bytes),
        )

    def test_x509_cert_der_to_pem_type_error(self) -> None:
        with self.assertRaises(TypeError) as cm:
            x509_cert_der_to_pem(1)
        self.assertEqual(cm.exception.args, ("Value must be bytes.",))

    def test_x509_cert_pem_to_der_type_error(self) -> None:
        with self.assertRaises(TypeError) as cm:
            x509_cert_pem_to_der(1)
        self.assertEqual(cm.exception.args, ("Value must be bytes.",))

    def test_x509_cert_pem_to_der_valuetype_error(self) -> None:
        with self.assertRaises(ValueError) as cm:
            x509_cert_pem_to_der(b'hello')
        self.assertEqual(
            cm.exception.args,
            (
                "Input is not a valid base64 value.",
                "Invalid base64-encoded string: number of data characters (5) cannot be 1 more "
                "than a multiple of 4",
            ),
        )

    def test_add_pem_cert_header_footer(self) -> None:
        # TODO: implement for 'add_pem_cert_header_footer'
        pass

    def test_remove_pem_cert_header_footer(self) -> None:
        # TODO: implement for 'remove_pem_cert_header_footer'
        pass
