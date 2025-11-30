from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from models import DoctorAvailability, TreatmentRecord, User, Doctor, Patient, Appointment, ROLE_ADMIN, ROLE_DOCTOR, ROLE_PATIENT
from extensions import db, bcrypt
from forms import AvailabilityForm, LoginForm, PatientRegistrationForm, DoctorRegistrationForm, AppointmentForm, TreatmentForm

main = Blueprint('main', __name__)


# ------------------ HOME ------------------
@main.route('/')
def index():
    return render_template('index.html')


# ------------------ LOGIN ------------------
@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash("Login successful!", "success")
            if user.role == ROLE_ADMIN:
                return redirect(url_for('main.admin_dashboard'))
            elif user.role == ROLE_DOCTOR:
                return redirect(url_for('main.doctor_dashboard'))
            else:
                return redirect(url_for('main.patient_dashboard'))
        flash("Invalid username or password", "danger")
    return render_template('login.html', form=form)


# ------------------ LOGOUT ------------------
@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out successfully", "info")
    return redirect(url_for('main.index'))

# ------------------ HMS Redirect ------------------
@main.route('/dashboard_redirect')
def dashboard_redirect():
    from flask import request

    if not current_user.is_authenticated:
        return redirect(request.referrer or url_for('main.index'))

    if current_user.role == ROLE_ADMIN:
        return redirect(url_for('main.admin_dashboard'))
    elif current_user.role == ROLE_DOCTOR:
        return redirect(url_for('main.doctor_dashboard'))
    elif current_user.role == ROLE_PATIENT:
        return redirect(url_for('main.patient_dashboard'))

    return redirect(url_for('main.index'))


# ------------------ REGISTER PATIENT ------------------
@main.route('/register', methods=['GET', 'POST'])
def register_patient():
    form = PatientRegistrationForm()
    if form.validate_on_submit():
        hashed = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(username=form.username.data,
                    password_hash=hashed,
                    role=ROLE_PATIENT)
        db.session.add(user)
        db.session.flush()  
        patient = Patient(user_id=user.id, name=form.name.data)
        db.session.add(patient)
        db.session.commit()
        flash("Registration successful! Please login.", "success")
        return redirect(url_for('main.login'))
    return render_template('register_patient.html', form=form)


# ------------------ ADMIN DASHBOARD ------------------
@main.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if current_user.role != ROLE_ADMIN:
        return redirect(url_for('main.index'))

    active_tab = request.args.get('tab', 'doctors')
    search_query = request.args.get('query', '').strip()

    doctors, patients, appointments = [], [], []
    add_doctor_form = None  

    if active_tab == 'doctors':
        query = Doctor.query.join(User, Doctor.user_id == User.id)
        if search_query:
            query = query.filter(
                (Doctor.name.ilike(f"%{search_query}%")) |
                (Doctor.specialization.ilike(f"%{search_query}%")) |
                (User.username.ilike(f"%{search_query}%"))
            )
        doctors = query.all()
        add_doctor_form = DoctorRegistrationForm()  

    elif active_tab == 'patients':
        query = Patient.query.join(User, Patient.user_id == User.id)
        if search_query:
            query = query.filter(
                (Patient.name.ilike(f"%{search_query}%")) |
                (User.username.ilike(f"%{search_query}%")) |
                (Patient.contact.ilike(f"%{search_query}%"))
            )
        patients = query.all()

    elif active_tab == 'appointments':
        query = Appointment.query.join(Appointment.patient).join(Appointment.doctor)
        if search_query:
            query = query.filter(
                (Patient.name.ilike(f"%{search_query}%")) |
                (Doctor.name.ilike(f"%{search_query}%"))
            )
        appointments = query.all()

    return render_template(
        'dashboards/admin_dashboard.html',
        active_tab=active_tab,
        search_query=search_query,
        doctors=doctors,
        patients=patients,
        appointments=appointments,
        total_doctors=Doctor.query.count(),
        total_patients=Patient.query.count(),
        total_appointments=Appointment.query.count(),
        add_doctor_form=add_doctor_form 
    )



# ------------------ ADD DOCTOR ------------------
@main.route('/admin/add_doctor', methods=['GET', 'POST'])
@login_required
def add_doctor():
    if current_user.role != ROLE_ADMIN:
        return redirect(url_for('main.index'))

    form = DoctorRegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash("Username already taken.", "danger")
            return redirect(url_for('main.admin_dashboard'))

        hashed = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(username=form.username.data, password_hash=hashed, role=ROLE_DOCTOR)
        db.session.add(user)
        db.session.flush()

        doctor = Doctor(user_id=user.id, name=form.name.data, specialization=form.specialization.data)
        db.session.add(doctor)
        db.session.commit()
        flash("Doctor added successfully!", "success")
        return redirect(url_for('main.admin_dashboard'))

    return render_template("forms/add_doctor.html", form=form, edit=False)


# ------------------ EDIT DOCTOR ------------------
@main.route('/admin/edit_doctor/<int:doctor_id>', methods=['GET', 'POST'])
@login_required
def edit_doctor(doctor_id):
    if current_user.role != ROLE_ADMIN:
        return redirect(url_for('main.index'))

    doctor = Doctor.query.get_or_404(doctor_id)

    form = DoctorRegistrationForm()

    if request.method == 'GET':
        form.name.data = doctor.name
        form.specialization.data = doctor.specialization
        form.username.data = doctor.user.username

    if form.validate_on_submit():
        doctor.name = form.name.data
        doctor.specialization = form.specialization.data
        doctor.user.username = form.username.data

        if form.password.data:
            doctor.user.password_hash = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        db.session.commit()
        flash("Doctor updated successfully!", "success")
        return redirect(url_for('main.admin_dashboard'))

    return render_template("forms/add_doctor.html", form=form, edit=True, doctor_id=doctor.id)


# ------------------ DELETE DOCTOR ------------------
@main.route('/admin/delete_doctor/<int:doctor_id>')
@login_required
def delete_doctor(doctor_id):
    if current_user.role != ROLE_ADMIN:
        return redirect(url_for('main.index'))

    doctor = Doctor.query.get_or_404(doctor_id)
    user = doctor.user
    db.session.delete(doctor)
    if user:
        db.session.delete(user)
    db.session.commit()
    flash("Doctor deleted successfully.", "success")
    return redirect(url_for('main.admin_dashboard'))


# ------------------ BLACKLIST DOCTOR ------------------
@main.route('/admin/blacklist_doctor/<int:doctor_id>')
@login_required
def blacklist_doctor(doctor_id):
    if current_user.role != ROLE_ADMIN:
        return redirect(url_for('main.index'))

    doctor = Doctor.query.get_or_404(doctor_id)
    doctor.user.is_blacklisted = not doctor.user.is_blacklisted
    db.session.commit()
    status = "blacklisted" if doctor.user.is_blacklisted else "unblocked"
    flash(f"Doctor {status} successfully.", "info")
    return redirect(url_for('main.admin_dashboard'))


# ------------------ ADMIN SEARCH ------------------
@main.route('/admin/search')
@login_required
def admin_search():
    if current_user.role != ROLE_ADMIN:
        return redirect(url_for('main.index'))

    query = request.args.get('query', '').strip()
    doctors, patients = [], []

    if query:
        # Search doctors
        doctors = Doctor.query.join(User, Doctor.user_id == User.id).filter(
            (Doctor.name.ilike(f"%{query}%")) |
            (Doctor.specialization.ilike(f"%{query}%")) |
            (User.username.ilike(f"%{query}%"))
        ).all()

        # Search patients
        patients = Patient.query.join(User, Patient.user_id == User.id).filter(
            (Patient.name.ilike(f"%{query}%")) |
            (User.username.ilike(f"%{query}%")) |
            (Patient.contact.ilike(f"%{query}%"))
        ).all()

    add_doctor_form = DoctorRegistrationForm() 

    return render_template('dashboards/admin_dashboard.html',
                           total_doctors=Doctor.query.count(),
                           total_patients=Patient.query.count(),
                           total_appointments=Appointment.query.count(),
                           doctors=doctors,
                           patients=patients,
                           search_query=query,
                           add_doctor_form=add_doctor_form)



# ------------------ DOCTOR DASHBOARD ------------------
@main.route('/doctor_dashboard')
@login_required
def doctor_dashboard():
    if current_user.role != ROLE_DOCTOR:
        return redirect(url_for('main.index'))

    doctor = Doctor.query.filter_by(user_id=current_user.id).first()

    availability_form = AvailabilityForm()
    treatment_form = TreatmentForm() 

    upcoming = Appointment.query.filter_by(
        doctor_id=doctor.id, status="Booked"
    ).all()

    patients = [appt.patient for appt in Appointment.query.filter_by(
        doctor_id=doctor.id
    ).all()]

    return render_template(
        'dashboards/doctor_dashboard.html',
        doctor=doctor,
        availability_form=availability_form,
        treatment_form=treatment_form,  
        upcoming=upcoming,
        patients=patients
    )



# ------------------ ADD AVAILABILITY ------------------
@main.route('/doctor/add_availability', methods=['POST'])
@login_required
def doctor_add_availability():
    if current_user.role != ROLE_DOCTOR:
        return redirect(url_for('main.index'))

    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    form = AvailabilityForm()

    if form.validate_on_submit():
        conflict = DoctorAvailability.query.filter(
            DoctorAvailability.doctor_id == doctor.id,
            DoctorAvailability.date == form.date.data,
            DoctorAvailability.start_time <= form.end_time.data,
            DoctorAvailability.end_time >= form.start_time.data
        ).first()

        if conflict:
            flash("This time range overlaps with an existing availability!", "danger")
        else:
            slot = DoctorAvailability(
                doctor_id=doctor.id,
                date=form.date.data,
                start_time=form.start_time.data,
                end_time=form.end_time.data
            )
            db.session.add(slot)
            db.session.commit()
            flash("Availability added!", "success")

    return redirect(url_for('main.doctor_dashboard'))


# ------------------ DELETE AVAILABILITY ------------------
@main.route('/doctor/availability/delete/<int:slot_id>', methods=['POST'])
@login_required
def delete_availability(slot_id):
    if current_user.role != ROLE_DOCTOR:
        return redirect(url_for('main.index'))

    slot = DoctorAvailability.query.get_or_404(slot_id)
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()

    if slot.doctor_id != doctor.id:
        flash("You cannot delete this slot.", "danger")
        return redirect(url_for('main.doctor_dashboard'))

    db.session.delete(slot)
    db.session.commit()
    flash("Availability removed.", "success")

    return redirect(url_for('main.doctor_dashboard'))



# ------------------ UPDATE APPOINTMENT STATUS ------------------
@main.route('/doctor/appointment/<int:appt_id>/status', methods=['POST'])
@login_required
def update_appointment_status(appt_id):
    if current_user.role != ROLE_DOCTOR:
        return redirect(url_for('main.index'))

    appt = Appointment.query.get_or_404(appt_id)
    new_status = request.form.get('status')

    if new_status in ["Completed", "Cancelled"]:
        appt.status = new_status
        db.session.commit()
        flash(f"Appointment marked as {new_status}", "success")

    return redirect(url_for('main.doctor_dashboard'))



# ------------------ ADD TREATMENT ------------------
@main.route('/doctor/appointment/<int:appt_id>/treatment', methods=['POST'])
@login_required
def add_treatment(appt_id):
    if current_user.role != ROLE_DOCTOR:
        return redirect(url_for('main.index'))

    appt = Appointment.query.get_or_404(appt_id)
    form = TreatmentForm()

    if form.validate_on_submit():
        treatment = TreatmentRecord(
            patient_id=appt.patient.id,
            doctor_id=appt.doctor.id,
            appointment_id=appt.id,
            diagnosis=form.diagnosis.data,
            prescriptions=form.prescriptions.data,
            notes=form.notes.data
        )
        db.session.add(treatment)
        db.session.commit()
        flash("Treatment record saved successfully.", "success")
    else:
        flash("Diagnosis and Prescriptions are required.", "danger")

    return redirect(url_for('main.doctor_dashboard'))



# ------------------ VIEW PATIENT HISTORY ------------------
@main.route('/doctor/patient/<int:patient_id>/history')
@login_required
def patient_history(patient_id):
    if current_user.role != ROLE_DOCTOR:
        return redirect(url_for('main.index'))

    patient = Patient.query.get_or_404(patient_id)
    treatments = patient.treatments  

    return render_template('dashboards/patient_history.html',
                           patient=patient, treatments=treatments)



# ------------------ PATIENT DASHBOARD ------------------
@main.route('/patient_dashboard', methods=['GET', 'POST'])
@login_required
def patient_dashboard():
    if current_user.role != ROLE_PATIENT:
        return redirect(url_for('main.index'))

    patient = Patient.query.filter_by(user_id=current_user.id).first()

    upcoming = Appointment.query.filter(
        Appointment.patient_id == patient.id,
        Appointment.status == "Booked"
    ).order_by(Appointment.appointment_datetime.asc()).all()

    past = Appointment.query.filter(
        Appointment.patient_id == patient.id,
        Appointment.status.in_(["Cancelled", "Completed", "Rescheduled"])
    ).order_by(Appointment.appointment_datetime.desc()).all()

    action = request.args.get("action")
    appointment_id = request.args.get("id")

    if action and appointment_id:
        appt = Appointment.query.get(int(appointment_id))

        if not appt or appt.patient_id != patient.id:
            flash("Invalid appointment action!", "danger")
            return redirect(url_for('main.patient_dashboard'))

        # CANCEL
        if action == "cancel":
            appt.status = "Cancelled"
            db.session.commit()
            flash("Appointment cancelled successfully!", "success")
            return redirect(url_for('main.patient_dashboard'))

        # RESCHEDULE
        if action == "reschedule":
            if appt.reschedule_count >= 2:
                flash("You cannot reschedule this appointment more than 2 times.", "warning")
                return redirect(url_for('main.patient_dashboard'))
            appt.status = "Rescheduled"
            appt.reschedule_count += 1
            db.session.commit()
            return redirect(url_for('main.book_appointment', reschedule_id=appt.id))

    return render_template(
        "dashboards/patient_dashboard.html",
        upcoming_appts=upcoming,
        past_appts=past
    )


# ------------------ PATIENT BOOKING ------------------
@main.route('/patient/book', methods=['GET', 'POST'])
@login_required
def book_appointment():
    if current_user.role != ROLE_PATIENT:
        return redirect(url_for('main.index'))

    patient = Patient.query.filter_by(user_id=current_user.id).first()

    reschedule_id = request.args.get("reschedule_id")
    reschedule_appt = None
    reschedule_count = 0
    if reschedule_id:
        reschedule_appt = Appointment.query.get(int(reschedule_id))
        if reschedule_appt and reschedule_appt.patient_id == patient.id:
            reschedule_count = reschedule_appt.reschedule_count or 0
        else:
            flash("Invalid reschedule request.", "danger")
            return redirect(url_for('main.patient_dashboard'))

    specializations = [s[0] for s in db.session.query(Doctor.specialization).distinct().all()]

    selected_spec = request.form.get("specialization")
    selected_doctor_id = request.form.get("doctor")
    selected_date = request.form.get("selected_date")

    doctors = []
    free_slots = []

    if selected_spec:
        doctors = Doctor.query.filter_by(specialization=selected_spec).all()

    if selected_doctor_id and selected_date:
        doctor = Doctor.query.get_or_404(int(selected_doctor_id))
        date_obj = datetime.strptime(selected_date, "%Y-%m-%d").date()

        availabilities = DoctorAvailability.query.filter_by(
            doctor_id=doctor.id,
            date=date_obj
        ).all()

        for a in availabilities:
            start_dt = datetime.combine(a.date, a.start_time)
            end_dt = datetime.combine(a.date, a.end_time)
            slot = start_dt
            while slot < end_dt:
                existing_appt = Appointment.query.filter_by(
                    doctor_id=doctor.id, appointment_datetime=slot
                ).first()

                if not existing_appt or (reschedule_appt and existing_appt.id == reschedule_appt.id):
                    free_slots.append(slot)
                slot += timedelta(minutes=30)

        slot_str = request.form.get("slot")
        if slot_str:
            if reschedule_appt and reschedule_count >= 2:
                flash("Maximum 2 reschedules allowed. Cannot reschedule further.", "danger")
                return redirect(url_for('main.patient_dashboard'))

            dt = datetime.strptime(slot_str, "%Y-%m-%d %H:%M")
            conflict = Appointment.query.filter_by(
                doctor_id=doctor.id, appointment_datetime=dt
            ).first()
            
            if conflict and (not reschedule_appt or conflict.id != reschedule_appt.id):
                flash("This time slot is already booked!", "danger")
            else:
                if not reschedule_appt:
                    new_appt = Appointment(
                        patient_id=patient.id,
                        doctor_id=doctor.id,
                        appointment_datetime=dt,
                        status="Booked",
                        reschedule_count=0
                    )
                    db.session.add(new_appt)
                    db.session.commit()
                    flash(f"Appointment booked with Dr. {doctor.name} on {dt.strftime('%Y-%m-%d %H:%M')}", "success")
                else:
                    reschedule_appt.appointment_datetime = dt
                    reschedule_appt.status = "Booked"
                    reschedule_appt.reschedule_count += 1
                    db.session.commit()
                    flash(f"Appointment rescheduled with Dr. {doctor.name} on {dt.strftime('%Y-%m-%d %H:%M')}", "success")

                return redirect(url_for('main.patient_dashboard'))

    return render_template(
        'dashboards/patient_book_slots.html',
        specializations=specializations,
        selected_spec=selected_spec,
        doctors=doctors,
        selected_doctor_id=int(selected_doctor_id) if selected_doctor_id else None,
        selected_date=selected_date,
        free_slots=free_slots,
        reschedule_id=int(reschedule_id) if reschedule_id else None,
        reschedule_count=reschedule_count
    )

# ------------------ VIEW TREATMENT (PATIENT) ------------------
@main.route('/patient/appointment/<int:appointment_id>/treatment')
@login_required
def view_treatment(appointment_id):
    if current_user.role != ROLE_PATIENT:
        return redirect(url_for('main.index'))

    appt = Appointment.query.get_or_404(appointment_id)
    patient = Patient.query.filter_by(user_id=current_user.id).first()

    if not appt or appt.patient_id != patient.id:
        flash("You are not authorized to view this treatment.", "danger")

    if appt.status != "Completed":
        flash("Treatment details are only available for completed appointments.", "warning")
        return redirect(url_for('main.patient_dashboard'))

    treatments = TreatmentRecord.query.filter_by(appointment_id=appointment_id).all()

    return render_template(
        'dashboards/patient_view_treatment.html',
        appointment=appt,
        treatments=treatments
    )













