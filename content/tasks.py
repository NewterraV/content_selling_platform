from celery import shared_task
from content.src.services import get_image
from content.src.work_image import WorkImage


@shared_task
def task_get_image(pk: str) -> None:
    """
    Отложенная задача по автоматическому получению обложки видео из API
    YouTube на основе ссылки на видео
    :param pk: primary_key записи о контенте в базе данных
    :return: None
    """
    get_image(pk)


@shared_task
def task_delete_img(path_to: str) -> None:
    """
    Отложенная задача по удалению изображений
    :param path_to: Путь до изображения
    :return: None
    """
    WorkImage().delete_file(path_to=path_to)

