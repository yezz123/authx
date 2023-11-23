import time
import unittest

from authx._internal import SignatureSerializer


class SignatureSerializerTest(unittest.TestCase):
    def test_encode_decode(self):
        serializer = SignatureSerializer("MY_SECRET_KEY", expired_in=1)
        session_id = 1
        dict_obj = {"session_id": session_id}
        token = serializer.encode(dict_obj)
        data, err = serializer.decode(token)
        self.assertIsNotNone(data)
        self.assertIsNone(err)
        self.assertEqual(data["session_id"], session_id)

    def test_decode_with_no_token(self):
        serializer = SignatureSerializer("MY_SECRET_KEY", expired_in=1)
        token = None
        data, err = serializer.decode(token)
        self.assertIsNone(data)
        self.assertEqual(err, "NoTokenSpecified")

    def test_decode_with_expired_token(self):
        serializer = SignatureSerializer("MY_SECRET_KEY", expired_in=1)
        session_id = 1
        dict_obj = {"session_id": session_id}
        token = serializer.encode(dict_obj)
        # Sleep for more than 1 second to simulate an expired token
        time.sleep(2)
        data, err = serializer.decode(token)
        self.assertIsNone(data)
        self.assertEqual(err, "SignatureExpired")


def test_token_expiration():
    serializer = SignatureSerializer("MY_SECRET_KEY", expired_in=1)
    dict_obj = {"session_id": 999}
    token = serializer.encode(dict_obj)

    time.sleep(2)
    data, err = serializer.decode(token)
    assert data is None and err == "SignatureExpired", "Token did not expire as expected."


def test_token_no_expiration():
    serializer = SignatureSerializer("MY_SECRET_KEY", expired_in=0)
    dict_obj = {"session_id": 999}
    token = serializer.encode(dict_obj)

    time.sleep(2)
    data, err = serializer.decode(token)
    assert (
        data is not None and err is None and data["session_id"] == 999
    ), "Failed to decode or session_id does not match."


def test_token_tampering():
    serializer = SignatureSerializer("MY_SECRET_KEY", expired_in=3600)
    dict_obj = {"session_id": 999}
    token = serializer.encode(dict_obj)

    tampered_token = f"{token[:-1]}a"
    data, err = serializer.decode(tampered_token)
    assert data is None and err == "InvalidSignature", "Tampered token did not cause an error as expected."
