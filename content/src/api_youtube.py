from config import settings
from content.src.base import BaseAPI
from googleapiclient.discovery import build


class YouTubeAPI(BaseAPI):
    """Класс для работы с API YouTube"""

    def __init__(self):
        self.token = settings.API_YOUTUBE_TOKEN
        self.youtube = build(
            'youtube',
            'v3',
            developerKey=self.token
        )

    def get_video_cover(self, video_id: str) -> str:
        """
        Метод получает ссылку на обложку видео
        :param video_id: Идентификатор видео
        :return: Ссылка на обложку видео
        """
        video_response = self.youtube.videos().list(
            part='snippet',
            id=video_id
        ).execute()
        snippet = video_response['items'][0]['snippet']

        return snippet['thumbnails']['standard']['url']
