import re
from content.src.base import RegExpressionsBase


class RegExpressions(RegExpressionsBase):
    """Класс для работы с регулярными выражениями проекта"""

    @staticmethod
    def get_video_id(url):
        """Метод получает id_video из ссылки"""

        video_id = re.findall(r'(?<=be/).{11}', url)
        if not video_id:
            video_id = re.findall(r'(?<==).*', url)
        return video_id[0]
