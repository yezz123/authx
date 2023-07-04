import time

from authx._internal import SignatureSerializer


def test_token_expiration():
    serializer = SignatureSerializer('MY_SECRET_KEY', expired_in=1)
    dict_obj = {'session_id': 999}
    token = serializer.encode(dict_obj)

    time.sleep(2)
    data, err = serializer.decode(token)
    assert data is None and err == "SignatureExpired", "Token did not expire as expected."


def test_token_no_expiration():
    serializer = SignatureSerializer('MY_SECRET_KEY', expired_in=0)
    dict_obj = {'session_id': 999}
    token = serializer.encode(dict_obj)

    time.sleep(2)
    data, err = serializer.decode(token)
    assert (
        data is not None and err is None and data['session_id'] == 999
    ), "Failed to decode or session_id does not match."


def test_token_tampering():
    serializer = SignatureSerializer('MY_SECRET_KEY', expired_in=3600)
    dict_obj = {'session_id': 999}
    token = serializer.encode(dict_obj)

    tampered_token = f'{token[:-1]}a'
    data, err = serializer.decode(tampered_token)
    assert data is None and err == "InvalidSignature", "Tampered token did not cause an error as expected."
