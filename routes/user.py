from flask import Blueprint, render_template, url_for, redirect
from flask_login import login_required, current_user

from monolithic.forms.data_form import FileUploadForm


NAME = 'user'
bp = Blueprint(NAME, __name__, url_prefix=f'/{NAME}')

@login_required
@bp.route("/mypage/")
def mypage():
    if current_user.is_authenticated:
        form = FileUploadForm()
        return render_template(f'{NAME}/my_page.html', form=form)
    return redirect(url_for('auth.login'))
