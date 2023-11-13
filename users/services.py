

def user_directory_path_content(instance, filename):
    # file will be uploaded to MEDIA_ROOT / user_<id>/<filename>
    print(instance.owner)
    return f'user_{instance.owner.id}/content/{filename}'


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT / user_<id>/<filename>
    return f'user_{instance.pk}/{filename}'
