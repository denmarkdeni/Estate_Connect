from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from .models import UserInfo
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

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
            return render(request, 'register.html', {'error': 'Username already exists'})
        
        user = User.objects.create_user( email=email, password=password, username=username )
        UserInfo.objects.create( user =user, fullname=fullname, UserRole=role)
        
        return redirect('login')

    return render(request, 'register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect('admin_dashboard')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})

    return render(request, 'login.html')

@login_required
def admin_dashboard(request):
    users = UserInfo.objects.exclude(UserRole='admin')  # Exclude admin itself
    return render(request, 'admin_dashboard.html', {'users': users})

# ✅ Approve Users
@login_required
def approve_user(request, user_id):
    user = get_object_or_404(UserInfo, id=user_id)
    user.is_approved = True
    user.save()
    return redirect('admin_dashboard')

# ❌ Remove Users
@login_required
def remove_user(request, user_id):
    user = get_object_or_404(UserInfo, id=user_id)
    user.delete()
    return redirect('admin_dashboard')

# 🔄 Change User Role
@login_required
def change_role(request, user_id, role):
    user = get_object_or_404(UserInfo, id=user_id)
    user.UserRole = role
    user.save()
    return redirect('admin_dashboard')

# 🔒 Logout Function
def logout_view(request):
    logout(request)
    return redirect('login')