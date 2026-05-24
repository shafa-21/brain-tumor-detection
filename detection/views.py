from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.conf import settings
from django.core.files.storage import default_storage
import os
import numpy as np
import tensorflow as tf
from django.db.models import Count
from django.utils.timezone import now
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from .forms import SignupForm
from .models import DetectionHistory, Appointment
import random
model_path = os.path.join(settings.BASE_DIR, "brain_tumor.h5")
model = tf.keras.models.load_model(model_path)
class_names = ['glioma', 'no_tumor']
glioma_stages = [
    "Grade I (Pilocytic Astrocytoma)",
    "Grade II (Low-Grade Glioma)",
    "Grade III (Anaplastic Glioma)",
    "Grade IV (Glioblastoma)"
]

glioma_drugs = {
    "Grade I (Pilocytic Astrocytoma)": {
        "drugs": "Surgery",
        "note": "Usually curable with surgical removal."
    },

    "Grade II (Low-Grade Glioma)": {
        "drugs": "Temozolomide, Radiation Therapy",
        "note": "Slow-growing but may progress over time."
    },

    "Grade III (Anaplastic Glioma)": {
        "drugs": "Temozolomide, Radiation Therapy, PCV Chemotherapy",
        "note": "Requires aggressive multimodal treatment."
    },

    "Grade IV (Glioblastoma)": {
        "drugs": "Temozolomide, Bevacizumab, Lomustine",
        "note": "Highly aggressive tumor requiring intensive therapy."
    }
}

def index(request):
    return render(request, 'index.html')


@login_required(login_url='login')
def detect(request):
    context = {}

    if request.method == 'POST' and request.FILES.get('image'):

        img_file = request.FILES['image']

        file_name = default_storage.save(img_file.name, img_file)
        file_path = os.path.join(settings.MEDIA_ROOT, file_name)

        img = load_img(file_path, color_mode='grayscale', target_size=(256, 64))
        img_array = img_to_array(img) / 255.0
        img_array = img_array.reshape(256, 64)
        img_array = np.expand_dims(img_array, axis=0)

        prediction = model.predict(img_array)
        predicted_class = class_names[np.argmax(prediction)]
        confidence = float(np.max(prediction))
        confidence_percent = round(confidence * 100, 2)

        if predicted_class == 'glioma':

            stage = random.choice(glioma_stages)
            drug_info = glioma_drugs.get(stage, {})
            drugs = drug_info.get("drugs", "Consult doctor")
            drug_note = drug_info.get("note", "")

        else:
            stage = "No Stage"
            drugs = " "
            drug_note = "Healthy condition – preventive care suggested"

        if isinstance(drugs, str):
            drugs_list = [d.strip() for d in drugs.split(',') if d.strip()]
        else:
            drugs_list = drugs

        if not drugs_list:
            drugs_list = [""]

        severity_map = {
            "Grade I (Pilocytic Astrocytoma)": 25,
            "Grade II (Low-Grade Glioma)": 50,
            "Grade III (Anaplastic Glioma)": 75,
            "Grade IV (Glioblastoma)": 100,
        }

        severity = severity_map.get(stage, 0)

        if severity > 70:
            progress_class = "bg-danger"
        elif severity > 40:
            progress_class = "bg-warning"
        else:
            progress_class = "bg-success"

        border_color = "#ef4444" if severity > 50 else "#2dd4bf"

        DetectionHistory.objects.create(
            user=request.user,
            image=file_name,
            result=predicted_class,
            confidence=confidence_percent,
            stage=stage
        )

        context = {
            'result': "Glioma Tumor" if predicted_class == "glioma" else "No Tumor Detected",
            'confidence': confidence_percent,
            'stage': stage,
            'drugs_list': drugs_list,
            'drug_note': drug_note,
            'image_url': settings.MEDIA_URL + file_name,
            'severity': severity,
            'progress_class': progress_class,
            'border_color': border_color,
        }

    return render(request, 'detection.html', context)
def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
        else:
            print(form.errors) 
    else:
        form = SignupForm()

    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username'] 
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})

    return render(request, 'login.html')   

def logout_view(request):
    logout(request)
    return redirect('login') 
@login_required
def user_dashboard(request):
    data = DetectionHistory.objects.filter(user=request.user)
    return render(request, 'dashboard.html', {'data': data})
def drug_check(request):
    # GET (auto-fill from detection)
    medicine = request.GET.get('drug') or ""  

    result = None
    efficiency = None

    if request.method == 'POST':
        name = request.POST.get('name')
        age = int(request.POST.get('age', 0))
        blood = request.POST.get('blood')
        gender = request.POST.get('gender')
        size = request.POST.get('tumor_size')

        medicine = request.POST.get('drug') or ""

        med_lower = medicine.lower()

        efficiency = 70

        if age < 40:
            efficiency += 10
        else:
            efficiency -= 5

        if size == "Small":
            efficiency += 10
        elif size == "Large":
            efficiency -= 10

        if med_lower.startswith("temozolomide"):
            efficiency += 5

        efficiency = max(30, min(95, efficiency))
        result = f"{efficiency}% Effective"

    return render(request, 'drug_check.html', {
        'medicine': medicine,    # display
        'drug_name': medicine,   # autofill input
        'result': result,
        'efficiency': efficiency
    })
from .models import Appointment
from django.utils.timezone import now
def appointment(request):
    time_slots = ["09:00", "11:30", "14:00", "16:30"]

    if request.method == 'POST':
        Appointment.objects.create(
            user=request.user if request.user.is_authenticated else None,
            name=request.POST.get('name'),
            phone=request.POST.get('phone'),
            condition=request.POST.get('condition'),
            date=request.POST.get('date'),
            time=request.POST.get('time'),
        )

        return render(request, 'appointment.html', {
            'success': True,
            'time_slots': time_slots
        })

    return render(request, 'appointment.html', {
        'time_slots': time_slots
    })

    

@login_required
def doctor_dashboard(request):

    if not request.user.is_staff:
        return redirect('login')

    today = now().date()

    appointments = Appointment.objects.all().order_by('-date', '-time')

    pending_count = appointments.filter(status='Pending').count()
    today_appointments = appointments.filter(date=today).count()

    critical_count = appointments.filter(condition__icontains="Grade 4").count()

    schedule = appointments.filter(date=today).order_by('time')

    return render(request, 'doctor_dashboard.html', {
        'appointments': appointments,
        'pending_count': pending_count,
        'today_appointments': today_appointments,
        'critical_count': critical_count,
        'schedule': schedule,
    })

@login_required
def update_status(request, id, status):

    if not request.user.is_staff:
        return redirect('login')

    appt = get_object_or_404(Appointment, id=id)

    if status in ['Approved', 'Completed']:
        appt.status = status
        appt.save()

    return redirect('doctor_dashboard')
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

def doctor_login(request):
    if request.method == 'POST':
        doctor_id = request.POST.get('doctor_id')
        password = request.POST.get('password')

        user = authenticate(request, username=doctor_id, password=password)

        if user is not None and user.is_superuser:
            login(request, user)
            return redirect('doctor_dashboard')  # change if needed
        else:
            return render(request, 'doctor_login.html', {
                'error': 'Invalid credentials or not authorized'
            })

    return render(request, 'doctor_login.html')
