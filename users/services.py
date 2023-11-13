

def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT / user_<id>/<filename>
    print(instance.owner)
    return 'content/user_{0}/{1}'.format(instance.owner, filename)
