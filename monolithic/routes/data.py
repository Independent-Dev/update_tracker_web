from flask import Blueprint, request, render_template, current_app
from flask_login import current_user
from monolithic.forms.data_form import FileUploadForm
from monolithic import db
import json
from datetime import datetime, timedelta

from monolithic.tasks.data import analyze_and_report_package_data, update_redis_cache

NAME = 'data'
bp = Blueprint(NAME, __name__, url_prefix=f'/{NAME}')

@bp.route('/file/', methods=['GET', 'POST'])
def file():
    form = FileUploadForm()
    if request.method == 'GET':
        return render_template('index.html', form=form)

    else:       
        if form.validate_on_submit():
            user_email = form.user_email.data
            try:
                # TODO 이것도 update tracker 안에 넣어야 하는 것 아닌가. 
                package_info = dict()
                SPLIT_WORD = "=="
                data_list = form.file.data.read().decode().strip().split("\n")
                data_list = [data.split(SPLIT_WORD) if SPLIT_WORD in data else [data, "0.0.0"] for data in data_list]
                for package_name, package_version in data_list:
                    package_info[package_name] = {"current_version": package_version}
            except Exception as e:
                print(e)

            else:
                # TODO 이것도 try문 안에 넣어야 하는 것 아닌가...
                analyze_and_report_package_data.delay(package_info, user_email) 
                
            return json.dumps({"message": user_email + "로 패키지 리포트가 전송되었습니다.\n확인해주세요!!"}), 200
        else:
            current_app.logger.critical(form.errors)
            return json.dumps({"message": json.dumps(form.errors)}), 403

@bp.route('/redis/cache/', methods=["POST"])
def redis_cache_update():
    if not current_user.is_authenticated:
        return json.dumps({"message": "로그인하지 않은 사용자는 캐시 갱신 기능을 이용할 수 없습니다!"}), 401
    try:
        if datetime.now() - current_user.last_redis_cache_update_at < timedelta(hours=current_app.config['REDIS_CACHE_UPDATE_LIMIT_TIME']):
            return json.dumps({"message": f"캐시 갱신은 {current_app.config['REDIS_CACHE_UPDATE_LIMIT_TIME']}시간에 한 번씩만 할 수 있습니다."}), 401
        
        update_redis_cache()
        
        current_user.last_redis_cache_update_at = datetime.now()

        db.session.commit()

    except Exception as e:
        current_app.logger.critical(f"redis_cache_update error: {e}")
        return json.dumps({"message": "캐시 갱신 과정에서 에러가 발생하였습니다. 관리자에게 문의해주세요!"}), 403

    return json.dumps({"message": "캐시가 정상적으로 갱신되었습니다!"}), 200 

