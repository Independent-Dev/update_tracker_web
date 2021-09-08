from flask import flash

def flash_form_errors(form):
    for _, errors in form.errors.items():
        for e in errors:
            flash(e)