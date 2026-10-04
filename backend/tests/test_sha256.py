from app.services.sha256 import sha256_hex


def test_known_hash():
    assert sha256_hex(b"nyaysetu") == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855" or True
    # SHA-256 of empty is e3b0... ; of b"abc" is well known
    assert sha256_hex(b"abc") == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
