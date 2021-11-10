from flask import Flask
from flask import request
from flask import render_template
from flask import session
from flask import abort, redirect, url_for, send_from_directory, flash
import time
import db_handler
from patient import Patient
from result import Result

app = Flask(__name__)
app.secret_key = 'lqzn!ew31!ew32cq=w!ewfe34312cq=w!1'


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/login", methods=['GET', 'POST'])
def login_patient():
    if 'id' in session:
        return redirect(url_for('show_patient_results'))

    if request.method == 'GET':
        return render_template('login_user.html')
    else:
        dni = request.form['dni']
        password = request.form['password']
        patient = db_handler.validate_patient(dni, password)
        if not patient:
            flash('Usuario o contraseña incorrecta')
            return render_template('login_user.html')
        session['id'] = patient.id
        session['name'] = patient.name
        return redirect(url_for('show_patient_results'))


@app.route('/logout')
def logout():
    session.pop('id', None)
    session.pop('admin', None)
    return redirect(url_for('index'))


@app.route('/resultados')
def show_patient_results():
    if 'id' not in session:
        return redirect(url_for('login_patient'))

    results = db_handler.get_results_from_patient(session['id'])
    return render_template('results.html', name=session['name'], results=results)


@app.route('/cambiar_contrasena', methods=['GET', 'POST'])
def change_password():
    if 'id' not in session:
        return redirect(url_for('login_patient'))
    if request.method == 'GET':
        return render_template('change_password.html')
    else:
        old_pass = request.form['old_pass']
        new_pass1 = request.form['new_pass1']
        new_pass2 = request.form['new_pass2']
        if new_pass1 != new_pass2:
            flash('ERROR: Las contraseñas no son iguales')
            return render_template('change_password.html')

        if db_handler.change_password(session['id'], old_pass, new_pass1):
            flash('Contraseña cambiada con exito !')
            return render_template('change_password.html')

        return "Error"


@app.route('/admin', methods=['GET', 'POST'])
@app.route('/admin/', methods=['GET', 'POST'])
def login_admin():
    if 'admin' in session:
        return redirect(url_for('admin_main'))

    if request.method == 'GET':
        return render_template('admin_login.html')
    else:
        user = request.form['user']
        password = request.form['password']
        print(user, password)
        if user == 'admin' and password == '123':
            session['admin'] = True
            return redirect(url_for('admin_main'))
        else:
            flash('Usuario o contraseña incorrecta')
            return render_template('admin_login.html')


@app.route('/admin_main', methods=['GET', 'POST'])
def admin_main():
    check_admin_privilages()
    return render_template('admin_main.html')


@app.route('/admin/paciente/nuevo', methods=['GET', 'POST'])
def new_patient():
    check_admin_privilages()
    if request.method == 'GET':
        return render_template('admin_add_patient.html')
    else:
        name = request.form['name']
        dni = request.form['dni']
        patient = Patient(name=name, dni=dni)
        db_handler.add_patient(patient)
        flash(f'Paciente {name} añadido')
        return render_template('admin_add_patient.html')


@app.route('/admin/pacientes')
def show_list_of_patients():
    check_admin_privilages()
    patients = db_handler.get_patients()
    return render_template('admin_list_patients.html', patients=patients)


@app.route('/admin/resultados')
def show_list_of_results():
    check_admin_privilages()
    results = db_handler.get_results()
    return render_template('admin_list_results.html', results=results)


@app.route('/admin/paciente/<int:id>')
def show_patient_results_admin(id):
    check_admin_privilages()
    results = db_handler.get_results_from_patient(id)
    name = db_handler.get_patient(id).name
    return render_template('admin_view_patient.html', name=name, results=results)


@app.route('/admin/paciente/<int:id>/modificar', methods=['GET', 'POST'])
def modify_patient(id):
    check_admin_privilages()
    if request.method == 'GET':
        patient = db_handler.get_patient(id)
        return render_template('admin_modify_patient.html', patient=patient)
    else:
        name = request.form['name']
        dni = request.form['dni']
        db_handler.update_patient(id, name=name, dni=dni)
        return f"Paciente modificado <a href='{url_for('show_list_of_patients')}'>&larr; Volver</a>"


@app.route('/admin/resultado/<int:id>/eliminar')
def delete_result(id):
    check_admin_privilages()
    db_handler.delete_result(id)
    return f"Resulado eliminado <br> <a href='{url_for('admin_main')}'>&larr; Volver</a>"


@app.route('/admin/resultado/<int:id>/modificar', methods=['GET', 'POST'])
def modify_result(id):
    check_admin_privilages()
    if request.method == 'GET':
        result = db_handler.get_result(id)
        patient = db_handler.get_patient(result.id_patient)
        patients = db_handler.get_patients()
        return render_template('admin_modify_result.html', patient=patient, result=result, patients=patients)
    else:
        patient_id = request.form['patient']
        date = request.form['date']
        if not patient_id.isnumeric():
            return f"ERROR: Debe seleccionar un paciente <a href='{url_for('show_list_of_patients')}'>&larr; Volver</a>"
        db_handler.update_result(id=id, date=date, id_patient=patient_id)
        return f"Resultado modificado <a href='{url_for('show_list_of_patients')}'>&larr; Volver</a>"


@app.route('/admin/paciente/<int:id>/reestablecer-contrasena')
def reset_password(id):
    check_admin_privilages()
    db_handler.reset_password(id)
    return f"Contraseña reestablecida (usuario: dni, contraseña: dni) <br> <a href='{url_for('show_list_of_patients')}'>&larr; Volver</a>"


@app.route('/admin/paciente/<int:id>/eliminar')
def delete_patient(id):
    check_admin_privilages()
    db_handler.delete_patient(id)
    return f"Usuario eliminado <br> <a href='{url_for('show_list_of_patients')}'>&larr; Volver</a>"


@app.route('/admin/cargar', methods=['GET', 'POST'])
def add_result():
    check_admin_privilages()
    if request.method == 'GET':
        patients = db_handler.get_patients()
        return render_template('admin_add_result.html', patients=patients)
    else:
        patients = db_handler.get_patients()
        if 'file' not in request.files:
            return "No se subio ningun archivo"
        patient_id = request.form['patient']
        date = request.form['date']
        if not patient_id.isnumeric():
            flash('ERROR: no se selecciono un paciente')
            return render_template('admin_add_result.html', patients=patients)
        file = request.files['file']
        print('FILE TYPE:')
        print(type(file))
        print(file)
        epoch_time = str(time.time())
        epoch_time = epoch_time.split('.')[0]
        filename = f"{ patient_id }-{ epoch_time }.pdf"
        db_handler.add_result(
            Result(date=date, file_path=filename, id_patient=patient_id))
        file.save(f'../results/{ filename }')
        flash('Paciente Cargado')
        return render_template('admin_add_result.html', patients=patients)


@app.route('/descargar/<filename>')
def download_file(filename):
    if 'admin' in session and session['admin']:
        return send_from_directory('../results/', filename)
    else:
        results = db_handler.get_filepaths_from_patient(session['id'])
        print('compare:')
        print(results)
        print(filename)
        if (filename,) in results:
            return send_from_directory('../results/', filename)
        else:
            abort(403)


def check_admin_privilages():
    if 'admin' not in session or not session['admin']:
        abort(403)
