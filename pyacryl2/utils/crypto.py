"""
pyacryl2.utils.crypto
~~~~~~~~~~~~~~~~~~~~~

Cryptographic functions
"""

import os
import axolotl_curve25519
import base58


def sign_with_private_key(private_key, data):
    """
    Sign data with private key

    :param private_key: private key value in base58
    :type private_key: str
    :param data: data to sign
    :type data: bytes
    :return: signed data
    :rtype: bytes
    """
    random_bytes = os.urandom(64)
    signed_data = base58.b58encode(
        axolotl_curve25519.calculateSignature(random_bytes, base58.b58decode(private_key), data)
    ).decode()
    return signed_data


def verify_signature(public_key, signature, data):
    """
    Verify data signature

    :param public_key: public key value
    :type public_key: bytes
    :param signature: signature value
    :type public_key: bytes
    :param data: signed data
    :type public_key: bytes
    :return: valid or not
    :rtype: bool
    """
    result = axolotl_curve25519.verifySignature(public_key, data, signature)
    return result == 0
