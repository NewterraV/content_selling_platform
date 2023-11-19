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
