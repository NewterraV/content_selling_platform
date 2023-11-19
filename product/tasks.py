from celery import shared_task
from product.src.Payment import UserProduct
from product.src.api_stripe import APIStripe


@shared_task
def task_create_product(pk: str) -> None:
    """
    Отложенная задача по автоматическому получению id продукта и цены из API
    Stripe на основе ссылки на видео
    :param pk: primary_key записи о продукте в базе данных
    :return: None
    """
    product = UserProduct(pk)
    product.create_ids_product()


@shared_task
def task_delete_product(product_id: str, ) -> None:
    """
    Отложенная задача удаляет продукт на стороне сервера stripe
    :param product_id: id продукта stripe
    :return: None
    """
    APIStripe().delete_product(product_id)


@shared_task
def task_update_product(product_id: str, ) -> None:
    """
    Отложенная задача удаляет продукт на стороне сервера stripe
    :param product_id: id продукта stripe
    :return: None
    """
    product = UserProduct(product_id)
    product.update_product()
