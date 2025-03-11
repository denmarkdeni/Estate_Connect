from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from .models import UserInfo, Property, PropertyModification, Dealer, Engineer,FloorPlan
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .serializers import PropertySerializer
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from .floor_plan import generate_floor_plan ,generate_dynamic_floor_plan,generate_realistic_floor_plan
from django.http import JsonResponse

def index(request):
    return render(request,'index.html')

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

@login_required
def admin_dashboard(request):
    person = User.objects.get(id=request.user.id)
    users = UserInfo.objects.exclude(UserRole='admin')  
    users_count = users.count()
    return render(request, 'admin_dashboard.html', {'users': users,'users_count':users_count,'person':person})

def manage_users(request):
    users = UserInfo.objects.exclude(UserRole='admin') 
    return render(request, 'manage_users.html', {'users': users})


# ✅ Approve Users
@login_required
def approve_user(request, user_id):
    user = get_object_or_404(UserInfo, id=user_id)
    user.is_approved = True
    user.save()
    return redirect('manage_users')

# ❌ Remove Users
@login_required
def remove_user(request, user_id):
    user = get_object_or_404(UserInfo, id=user_id)
    user.delete()
    return redirect('manage_users')

# 🔄 Change User Role
@login_required
def change_role(request, user_id, role):
    user = get_object_or_404(UserInfo, id=user_id)
    user.UserRole = role
    user.save()
    return redirect('manage_users')

# 🔒 Logout Function
def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('login')

@login_required
def dealer_dashboard(request):
    properties = Property.objects.filter(dealer=request.user)
    return render(request, 'dealer_dashboard.html', {'properties': properties})

@login_required
def upload_property(request):
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
        
        return redirect('dealer_dashboard')  # Redirect to dashboard after upload

    return render(request, 'upload_property.html')

def customer_dashboard(request):
    query = request.GET.get('q', '')  # Get search query from the request
    properties = Property.objects.filter(status='available')  # Fetch only available properties

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
    return render(request, 'customer_dashboard.html', context)

def property_details(request, property_id):
    property = get_object_or_404(Property, id=property_id)
    return render(request, 'property_details.html', {'property': property})

@login_required
def request_modification(request, property_id):
    property = get_object_or_404(Property, id=property_id)

    if request.method == "POST":
        description = request.POST.get("description")
        modification = PropertyModification.objects.create(
            customer=request.user,
            property=property,
            dealer=property.dealer,
            description=description
        )
        messages.success(request, "Your modification request has been submitted.")
        return redirect('customer_dashboard')

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

@login_required
def update_profile(request):
    user = request.user
    dealer = None
    engineer = None

    # Check if the user is a Dealer
    if hasattr(user, 'dealer'):
        dealer = user.dealer

    # Check if the user is an Engineer
    elif hasattr(user, 'engineer'):
        engineer = user.engineer

    if request.method == "POST":
        phone = request.POST.get("phone")
        address = request.POST.get("address")

        if dealer:
            company_name = request.POST.get("company_name")
            dealer.phone = phone
            dealer.address = address
            dealer.company_name = company_name
            dealer.is_approved = False  # Reset approval on update
            dealer.save()

        elif engineer:
            expertise = request.POST.get("expertise")
            engineer.phone = phone
            engineer.expertise = expertise
            engineer.is_approved = False  # Reset approval on update
            engineer.save()

        messages.success(request, "Profile updated successfully. Awaiting admin approval.")
        return redirect("dashboard")

    return render(request, "update_profile.html", {"dealer": dealer, "engineer": engineer})

@staff_member_required
def verify_users(request):
    dealers = Dealer.objects.filter(is_approved=False)
    engineers = Engineer.objects.filter(is_approved=False)

    if request.method == "POST":
        user_id = request.POST.get("user_id")
        role = request.POST.get("role")
        action = request.POST.get("action")

        if role == "dealer":
            user_profile = Dealer.objects.get(id=user_id)
        else:
            user_profile = Engineer.objects.get(id=user_id)

        if action == "approve":
            user_profile.is_approved = True
        else:
            user_profile.is_approved = False

        user_profile.save()
        messages.success(request, "Verification updated successfully.")
        return redirect("verify_users")

    return render(request, "verify_users.html", {"dealers": dealers, "engineers": engineers})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def property_list(request):
    properties = Property.objects.all()
    serializer = PropertySerializer(properties, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def property_create(request):
    serializer = PropertySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(dealer=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def model_3d(request):
    return render(request, 'model_3d.html')

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
