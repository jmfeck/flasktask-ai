from flask import Blueprint, render_template, request, send_file, session, flash, redirect, url_for
from PyPDF2 import PdfMerger
import io

pdf_merger_blueprint = Blueprint('pdf_merger', __name__, template_folder='templates')

@pdf_merger_blueprint.route('/', methods=['GET', 'POST'])
def show_pdf_merger():
    if 'user' not in session:
        return redirect(url_for('login'))

    # Check if the user has access to this app
    if 3 not in session.get('my_apps', []):
        flash('You do not have access to this app.')
        return redirect(url_for('my_apps'))

    if request.method == 'POST':
        # Check if the user has enough credits
        if session['credits'] <= 0:
            flash('You do not have enough credits to use this app.')
            return redirect(url_for('buy_credits'))

        files = request.files.getlist('files')
        if len(files) < 2:
            flash('Please upload at least two PDF files.')
            return redirect(url_for('pdf_merger.show_pdf_merger'))

        merger = PdfMerger()

        for file in files:
            if not file.filename.endswith('.pdf'):
                flash('Please upload only PDF files.')
                return redirect(url_for('pdf_merger.show_pdf_merger'))
            merger.append(file)

        output = io.BytesIO()
        merger.write(output)
        output.seek(0)

        # Deduct 1 credit
        users[session['user']]['credits'] -= 1
        session['credits'] = users[session['user']]['credits']
        flash(f'1 credit used. You have {session["credits"]} credits remaining.')

        return send_file(output, as_attachment=True, download_name='merged_pdf.pdf')

    return render_template('pdf_merger.html', credits=session['credits'])