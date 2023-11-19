import os


def user_directory_path_content(instance, filename=None):
    """
    Метод генерирует путь до файла на основе пользователя
    :param instance: Экземпляр пользователя
    :param filename: Имя файла
    :return:
    """
    if filename:
        return os.path.join('content', f'user_{instance.owner.id}', 'content',
                            filename)
    return os.path.join('content', f'user_{instance.owner.id}', 'content')


def user_directory_path(instance, filename):
    return f'user_{instance.pk}/{filename}'


def get_client_ip(request):
    """Метод возвращает ip клиента"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
