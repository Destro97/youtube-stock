from schedule import Scheduler
import threading
import time
from datetime import datetime


from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


from .models import Video


page_token = None
api_keys = [
    "AIzaSyCNchRAFaJXrHbczf4I3d-vCjmgOoeBrhI",
    "AIzaSyDB5g6WxgaERxXjLdArg8aTySlHeu8JMIk",
    "AIzaSyBTh5fZwND58gyhImFoDsJX98nNFGpRfB8",
    "AIzaSyAaYJFJ4FEkXxTrSUHhtyKh3ZX71VTcI-k",
    "AIzaSyDlWK50iYEee4z9ISQiAdo5adECc7bXf6Y"
]
key_index = 0


def fetch_youtube_search_results_helper(key_index):
    global api_keys
    DEVELOPER_KEY = api_keys[key_index]
    YOUTUBE_API_SERVICE_NAME = 'youtube'
    YOUTUBE_API_VERSION = 'v3'
    youtube_api = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)
    global page_token
    search_query = 'official'
    pub_after_date = datetime(2019, 12, 1).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    response = youtube_api.search().list(
        q=search_query,
        order='date',
        maxResults=20,
        type='video',
        pageToken=page_token,
        publishedAfter=pub_after_date,
        part='id,snippet',
        fields='nextPageToken,items(id(videoId),snippet(title,description,channelTitle,publishedAt,thumbnails/default/url))'
    ).execute()
    return response


def fetch_youtube_search_results():
    global api_keys
    global key_index
    response = {}
    init_key_index = key_index
    try:
        response = fetch_youtube_search_results_helper(key_index)
    except HttpError as e:
        error_reason = e._get_reason().lower()
        error_status = e.resp.status
        if error_status == 403 and 'exceed' in error_reason and 'quota' in error_reason:
            print(f"Quota exceeded for API KEY with index {key_index}")
            key_index += 1
            key_index = key_index % len(api_keys)
            while key_index != init_key_index:
                print(f"Trying to fetch youtube results from API KEY with index {key_index}")
                try:
                    response = fetch_youtube_search_results_helper(key_index)
                except HttpError as e:
                    error_reason = e._get_reason().lower()
                    error_status = e.resp.status
                    if error_status == 403 and 'exceed' in error_reason and 'quota' in error_reason:
                        print(f"Quota exceeded for API KEY with index {key_index}")
                        key_index += 1
                        key_index = key_index % len(api_keys)
                    else:
                        print(f'Some error occured fetching youtube results as {e}')
                        raise Exception('Internal error')
                except Exception as e:
                    print(f'Some error occured fetching youtube results as {e}')
                    raise Exception('Internal error')
                else:
                    break
            else:
                print("All api keys quota exceeded")
                raise Exception("Quota exceeded for all API KEYs")
        else:
            print(f'Some error occured fetching youtube results as {e}')
            raise Exception('Internal error')
    except Exception as e:
        print(f'Some error occured fetching youtube results as {e}')
        raise Exception('Internal error')
    return response


def youtube_fetch_task():
    print("Starting to fetch videos from Youtube with Search Filter: 'official'")
    global page_token
    try:
        search_response = fetch_youtube_search_results()
    except Exception as e:
        print(f"Could not fetch youtube videos due to error {e}")
    else:
        if not search_response.get('items', []):
            print("No results found while fetching videos")
            print("Task Finishes")
            return
        print("Starting to store results in DB")
        if search_response.get('nextPageToken'):
            page_token = search_response['nextPageToken']
        video_items = search_response.get('items', [])
        model_items = []
        for item in video_items:
            model_item = {
                "video_id": item.get('id', {}).get('videoId', ''),
                "title": item.get('snippet', {}).get('title', ''),
                "description": item.get('snippet', {}).get('description', ''),
                "published_at": item.get('snippet', {}).get('publishedAt', ''),
                "publisher": item.get('snippet', {}).get('channelTitle', ''),
                "thumbnail": item.get('snippet', {}).get('thumbnails', {}).get('default', {}).get('url')
            }
            model_items.append(Video(
                video_id=model_item['video_id'],
                title=model_item['title'],
                description=model_item['description'],
                published_at=model_item['published_at'],
                publisher=model_item['publisher'],
                thumbnail=model_item['thumbnail']
            ))
        try:
            Video.objects.bulk_create(model_items)
        except Exception as e:
            print(f'DB Save Error: {e}')
        else:
            print("Storing in DB successful")
    print("Task Finished")


## Referenced from https://stackoverflow.com/questions/44896618/django-run-a-function-every-x-seconds
## Also from https://schedule.readthedocs.io/en/stable/faq.html#how-to-continuously-run-the-scheduler-without-blocking-the-main-thread
def run_continuously(self, interval=1):
    cease_continuous_run = threading.Event()

    class ScheduleThread(threading.Thread):

        @classmethod
        def run(cls):
            while not cease_continuous_run.is_set():
                self.run_pending()
                time.sleep(interval)

    continuous_thread = ScheduleThread()
    continuous_thread.setDaemon(True)
    continuous_thread.start()
    return cease_continuous_run


Scheduler.run_continuously = run_continuously


def start_scheduler():
    scheduler = Scheduler()
    scheduler.every(10).seconds.do(youtube_fetch_task)
    scheduler.run_continuously()
