from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from .models import UserInfo, Property, PropertyModification, Dealer, Engineer, Customer, FloorPlan
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from .floor_plan import generate_dynamic_floor_plan,generate_realistic_floor_plan
from .plot_plan import generate_floor_plan, plot_floor_plan
from django.http import JsonResponse
import plotly.graph_objects as go
import json

def index(request):
    return render(request, 'index.html')

def search_engineers(request):
    try:
        data = json.loads(request.body)
        location = data.get('location', '').strip().lower()
        engineers = Engineer.objects.filter(location__icontains=location, is_approved=True)
        
        engineer_list = []
        for eng in engineers:
            engineer_list.append({
                "user": {
                    "username": eng.user.username,
                    "email": eng.user.email,
                },
                "specialization": eng.expertise if hasattr(eng, 'expertise') else "General",
                "place": eng.location,
            })

        return JsonResponse({"engineers": engineer_list}, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        fullname = request.POST['fullname']
        email = request.POST['email']
        password = request.POST['password']
        role = request.POST['UserRole']

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('register')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return redirect('register')
        
        user = User.objects.create_user( email=email, password=password, username=username )
        UserInfo.objects.create( user =user, fullname=fullname, UserRole=role)
        messages.success(request, 'Your account has been created successfully!')
        return redirect('login')

    return render(request, 'register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, 'Signed In successfully!')
            if user.is_superuser:
                return redirect('admin_dashboard')
            if user.userinfo.UserRole == "dealer":
                return redirect('dealer_dashboard')
            if user.userinfo.UserRole == "customer":
                return redirect('customer_dashboard')
            if user.userinfo.UserRole == "engineer":
                return redirect('engineer_dashboard')
        else:
            messages.error(request, 'Invalid username or password')
            return redirect('login')

    return render(request, 'login.html')

# 🔒 Logout Function
def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('login')

@login_required
def admin_dashboard(request):
    person = User.objects.get(id=request.user.id)
    engineers_count = UserInfo.objects.filter(UserRole='engineer').count()
    dealers_count = UserInfo.objects.filter(UserRole='dealer').count()
    customers_count = UserInfo.objects.filter(UserRole='customer').count()
    properties_count = Property.objects.all().count()
    return render(request, 'admin_dashboard.html', {'engineers_count':engineers_count,'dealers_count':dealers_count,'customers_count':customers_count,'person':person,'properties_count':properties_count})

def admin_engineers(request):
    approved_engineers = Engineer.objects.filter(is_approved=True)
    pending_engineers = Engineer.objects.filter(is_approved=False)
    return render(request, 'admin_engineers.html', {'approved_engineers': approved_engineers, 'pending_engineers': pending_engineers})

def admin_dealers(request):
    approved_dealers = Dealer.objects.filter(is_approved=True)
    pending_dealers = Dealer.objects.filter(is_approved=False)
    return render(request, 'admin_dealers.html', {'approved_dealers': approved_dealers, 'pending_dealers': pending_dealers})

def admin_customers(request):
    customers = Customer.objects.all()
    return render(request, 'admin_customers.html', {'customers': customers})

def admin_properties(request):
    properties = Property.objects.all()
    return render(request, 'admin_properties.html', {'properties': properties})

def user_profile(request):
    user = request.user  # Get logged-in user
    
    if user.userinfo.UserRole == "dealer":
        dealer, created = Dealer.objects.get_or_create(user=user)
        if request.method == "POST":
            dealer.company_name = request.POST.get("company_name", dealer.company_name)
            dealer.phone = request.POST.get("phone", dealer.phone)
            dealer.address = request.POST.get("address", dealer.address)
            dealer.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("user_profile") 

    elif user.userinfo.UserRole == "customer":
        customer, created = Customer.objects.get_or_create(user=user)
        if request.method == "POST":
            customer.phone = request.POST.get("phone", customer.phone)
            customer.address = request.POST.get("address", customer.address)
            customer.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("user_profile")

    elif user.userinfo.UserRole == "engineer":
        engineer, created = Engineer.objects.get_or_create(user=user)
        if request.method == "POST":
            engineer.expertise = request.POST.get("expertise", engineer.expertise)
            engineer.phone = request.POST.get("phone", engineer.phone)
            engineer.location = request.POST.get("location", engineer.location).strip().lower()
            engineer.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("user_profile")
        
    return render(request, 'user_profile.html')

def approve_engineer(request, user_id):
    engineer = get_object_or_404(Engineer, user_id=user_id)
    engineer.is_approved = True  
    engineer.save()
    messages.success(request, f"{engineer.user.userinfo.fullname} has been approved! ✔")
    return redirect("admin_engineers")

def remove_engineer(request, user_id):
    engineer = get_object_or_404(Engineer, user_id=user_id)
    user = User.objects.get(engineer=engineer)
    name =user.userinfo.fullname
    user.delete()
    messages.success(request, f"{name} has been removed! ❌")
    return redirect("admin_engineers")

def approve_dealer(request, user_id):
    dealer = get_object_or_404(Dealer, user_id=user_id)
    dealer.is_approved = True  
    dealer.save()
    messages.success(request, f"{dealer.user.userinfo.fullname} has been approved!")
    return redirect("admin_dealers")

def remove_dealer(request, user_id):
    dealer = get_object_or_404(Dealer, user_id=user_id)
    user = User.objects.get(dealer=dealer)
    name =user.userinfo.fullname
    user.delete()
    messages.success(request, f"{name} has been removed! ❌")
    return redirect("admin_dealers")

def remove_customer(request, user_id):
    customer = get_object_or_404(Customer, user_id=user_id)
    user = User.objects.get(customer=customer)
    name =user.userinfo.fullname
    user.delete()
    messages.success(request, f"{name} has been removed! ❌")
    return redirect("admin_customers")

def approve_property(request, property_id):
    property = Property.objects.get(id=property_id)
    property.status = "approved"
    property.save()
    messages.success(request, "Property Approved!")
    return redirect("admin_properties")

def remove_property(request, property_id):
    property = Property.objects.get(id=property_id)
    property.delete()
    messages.success(request, "Property Removed!")
    return redirect("admin_properties")

def customer_dashboard(request):
    return render(request, 'customer_dashboard.html')

def engineers_list(request):
    engineers = Engineer.objects.filter(is_approved=True)
    return render(request, 'engineers_list.html',{'engineers' : engineers})

def property_list(request):
    query = request.GET.get('q', '')  
    properties = Property.objects.filter(status='approved')

    if query:
        properties = properties.filter(
            title__icontains=query
        ) | properties.filter(
            location__icontains=query
        ) | properties.filter(
            price__icontains=query
        )

    context = {
        'properties': properties,
        'query': query,
    }
    return render(request, "property_list.html", context)

def property_details(request, property_id):
    property = get_object_or_404(Property, id=property_id)
    return render(request, 'property_details.html', {'property': property})

@login_required 
def dealer_dashboard(request):
    properties = Property.objects.filter(dealer=request.user)
    return render(request, 'dealer_dashboard.html', {'properties': properties})

def dealer_upload_property(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        price = request.POST.get('price')
        location = request.POST.get('location')
        image = request.FILES.get('image')

        property_obj = Property(
            dealer=request.user,
            title=title,
            description=description,
            price=price,
            location=location,
            image=image
        )
        property_obj.save()
        messages.success(request, 'Property uploaded successfully!')
        
        return redirect('dealer_dashboard')
    return render(request, 'dealer_upload_property.html')  


@login_required
def request_modification(request, property_id):
    property = get_object_or_404(Property, id=property_id)

    if request.method == "POST":
        description = request.POST.get("description")
        PropertyModification.objects.create(
            customer=request.user,
            property=property,
            dealer=property.dealer,
            description=description
        )
        messages.success(request, "Your modification request has been submitted.")
        return redirect(f'/property/{property_id}/')

    return render(request, "request_modification.html", {"property": property})

@login_required
def dealer_manage_requests(request):
    requests = PropertyModification.objects.filter(dealer=request.user)

    if request.method == "POST":
        request_id = request.POST.get("request_id")
        engineer_id = request.POST.get("engineer_id")
        status = request.POST.get("status")

        mod_request = get_object_or_404(PropertyModification, id=request_id)

        if engineer_id:
            mod_request.engineer_id = engineer_id
            mod_request.status = "in_progress"
        elif status:
            mod_request.status = status
        
        mod_request.save()
        messages.success(request, "Modification request updated successfully.")
        return redirect("dealer_manage_requests")

    engineers = User.objects.filter(userinfo__UserRole="engineer")
    return render(request, "dealer_manage_requests.html", {"requests": requests, "engineers": engineers})

@login_required
def engineer_dashboard(request):
    requests = PropertyModification.objects.filter(engineer=request.user)

    if request.method == "POST":
        request_id = request.POST.get("request_id")
        status = request.POST.get("status")

        mod_request = get_object_or_404(PropertyModification, id=request_id)
        mod_request.status = status
        mod_request.save()
        messages.success(request, "Status updated successfully.")
        return redirect("engineer_dashboard")

    return render(request, "engineer_dashboard.html", {"requests": requests})

def upload_3d_model(request):
    if request.method == 'POST':
        property_id = request.POST.get('property_id')
        model_3d = request.FILES.get('glb_model')

        property = Property.objects.get(id=property_id)
        property.model_3d = model_3d
        property.save()
        
        messages.success(request, '3D model uploaded successfully!')
        return redirect('upload_3d_model')
    properties = Property.objects.filter(status='available')
    return render(request, 'upload_3d_model.html', {'properties': properties})

def model_3d(request, property_id):
    property = get_object_or_404(Property, id=property_id)
    return render(request, 'model_3d.html', {'property': property}) 

import razorpay
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse

def create_order(request, property_id):
    property_obj = Property.objects.get(id=property_id) 
    amount = int(property_obj.price * 100) 
    amount = 1000

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    payment_data = {
        "amount": amount,
        "currency": "INR",
        "payment_capture": 1
    }
    order = client.order.create(data=payment_data)

    context = {
        "amount": amount,
        "order_id": order["id"],
        "property": property_obj,
        "RAZORPAY_KEY_ID": settings.RAZORPAY_KEY_ID
    }
    return render(request, "payment_page.html", context)

def payment_success(request):
    property_id = request.GET.get("property_id")
    property =  Property.objects.get(id=property_id)
    property.status = 'pending'
    property.registered_to = request.user
    property.save()
    messages.success(request, "Registered Successfully!")
    
    payment_id = request.GET.get("payment_id")
    return render(request, "payment_success.html", {"payment_id": payment_id,"property": property})

def generate_plan(request):
    return render(request, 'floor_plan.html')

def blueprint(request):
    return render(request, 'blueprint_form.html')

def floor_plan_view(request):
    """Render SVG floor plan based on user input."""
#     rooms = int(request.GET.get("rooms", 2))
#     room_width = int(request.GET.get("room_width", 100))
#     room_height = int(request.GET.get("room_height", 100))
# rooms, room_width, room_height

    svg = generate_realistic_floor_plan()

    # Save to Database
    plan = FloorPlan.objects.create(name="Generated Plan", svg_data=svg)
    plan.save()

    return HttpResponse(svg, content_type="image/svg+xml")

def api_floorplan(request, plan_id):
    try:
        floor_plan = FloorPlan.objects.get(id=plan_id)
        return JsonResponse({"svg": floor_plan.svg_data})
    except FloorPlan.DoesNotExist:
        return JsonResponse({"error": "Plan not found"}, status=404)
    
def print_2d(request):
    return render(request, '2d_print.html')
    
def fabric_2d(request):
    return render(request, 'fabric_2d.html')

def plot_2d(request):
    if request.method == "POST":
        room_counts = {
            "Entry": 1,
            "Living Room": int(request.POST.get("living_room", 0)),
            "Dining Room": int(request.POST.get("dining_room", 0)),
            "Kitchen": int(request.POST.get("kitchen", 0)),
            "Bedroom": int(request.POST.get("bedroom", 0)),
            "Bathroom": int(request.POST.get("bathroom", 0)),
        }

        floor_plan, max_x, max_y = generate_floor_plan(room_counts)
        plot_floor_plan(floor_plan, max_x, max_y)

        return HttpResponse("Floor Plan Generated Successfully!")
    
    return render(request, "plot_2d.html")

def plot_3d(request):
    floor_plan = [
        [0, 1, 1, 0],  
        [1, 2, 2, 1],  
        [1, 2, 2, 1],  
        [0, 1, 1, 0]
    ]
    
    fig = go.Figure(data=[go.Surface(z=floor_plan)])
    plot_div = fig.to_html(full_html=False)
    
    return render(request, "plot_3d.html", {"plot_div": plot_div})

from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from django.conf import settings
import os

model_path = os.path.join(settings.BASE_DIR, "construction-estimator\\")

tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForSeq2SeqLM.from_pretrained(model_path)

def input_page(request):
    prediction = None

    if request.method == "POST":
        land_size = request.POST.get("land_size")
        location = request.POST.get("location")
        building_type = request.POST.get("building_type")
        floors = request.POST.get("floors")

        input_text = f"Land: {land_size} sqft, Location: {location}, Type: {building_type}, Floors: {floors}"
        inputs = tokenizer(input_text, return_tensors="pt", truncation=True)
        output = model.generate(**inputs, max_new_tokens=100)
        prediction = tokenizer.decode(output[0], skip_special_tokens=True)
        prediction = prediction.replace("?", "₹")
    
        return render(request, "estimator_app/input_page.html", {"prediction": prediction, "land_size": land_size, "location": location, "building_type": building_type, "floors": floors})
    return render(request, "estimator_app/input_page.html", {"prediction": prediction})