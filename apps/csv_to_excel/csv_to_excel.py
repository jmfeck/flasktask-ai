from flask import Blueprint, render_template, request, send_file, session, flash, redirect, url_for
import io
import pandas as pd

csv_to_excel_blueprint = Blueprint('csv_to_excel', __name__, template_folder='templates')

@csv_to_excel_blueprint.route('/', methods=['GET', 'POST'])
def show_csv_to_excel():
    if 'user' not in session:
        return redirect(url_for('login'))

    # Check if the user has access to this app
    if 2 not in session.get('my_apps', []):
        flash('You do not have access to this app.')
        return redirect(url_for('my_apps'))

    # We assume credits have already been deducted by launch_app
    if request.method == 'POST':
        file = request.files['file']
        if file.filename == '':
            flash('No file selected.')
            return redirect(url_for('csv_to_excel.show_csv_to_excel'))

        if not file.filename.endswith('.csv'):
            flash('Please upload a CSV file.')
            return redirect(url_for('csv_to_excel.show_csv_to_excel'))

        # Convert CSV to Excel
        df = pd.read_csv(file)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Sheet1')
        output.seek(0)

        # Send the file to the user
        return send_file(output, as_attachment=True, download_name='converted_excel.xlsx')

    return render_template('csv_to_excel.html', credits=session['credits'])
