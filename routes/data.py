from flask import Blueprint, request, render_template, current_app
from flask_login import current_user
from monolithic.forms.data_form import FileUploadForm
import json

from monolithic.tasks.data import analyze_and_report_package_data

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

