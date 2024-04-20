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
        self.decode_serializer(None, "NoTokenSpecified")

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

    def test_decode_with_invalid_signature(self):
        self.decode_serializer("tampered_token", "BadSignature")

    def test_decode_with_malformed_token(self):
        self.decode_serializer("malformedtoken", "BadSignature")

    def decode_serializer(self, token, expected_data):
        serializer = SignatureSerializer("MY_SECRET_KEY", expired_in=1)
        token = token
        data, err = serializer.decode(token)
        self.assertIsNone(data)
        self.assertEqual(err, expected_data)


def test_token_expiration():
    serializer = SignatureSerializer("MY_SECRET_KEY", expired_in=1)
    dict_obj = {"session_id": 999}
    token = serializer.encode(dict_obj)

    time.sleep(2)
    data, err = serializer.decode(token)
    assert (
        data is None and err == "SignatureExpired"
    ), "Token did not expire as expected."


def test_token_no_expiration():
    serializer = SignatureSerializer("MY_SECRET_KEY", expired_in=0)
    dict_obj = {"session_id": 999}
    token = serializer.encode(dict_obj)

    time.sleep(2)
    data, err = serializer.decode(token)
    assert (
        data is not None and err is None and data["session_id"] == 999
    ), "Failed to decode or session_id does not match."


def test_decode_with_expired_token():
    serializer = SignatureSerializer("MY_SECRET_KEY", expired_in=1)
    dict_obj = {"session_id": 1}
    token = serializer.encode(dict_obj)
    time.sleep(2)
    data, err = serializer.decode(token)
    assert data is None and err == "SignatureExpired"


def test_decode_with_invalid_signature():
    serializer = SignatureSerializer("MY_SECRET_KEY", expired_in=1)
    dict_obj = {"session_id": 1}
    token = serializer.encode(dict_obj)
    tampered_token = f"{token[:-1]}a"
    data, err = serializer.decode(tampered_token)
    assert data is None and err == "InvalidSignature"


def test_decode_with_malformed_token():
    serializer = SignatureSerializer("MY_SECRET_KEY", expired_in=1)
    data, err = serializer.decode("malformedtoken")
    assert data is None and err == "BadSignature"


CASUAL_UT = False


if CASUAL_UT:

    def test_casual_ut():
        secret_key = "MY_SECRET_KEY"
        expired_in = 1
        session_id = 1
        dict_obj = {"session_id": session_id}

        # Instantiate SignatureSerializer
        serializer = SignatureSerializer(secret_key, expired_in=expired_in)

        # Encode the dictionary object into a token
        token = serializer.encode(dict_obj)

        # Decode the token
        data, err = serializer.decode(token)

        # Assert the results
        assert (
            data is not None and err is None and data["session_id"] == session_id
        ), "Failed to decode or session_id does not match."

    def test_decode_with_no_token():
        serializer = SignatureSerializer("MY_SECRET_KEY", expired_in=1)
        data, err = serializer.decode(None)
        assert data is None and err == "NoTokenSpecified"
