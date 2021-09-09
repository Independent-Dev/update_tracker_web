import requests
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
    
    def report_package_info(self):
        self.get_updated_package_info()
        self.compare_current_and_updated_package_info()

        context = dict(
            level=Level, 
            result_list=self.result, 
            field_list=PackageData._fields, 
            error_dict=self.error)

        send_email_celery(
            subject='패키지 리포트',
            recipient=self.user_email,
            template='email/package_report_email',
            **context
        )


    def get_updated_package_info(self):
        SEARCH_URL = "https://pypi.python.org/pypi/{}/json"
        updated_package_info = dict()

        # 여기서 idx
        for idx, (package_name, package_data) in enumerate(self.package_info.items(), start=1):
            result = requests.get(SEARCH_URL.format(package_name))
            
            try:
                if result.status_code != 200:
                    raise ValueError('Package not found in PyPI')  # 에러의 종류 좀 더 생각해보기
                result_json = result.json()
                updated_version = result_json["info"]["version"]
                updated_package_info[package_name] = PackageData(
                    **package_data,
                    updated_version = updated_version,
                    upload_time = result_json["releases"][updated_version][0]["upload_time"].replace("T", " ")
                )
            except IndexError:
                self.error[package_name] = f"Unknown info format. Check on {SEARCH_URL.format(package_name)}"
            except Exception as e:
                self.error[package_name] = str(e)

        self.package_info = updated_package_info

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
 