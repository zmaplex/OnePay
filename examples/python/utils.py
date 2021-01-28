import base64

import requests

try:
    import Crypto.Signature.PKCS1_v1_5 as sign_PKCS1_v1_5  # 用于签名/验签
    from Crypto import Hash
    from Crypto.PublicKey import RSA
except Exception as e:
    print("请执行命令 'pip install pycryptodome'")
    raise e


class RSASignatureTool(object):

    @staticmethod
    def sort_argv(data: dict, ignore: list = None):
        """
        对参数进行排序，字典序，默认升序。
        @param data:字典数据
        @param ignore:排除字段的列表
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


class JCPay:
    """
    演示创建订单，查询订单，验证数据
    """

    def __init__(self, domain, app_id, private_key, platform_public_key):
        """
        初始化必要参数
        @param domain: http(s)://example.com
        @param app_id: 20201029200917
        @param private_key: -----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----
        @param platform_public_key: -----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----
        """
        self.domain = domain
        self.app_id = app_id
        self.private_key = private_key
        self.platform_public_key = platform_public_key
        self.gateway = None
        print(self.list_gateways())

    def list_gateways(self):
        return requests.get(self.domain + "/api/PayGateway/BaseGateway/").json()

    def set_gateway(self, name):
        self.gateway = name

    def create(self, name, price=0.01):
        data = {'app_id': self.app_id, 'name': name,
                'price': price, 'gateway': self.gateway,
                'device_type': 0}
        sign = self.get_sign(data)
        data['sign'] = sign

        res = requests.post(self.domain + '/api/PayGateway/BaseGateway/create_order/', data=data)
        print(res.json())

    def query(self, sid='20210128205836947850'):
        data = {'app_id': self.app_id, 'sid': sid}
        sign = self.get_sign(data)
        data['sign'] = sign

        res = requests.get(self.domain + '/api/PayGateway/BaseBilling/query_order/', params=data)
        print(res.json())

    def query_gateway_platform(self, sid='20210128205836947850'):
        data = {'app_id': self.app_id, 'sid': sid}
        sign = self.get_sign(data)
        data['sign'] = sign

        res = requests.get(self.domain + '/api/PayGateway/BaseGateway/query_order/', params=data)
        print(res.json())

    def get_sign(self, data):
        data = RSASignatureTool.sort_argv(data)
        sign = RSASignatureTool.to_sign_with_private_key(self.private_key, data)
        return RSASignatureTool.to_base64(sign)
