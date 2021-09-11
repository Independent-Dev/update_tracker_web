import requests, redis, json
from flask import current_app
from enum import IntEnum
from collections import namedtuple
from monolithic.tasks.mail import send_email_celery

class Level(IntEnum):
    MAJOR = 1
    MINOR = 2
    MICRO = 3

PackageData = namedtuple(
    'PackageData', [
        'current_version', 'updated_version', 'upload_time'
        ]
    )

class UpdateTracker:
    def __init__(self, package_info, user_email) -> None:
        self.package_info = package_info
        self.error = dict()
        self.user_email=user_email
        self.redis = redis.StrictRedis(host='localhost', port=6379, db=0)
        self.SEARCH_URL = "https://pypi.python.org/pypi/{}/json"
    

    def report_package_info(self):
        self.get_updated_package_info()
        self.compare_current_and_updated_package_info()
        self.make_report()


    def get_updated_package_info(self):
        updated_package_info = dict()
        
        for package_name, package_data in self.package_info.items():    
            try:
                updated_package_info[package_name] = self.fetch_data(package_name, package_data)
            except IndexError:
                self.error[package_name] = f"Unknown info format. Check on {self.SEARCH_URL.format(package_name)}"
            except Exception as e:
                self.error[package_name] = str(e)

        self.package_info = updated_package_info
    
    def fetch_data(self, package_name, package_data):
        fetched_data = self.redis.get(package_name)

        if not fetched_data:
            current_app.logger.info(f"{package_name} not in redis")
            result = requests.get(self.SEARCH_URL.format(package_name))

            if result.status_code != 200:
                raise ValueError('Package not found in PyPI')  # TODO 에러의 종류 좀 더 생각해보기

            result_json = result.json()
            updated_version = result_json["info"]["version"]

            fetched_data = dict(
                updated_version = updated_version,
                upload_time = result_json["releases"][updated_version][0]["upload_time"]
            )

            self.redis.set(package_name, json.dumps(fetched_data, ensure_ascii=False).encode('utf-8'))

        else:
            current_app.logger.info(f"{package_name} already in redis")
            fetched_data = json.loads(fetched_data.decode("utf-8"))
            
        return PackageData(
            **package_data,
            **fetched_data
        )

    def compare_current_and_updated_package_info(self):
        self.result = [{} for _ in range(len(Level))]
        for package_name, package_data in self.package_info.items():
            if package_data.current_version != package_data.updated_version:  
                current_package_version = package_data.current_version.split(".")
                updated_package_version = package_data.updated_version.split(".")
                for i in range(min(len(self.result), len(current_package_version))):
                    if current_package_version[i] != updated_package_version[i]:
                        self.result[i][package_name] = package_data
                        break
    
    def make_report(self):
        context = dict(
            level=Level, 
            result_list=self.result, 
            field_list=PackageData._fields, 
            error_dict=self.error
        )
        
        send_email_celery(
            subject='패키지 리포트',
            recipient=self.user_email,
            template='email/package_report_email',
            **context
        )
 