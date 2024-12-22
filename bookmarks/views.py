from functools import wraps
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Bookmark
from restaurants.models import Restaurant
import json
import uuid
from django.db import IntegrityError
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.core import serializers

def bookmark_list(request):
    bookmarks = Bookmark.objects.filter(user=request.user)
    return render(request, 'bookmarks/bookmark_list.html', {'bookmarks': bookmarks})

@login_required
@require_POST
def toggle_bookmark(request):
    try:
        restaurant_id = request.POST.get('restaurant_id')

        print(restaurant_id)
        
        if not restaurant_id and request.body:
            try:
                data = json.loads(request.body)
                restaurant_id = data.get('restaurant_id')
            except json.JSONDecodeError:
                return JsonResponse({
                    'error': 'Invalid JSON data'
                }, status=400)
        
        if not restaurant_id:
            return JsonResponse({
                'error': 'No restaurant ID provided.'
            }, status=400)

        try:
            if not isinstance(restaurant_id, uuid.UUID):
                restaurant_id = uuid.UUID(str(restaurant_id))
        except ValueError:
            return JsonResponse({
                'error': 'Invalid restaurant ID format'
            }, status=400)

        try:
            restaurant = Restaurant.objects.get(id=restaurant_id)
        except Restaurant.DoesNotExist:
            return JsonResponse({
                'error': 'Restaurant not found'
            }, status=404)

        try:
            bookmark = Bookmark.objects.get(
                user=request.user,
                restaurant=restaurant
            )
            bookmark.delete()
            is_bookmarked = False
            message = 'Bookmark removed successfully'
        except Bookmark.DoesNotExist:
            try:
                bookmark = Bookmark.objects.create(
                    id=uuid.uuid4(),
                    user=request.user,
                    restaurant=restaurant
                )
                is_bookmarked = True
                message = 'Restaurant bookmarked successfully'
            except IntegrityError:
                return JsonResponse({
                    'error': 'Bookmark already exists'
                }, status=400)

        return JsonResponse({
            'success': True,
            'is_bookmarked': is_bookmarked,
            'message': message,
            'bookmark_id': str(bookmark.id) if is_bookmarked else None
        })

    except Exception as e:
        print(f"Error in toggle_bookmark: {str(e)}")
        return JsonResponse({
            'error': str(e)
        }, status=500)
    
@login_required
@csrf_exempt
def toggle_bookmark_flutter(request, restaurant_id):
    try:
        # Ensure that the restaurant ID is in a valid UUID format
        try:
            # restaurant_id = uuid.UUID(str(restaurant_id))
            restaurant_id = str(restaurant_id)
        except ValueError:
            return JsonResponse({
                'error': 'Invalid restaurant ID format'
            }, status=400)

        try:
            restaurant = Restaurant.objects.get(id=restaurant_id)
        except Restaurant.DoesNotExist:
            return JsonResponse({
                'error': 'Restaurant not found'
            }, status=404)

        try:
            bookmark = Bookmark.objects.get(user=request.user, restaurant=restaurant)
            bookmark.delete()
            is_bookmarked = False
            message = 'Bookmark removed successfully'
        except Bookmark.DoesNotExist:
            try:
                bookmark = Bookmark.objects.create(
                    id=restaurant.id,
                    user=request.user,
                    restaurant=restaurant
                )
                is_bookmarked = True
                message = 'Restaurant bookmarked successfully'
            except IntegrityError:
                return JsonResponse({
                    'error': 'Bookmark already exists'
                }, status=400)

        return JsonResponse({
            'success': True,
            'is_bookmarked': is_bookmarked,
            'message': message,
            'bookmark_id': str(bookmark.id) if is_bookmarked else None
        })

    except Exception as e:
        print(f"Error in toggle_bookmark_flutter: {str(e)}")
        return JsonResponse({
            'error': str(e)
        }, status=500)
    

def flutter_login_required(view_func):
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False,
                'message': 'Authentication required',
                'login_url': '/auth/flutter-login/'
            }, status=401)
        return view_func(request, *args, **kwargs)
    return wrapped_view

@flutter_login_required
@csrf_exempt
def get_bookmarks_flutter(request):
    try:
        data = []
        user = request.user
        bookmarks = Bookmark.objects.filter(user=user).select_related('restaurant')
        restaurants = Restaurant.objects.all()
        
        if not bookmarks:
            return JsonResponse({"success": False, "message": "No bookmarks found."}, status=404)
        
        for bookmark in bookmarks:
            datcon = {
                "id": bookmark.restaurant.id,
                "name": bookmark.restaurant.name,
                "location": bookmark.restaurant.get_location(),
                "description": bookmark.restaurant.description,
                "is_bookmarked": True,
            }

            data.append(datcon)

        return JsonResponse({"success": True, "bookmarks": data}, status=200)

    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)

def show_json(request):
    data = Bookmark.objects.filter(user=request.user)
    return HttpResponse(serializers.serialize("json", data), content_type="application/json")

def show_json_by_id(request, id):
    data = Bookmark.objects.filter(pk=id)
    return HttpResponse(serializers.serialize("json", data), content_type="application/json")