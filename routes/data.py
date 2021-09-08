import logging

from flask import Blueprint, request, render_template
from monolithic.forms.data_form import FileUploadForm

NAME = 'data'
bp = Blueprint(NAME, __name__, url_prefix=f'/{NAME}')

@bp.route('/file', methods=['GET', 'POST'])
def file():
    form = FileUploadForm()
    if request.method == 'GET':
        print(f"this is {request.method} method")
        return render_template(f'{NAME}/file_upload.html', form=form)
    else:
        # if form.validate_on_submit():
        # print(form.validate_on_submit(), type(form.file.data), dir(form.file.data))
        print(form.file.data.read().decode())
        return "<h1>thanks for data</h1>"
