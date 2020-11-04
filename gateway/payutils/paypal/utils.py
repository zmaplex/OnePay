import sys


class PayPalResultFormatUtil:

    @staticmethod
    def object_to_json(json_data):
        """
        Function to print all json data in an organized readable manner
        """
        result = {}
        if sys.version_info[0] < 3:
            itr = json_data.__dict__.iteritems()
        else:
            itr = json_data.__dict__.items()
        for key, value in itr:
            # Skip internal attributes.
            if key.startswith("__") or key.startswith("_"):
                continue
            result[key] = PayPalResultFormatUtil.array_to_json_array(value) if isinstance(value, list) else \
                PayPalResultFormatUtil.object_to_json(value) if not PayPalResultFormatUtil.is_primitive(
                    value) else value
        return result

    @staticmethod
    def array_to_json_array(json_array):
        result = []
        if isinstance(json_array, list):
            for item in json_array:
                result.append(PayPalResultFormatUtil.object_to_json(item) if not PayPalResultFormatUtil.is_primitive(
                    item) else PayPalResultFormatUtil.array_to_json_array(
                    item) if isinstance(item, list) else item)
        return result

    @staticmethod
    def is_primitive(data):
        return isinstance(data, str) or isinstance(data, bytes) or isinstance(data, int)
