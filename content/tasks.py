from celery import shared_task
from content.src.services import get_image


@shared_task
def task_get_image(pk: str) -> None:
    """
    Отложенная задача по автоматическому получению обложки видео из API
    YouTube на основе ссылки на видео
    :param pk: primary_key записи о контенте в базе данных
    :return: None
    """
    get_image(pk)
