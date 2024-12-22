from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from main.models import UserProfile
import json


@csrf_exempt
def register(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            email = data.get('email')
            full_name = data.get('full_name')
            interested_in = data.get('interested_in')

            if User.objects.filter(username=username).exists():
                return JsonResponse({
                    "status": False,
                    "message": "Username sudah digunakan."
                }, status=400)
            
            user = User.objects.create_user(
                username=username,
                password=password,
                email=email
            )

            user_profile = UserProfile.objects.create(
                user=user,
                full_name=full_name,
                email=email,
                interested_in=interested_in
            )

            return JsonResponse({
                "status": True,
                "message": "Registrasi berhasil!",
                "user": {
                    "username": user.username,
                    "email": user.email,
                    "full_name": user_profile.full_name,
                    "interested_in": user_profile.interested_in
                }
            }, status=201)

        except Exception as e:
            return JsonResponse({
                "status": False,
                "message": f"Terjadi kesalahan: {str(e)}"
            }, status=400)

@csrf_exempt
def login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')

            user = authenticate(username=username, password=password)
            
            if user is not None:
                if user.is_active:
                    auth_login(request, user)
                    
                    user_profile = UserProfile.objects.get(user=user)
                    
                    return JsonResponse({
                        "status": True,
                        "message": "Login berhasil!",
                        "user": {
                            "username": user.username,
                            "email": user.email,
                            "full_name": user_profile.full_name,
                            "interested_in": user_profile.interested_in
                        }
                    }, status=200)
                else:
                    return JsonResponse({
                        "status": False,
                        "message": "Akun dinonaktifkan."
                    }, status=401)
            else:
                return JsonResponse({
                    "status": False,
                    "message": "Username atau password salah."
                }, status=401)

        except Exception as e:
            return JsonResponse({
                "status": False,
                "message": f"Terjadi kesalahan: {str(e)}"
            }, status=400)

    return JsonResponse({
        "status": False,
        "message": "Method not allowed."
    }, status=405)

@csrf_exempt
def check_auth_status(request):
    if request.user.is_authenticated:
        user_profile = UserProfile.objects.get(user=request.user)
        return JsonResponse({
            "status": True,
            "user": {
                "username": request.user.username,
                "email": request.user.email,
                "full_name": user_profile.full_name,
                "interested_in": user_profile.interested_in
            }
        })
    return JsonResponse({
        "status": False,
        "message": "User tidak terautentikasi"
    })

@csrf_exempt
def logout(request):
    try:
        if request.method == 'POST':
            auth_logout(request)
            response = JsonResponse({
                "status": True,
                "message": "Logout berhasil!"
            }, status=200)
            response.delete_cookie('sessionid')
            response.delete_cookie('csrftoken')
            return response

        return JsonResponse({
            "status": False,
            "message": "Method not allowed."
        }, status=405)
    except Exception as e:
        return JsonResponse({
            "status": False,
            "message": f"Logout error: {str(e)}"
        }, status=500)