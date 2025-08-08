from ursa_bbs_signatures import BlsKeyPair, sign, SignRequest, verify, VerifyRequest, BbsKey

"""!!"""
def issue_credentials(attrs: dict):

    keypair = BlsKeyPair.generate_g2()

    messages = [str(v).encode() for v in attrs.values()]

    # Produces a 'Request' to sign a message which is passed to the sign function
    request = SignRequest(messages=messages, key_pair=keypair)
    signature = sign(request)

    return signature, keypair

"""!!"""
def verify_attributes(attrs: dict, signature, keypair):

    messages = [str(v).encode() for v in attrs.values()]

    #Produces a 'Request' to verify a message which is passed to the sign function
    request = VerifyRequest(messages=messages, signature=signature, key_pair=keypair)

    return verify(request)
