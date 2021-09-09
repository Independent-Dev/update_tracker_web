from flask import Blueprint, request, render_template, redirect
from flask_login import current_user
from monolithic.forms.data_form import FileUploadForm

from monolithic.tasks.data import analyze_and_report_package_data

NAME = 'data'
bp = Blueprint(NAME, __name__, url_prefix=f'/{NAME}')

@bp.route('/file/', methods=['GET', 'POST'])
def file():
    form = FileUploadForm()
    if request.method == 'GET':
        print(f"this is {request.method} method")
        return render_template(f'{NAME}/file_upload.html', form=form)
    else:        
        if form.validate_on_submit():
            try:
                package_info = dict()
                SPLIT_WORD = "=="
                data_list = form.file.data.read().decode().strip().split("\n")
                data_list = [data.split(SPLIT_WORD) if SPLIT_WORD in data else [data, "0.0.0"] for data in data_list]
                for package_name, package_version in data_list:
                    package_info[package_name] = {"current_version": package_version}
            except Exception as e:
                print(e)
            else:
                print("analyze_and_report_package_data!!!!")

                analyze_and_report_package_data.delay(package_info, form.user_email.data or current_user.user_email)
        print("post is working ", form.errors)
        return redirect(request.path)
