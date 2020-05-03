from django.apps import AppConfig
import os


class AppConfig(AppConfig):
    name = 'app'

    def ready(self):
        from . import task
        ## This function is called twice by runserevr command and this check
        ## handles calling the thread to invoke youtube fetch task only once
        ## when the server is finally started
        if os.environ.get('RUN_MAIN', None) != 'true':
            task.start_scheduler()
