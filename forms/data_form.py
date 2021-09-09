from flask_wtf import FlaskForm
from wtforms import StringField
from flask_wtf.file import FileField
from wtforms.validators import DataRequired

class FileUploadForm(FlaskForm):
    user_email = StringField('user email')
    file = FileField('file', validators=[DataRequired()])
