import base64

import Crypto.Signature.PKCS1_v1_5 as sign_PKCS1_v1_5  # 用于签名/验签
from Crypto import Hash
from Crypto.PublicKey import RSA


class RSASignatureTool(object):

    @staticmethod
    def sort_argv(data: dict, ignore=None):
        """
        对参数进行排序，字典序，默认升序。
        @param data:字典数据
        @param ignore:排除字段
        @return:
        """
        string = ""
        if ignore is None:
            ignore = []

        keys = sorted(data)
        for key in keys:
            if key in ignore:
                continue
            string += str(data[key])
        return string

    @staticmethod
    def get_public_key_from_private_key(private_key):
        s_key = RSA.importKey(private_key)
        new_g_key = s_key.publickey().export_key()
        return new_g_key

    @staticmethod
    def to_sign_with_private_key(rsa_private_key, plain_text) -> bytes:
        """
        使用私钥生成签名，默认使用 SHA256 签名算法
        @param rsa_private_key: 私钥
        @param plain_text: 签名文本
        @return:返回的是字节流，如果要转换成字符串传输，需要进行 base64 编码
        """
        # 私钥签名
        signer_pri_obj = sign_PKCS1_v1_5.new(RSA.importKey(rsa_private_key))
        rand_hash = Hash.SHA256.new()
        rand_hash.update(plain_text.encode())
        signature = signer_pri_obj.sign(rand_hash)
        return signature

    @staticmethod
    def to_verify_with_public_key(rsa_public_key, signature: bytes, plain_text: str) -> bool:
        """
        使用公钥进行验签
        @param rsa_public_key:
        @param signature:
        @param plain_text:
        @return: 返回 true 验签成功，返回 false 验签失败
        """
        verifier = sign_PKCS1_v1_5.new(RSA.importKey(rsa_public_key))
        _rand_hash = Hash.SHA256.new()
        _rand_hash.update(plain_text.encode())
        return verifier.verify(_rand_hash, signature)

    @staticmethod
    def to_base64(data):
        """
        把字节流转换成 base64 字符串
        @param data:
        @return:
        """
        if isinstance(data, str):
            data = data.encode()
        elif isinstance(data, bytes):
            pass
        else:
            raise RuntimeError("传入参数必须是字节流或者字符串")
        return base64.b64encode(data)

    @staticmethod
    def base64_to_bytes(data) -> bytes:
        """
        base64 字符串转成字节流
        @param data: base64 编码的字符串
        @return: bytes , 可用 x.decode() 对字节流解码成字符串
        """
        return base64.b64decode(data)
