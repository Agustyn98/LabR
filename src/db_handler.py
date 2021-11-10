import sqlite3
from sqlite3 import Error
from patient import *
from result import Result
import os

db_file = 'database.db'


def validate_patient(dni, password):
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    cur.execute(
        f"SELECT * FROM patient WHERE dni = ? and password = ?", (dni, password))
    row = cur.fetchall()
    conn.close()
    if row:
        for patient in row:
            return Patient(id=patient[0], name=patient[1], dni=patient[2])
    else:
        return False


def verify_password(id, old_pass):
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    cur.execute(
        "SELECT password FROM patient WHERE id = ?", (str(id)))
    row = cur.fetchall()
    conn.close()
    if row:
        for patient in row:
            if patient[0] == old_pass:
                return True


def change_password(id, old_pass, new_pass):
    if verify_password(id, old_pass):
        conn = sqlite3.connect(db_file)
        cur = conn.cursor()
        cur.execute("update patient set password = ? where id = ?",
                    (new_pass, str(id)))
        conn.commit()
        conn.close()
        return True
    else:
        return False


def get_results_from_patient(id):
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM result WHERE id_patient = { id }")
    rows = cur.fetchall()
    conn.close()
    results = []
    if rows:
        for result in rows:
            results.append(
                Result(id=result[0], date=result[1], file_path=result[2], id_patient=result[3]))
        return results
    else:
        return False


def add_patient(patient):
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    cur.execute('INSERT INTO patient(name, dni, password) VALUES(?, ?, ?)',
                (patient.name, str(patient.dni), str(patient.dni)))
    conn.commit()
    conn.close()


def add_result(result):
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    cur.execute('INSERT INTO result(date, file_path, id_patient) VALUES(?, ?, ?)',
                (result.date, str(result.file_path), str(result.id_patient)))
    conn.commit()
    conn.close()


def get_patients():
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    sql = "select patient.id, patient.name, patient.dni, count(result.id_patient) FROM patient LEFT JOIN result ON patient.id = result.id_patient GROUP BY patient.id ORDER BY patient.name"
    cur.execute(sql)
    rows = cur.fetchall()
    conn.close()
    patients = []
    if rows:
        for patient in rows:
            print(patient)
            patient = Patient(
                id=patient[0], name=patient[1], dni=patient[2], number_of_results=patient[3])
            patients.append(patient)
        return patients


def get_results():
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    sql = "SELECT result.*, patient.name, patient.dni FROM result, patient WHERE result.id_patient = patient.id"
    cur.execute(sql)
    rows = cur.fetchall()
    conn.close()
    patients = []
    if rows:
        return rows


def delete_patient(id):
    delete_files_from_patient(id)
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    cur.executescript(
        f"DELETE FROM result WHERE id_patient={id}; DELETE FROM patient WHERE id={id};")
    conn.close()


def delete_files_from_patient(id):
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    cur.execute(f'SELECT file_path FROM result WHERE id_patient = { id }')
    rows = cur.fetchall()
    if rows:
        for filename in rows:
            path = f"../results/{ filename[0] }"
            os.remove(path)
    conn.close()


def delete_result(id):
    delete_result_file(id)
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    cur.execute(f'DELETE FROM result WHERE id = { id }')
    conn.commit()
    conn.close()


def delete_result_file(id):
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    cur.execute(f'SELECT file_path FROM result WHERE id = { id }')
    row = cur.fetchall()
    if row:
        for filename in row:
            path = f"../results/{ filename[0] }"
            os.remove(path)


def get_patient(id):
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM patient WHERE id = { id } ")
    row = cur.fetchall()
    if row:
        for patient in row:
            return Patient(id=patient[0], name=patient[1], dni=patient[2])


def get_result(id):
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM result WHERE id = { id } ")
    row = cur.fetchall()
    if row:
        for result in row:
            return Result(id=result[0], date=result[1], file_path=result[2], id_patient=result[3])


def update_patient(id, name, dni):
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    cur.execute(
        f"UPDATE patient SET name = '{ name }', dni = { dni } WHERE id = { id }")
    conn.commit()
    conn.close()


def update_result(id, date, id_patient):
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    cur.execute(
        f"UPDATE result SET date = '{ date }', id_patient = { id_patient } WHERE id = { id }")
    conn.commit()
    conn.close()


def reset_password(id):
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    cur.execute(
        f"UPDATE patient SET password=(SELECT dni FROM patient WHERE id={id}) WHERE id={id}")
    conn.commit()
    conn.close()


def get_filepaths_from_patient(id):
    sql = f"SELECT result.file_path FROM patient,result WHERE patient.id = result.id_patient AND patient.id = { id }"
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    conn.close()
    results = []
    if rows:
        for result in rows:
            results.append(result)
        return results
