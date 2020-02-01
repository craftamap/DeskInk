""" basic functions to implement an encrypted ini config file """
import configparser
import os

import blowfish
import tempfile
from subprocess import call

EDITOR = os.environ.get('EDITOR', 'nano')

def get_config(key: bytes, path: str) -> configparser.ConfigParser:
    """Gets ecb_cts-encrypted config from path as ConfigParser

    Args:
        key (bytes): blowfish key
        path  (str): path to config file

    Returns:
        configparser.ConfigParser
    """
    cipher = blowfish.Cipher(key)

    with open(path, "rb") as configfile:
        configfile_content = configfile.read()

    config_decrypted = b"".join(cipher.decrypt_ecb_cts(configfile_content))
    configp = configparser.ConfigParser()
    configp.read_string(config_decrypted.decode('utf-8'))
    return configp


def edit_config(key: bytes, path: str):
    """Edits ecb_cts-encrypted config from path; creates file, if it doesn't
    exist and puts default config.

    Args:
        key (bytes): blowfish key
        path  (str): path to config file
    """
    cipher = blowfish.Cipher(key)
 
    if not os.path.exists(path):
        _create_config(cipher, path)

    with open(path, "rb") as configfile:
        i_data_decrypted = b''.join(cipher.decrypt_ecb_cts(configfile.read()))
        try:
            configparser.ConfigParser().read_string(i_data_decrypted.decode())
            """ Throws an exception if config is invalid"""
        except configparser.Error:
            raise Exception("Invalid Config file: Is your Key correct")
    
    with tempfile.NamedTemporaryFile(suffix="tmp") as tf:
        tf.write(i_data_decrypted)
        tf.flush()

        call([EDITOR, tf.name])

        tf.seek(0)
        newconfig = tf.read()
    
    try:
        configparser.ConfigParser().read_string(newconfig.decode())
        """ Throws an exception if config is invalid"""
    except configparser.Error:
        print("Cannot read new config... Restoring old config") 
        newconfig =  i_data_decrypted


    with open(path, "wb") as configfile:
        o_encrypt_data = b"".join(cipher.encrypt_ecb_cts(newconfig))
        configfile.write(o_encrypt_data)


def _create_config(cipher, path):
    default_config = b"""
[owm]
key=
location=

[airhorn]
tempid=
pid=

[mail_first]
host=
port=997
username=
password=
"""

    if not os.access(
            os.path.dirname(os.path.abspath(path)), os.W_OK
        ):
        raise ValueError("Can't create file here")

    with open(path, "wb+") as configfile:
        data_encrypted = b"".join(cipher.encrypt_ecb_cts(default_config))
        configfile.write(data_encrypted)
