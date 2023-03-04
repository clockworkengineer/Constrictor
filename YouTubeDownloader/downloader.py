from googleapiclient.discovery import build

API_KEY = 'AIzaSyDRVXAVB3k5RUt8jJTD-qBemEcMGKkpZXQ'

youtube = build('youtube', 'v3', developerKey=API_KEY)

request = youtube.channels().list(
    part='statistics',
    forUsername='schafer5'
)

response = request.execute()

print(response)
