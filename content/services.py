import re


class RegExpressionsBase:
    pass


class RegExpressions(RegExpressionsBase):
    """Класс для работы с регулярными выражениями проекта"""

    @staticmethod
    def get_video_id(url):
        """Метод получает id_video из ссылки"""

        video_id = re.findall(r'(?<=be/)\w+', url)
        if not video_id:
            video_id = re.findall(r'(?<==)\w+', url)
        return video_id[0]
