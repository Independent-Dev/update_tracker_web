import requests, redis, json
from enum import IntEnum
from collections import namedtuple

from flask import current_app
from monolithic.tasks.mail import send_email_celery
from monolithic.utils.common import from_utc_to_local

PackageData = namedtuple(
    'PackageData', [
        'current_version', 'updated_version', 'upload_time'
        ]
    )


class Level(IntEnum):
    MAJOR = 1
    MINOR = 2
    PATCH = 3


class UpdateTracker:
    def __init__(self, package_info, user_email) -> None:
        self.package_info = package_info
        self.error = dict()
        self.user_email = user_email
        self.redis = Redis()

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
                self.error[package_name] = f"Unknown info format. Check on {current_app.config['PYPI_SEARCH_URL_FORMAT'].format(package_name)}"
            except Exception as e:
                current_app.logger.critical(e)
                self.error[package_name] = str(e)

        self.redis.cache_update()

        self.package_info = updated_package_info

    def fetch_data(self, package_name, package_data):
        fetched_data = self.redis.conn.get(current_app.config["REDIS_PACKAGE_NAME_PREFIX"] + package_name)

        if not fetched_data:
            current_app.logger.info(f"{package_name} not in redis")
            fetched_data = self.redis.fetch_updated_package_data(package_name)
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
                for i in range(min(len(self.result), len(current_package_version), len(updated_package_version))):
                    if current_package_version[i] != updated_package_version[i]:
                        self.result[i][package_name] = package_data
                        break
                else:
                    self.result[-1][package_name] = package_data

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


class Redis:
    def __init__(self) -> None:
        self.conn = redis.StrictRedis(host=current_app.config["REDIS_HOST"], port=6379, db=0, password=current_app.config["REDIS_PASSWORD"])
        self.package_data = dict()

    def get_keys(self):
        package_name_list = self.conn.keys(f"[{current_app.config['REDIS_PACKAGE_NAME_PREFIX']}]*")
        return [package_name.decode().strip(current_app.config["REDIS_PACKAGE_NAME_PREFIX"]) for package_name in package_name_list]

    def fetch_updated_package_data(self, package_name):
        result = requests.get(current_app.config['PYPI_SEARCH_URL_FORMAT'].format(package_name))

        if result.status_code == 200:
            result_json = result.json()
            updated_version = result_json["info"]["version"]
            upload_time = result_json["releases"][updated_version][0]["upload_time"].replace("T", " ")

            fetched_data = dict(
                updated_version=updated_version,
                upload_time=from_utc_to_local(upload_time)
            )

            self.package_data[current_app.config["REDIS_PACKAGE_NAME_PREFIX"] + package_name] = json.dumps(fetched_data, ensure_ascii=False).encode('utf-8')

            return fetched_data
        else:
            raise ValueError('Package not found in PyPI')

    def cache_update(self):
        if self.package_data:
            current_app.logger.info("package data update 시작")
            current_app.logger.info(f"업데이트 필요 패키지: {self.package_data.keys()}")
            self.conn.mset(self.package_data)
