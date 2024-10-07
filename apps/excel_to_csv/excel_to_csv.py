from flask import Blueprint, render_template, request, send_file, session, flash, redirect, url_for
import io
import pandas as pd
import zipfile

excel_to_csv_blueprint = Blueprint('excel_to_csv', __name__, template_folder='templates')

@excel_to_csv_blueprint.route('/', methods=['GET', 'POST'])
def show_excel_to_csv():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    # Check if the user has access to this app
    if 1 not in session.get('my_apps', []):
        flash('You do not have access to this app.')
        return redirect(url_for('my_apps'))

    if request.method == 'POST':
        # Check if the user has enough credits
        if session['credits'] <= 0:
            flash('You do not have enough credits to use this app.')
            return redirect(url_for('buy_credits'))

        files = request.files.getlist('file')
        if not files or files[0].filename == '':
            flash('No file selected.')
            return redirect(url_for('excel_to_csv.show_excel_to_csv'))

        # Process files and create a ZIP archive
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for file in files:
                if file.filename.endswith('.xlsx'):
                    csv_file = convert_to_csv(file)
                    zip_file.writestr(file.filename.replace('.xlsx', '.csv'), csv_file.getvalue().encode('utf-8'))
                else:
                    flash('Invalid file format. Please upload .xlsx files.')
                    return redirect(url_for('excel_to_csv.show_excel_to_csv'))

        # Deduct 1 credit
        users[session['user']]['credits'] -= 1
        session['credits'] = users[session['user']]['credits']
        flash(f'1 credit used. You have {session["credits"]} credits remaining.')

        # Send the ZIP file back to the user
        zip_buffer.seek(0)
        return send_file(zip_buffer, as_attachment=True, download_name='converted_csvs.zip')

    return render_template('excel_to_csv.html', credits=session['credits'])

def convert_to_csv(file):
    df = pd.read_excel(file)
    output = io.StringIO()
    df.to_csv(output, index=False)
    return output
