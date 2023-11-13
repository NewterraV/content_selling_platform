import os
from PIL import Image
import requests
from config import settings


class WorkImage:

    def __init__(self):
        self.media_path = settings.MEDIA_ROOT

    def get_file_from_link(self, link: str, path_to: str,
                           filename: str) -> str:
        """
        Метод принимает ссылку и сохраняет полученное изображение по
        указанному пути.
        :param link: Ссылка на изображение
        :param path_to: Путь сохранения
        :param filename: Имя файла
        :return: Путь до сохраненного файла
        """

        response = requests.get(link)
        try:
            os.makedirs(os.path.join(self.media_path, path_to))
        except FileExistsError:
            print('Директория уже существует')

        finally:
            root = os.path.join(self.media_path, path_to, filename)

            with open(root, 'wb') as file:
                file.write(response.content)

        return os.path.join(path_to, filename)

    def crop_img(self, path_to):
        """
        Метод получает путь к файлу и обрезает изображение под необходимый
        размер.
        :param path_to: Пут
        :return:
        """

        img_path = os.path.join(self.media_path, path_to)
        box = (0, 60, 640, 420)
        img = Image.open(img_path)
        img_crop = img.crop(box)
        img_crop.save(img_path, quality=95)
