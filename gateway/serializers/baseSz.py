from rest_framework import serializers, status

from gateway.models import PayApplication
from gateway.utils import RSASignatureTool


class BaseSz(serializers.Serializer):
    sign = serializers.CharField(max_length=1024, label="签名", help_text="base64 签名内容，签名算法为：SHA256WithRSA")

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    @staticmethod
    def verify_signature(app_id, data: dict, ignore: list = None):
        """
        使用商户保存在应用中的公钥进行验签
        @param app_id: 应用 app_id
        @param data: 参数数据
        @param ignore: 忽略参数名的集合列表
        @return:
        """

        if ignore is None:
            ignore = ['sign']
        elif 'sign' not in ignore:
            ignore.append('sign')
        objs = PayApplication.objects.filter(app_id=app_id)
        if not objs.exists():
            raise serializers.ValidationError({"app_id": ["应用不存在"]}, code=status.HTTP_404_NOT_FOUND)
        # 验证 app 状态
        app: PayApplication = objs.first()
        if not app.is_valid():
            raise serializers.ValidationError({"app_id": ["您的应用尚未就绪"]}, code=status.HTTP_403_FORBIDDEN)

        # 对参数进行验签
        plain_text = RSASignatureTool.sort_argv(data, ignore)
        print(f"已排序的签名参数：{plain_text}")
        _bool = False
        try:
            _bool = app.to_verify_with_public_key(data.get('sign'), plain_text)
        except Exception as e:
            raise serializers.ValidationError({"sign": ["验签出错"], 'msg': plain_text},
                                              code=status.HTTP_422_UNPROCESSABLE_ENTITY)
        if not _bool:
            raise serializers.ValidationError({"sign": ["签名未通过"], 'msg': plain_text},
                                              code=status.HTTP_403_FORBIDDEN)
