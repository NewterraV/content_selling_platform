from content.models import Video, Content
from content.src.api_youtube import YouTubeAPI
from content.src.work_image import WorkImage
from users.services import user_directory_path_content


def get_image(pk: str) -> None:
    """
    Метод получает обложку видео из API
    YouTube на основе ссылки на видео
    :param pk: primary_key записи о контенте в базе данных
    :return: None
    """
    # Получаем экземпляр контента
    content = Content.objects.filter(pk=pk).first()

    if content:

        # Получаем url изображения
        video_id = content.video.video_id
        api = YouTubeAPI()

        try:
            img_url = api.get_video_cover(video_id=video_id)
        except IndexError:
            raise IndexError('Неверный id')
        else:

            #  Генерируем путь и сохраняем файл
            filename = f'{video_id}.jpg'
            path_to = user_directory_path_content(
                instance=content
            )
            img = WorkImage().get_file_from_link(
                link=img_url,
                path_to=path_to,
                filename=filename
            )

            # Сохраняем путь в бд
            content.image = img
            content.save()

            # Обрезаем изображение
            WorkImage().crop_img(img)
