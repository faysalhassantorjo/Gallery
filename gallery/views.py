from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import check_password
from django.views.decorators.http import require_POST
from .models import Photo, GallerySettings
from .auth import gallery_authenticated


def enter_view(request):
    if request.session.get('gallery_authenticated'):
        return redirect('gallery')

    error = None
    if request.method == 'POST':
        password = request.POST.get('password', '')
        settings_obj = GallerySettings.objects.first()

        if settings_obj:
            is_valid = False
            # Check hashed password (set via management command)
            if check_password(password, settings_obj.password_hash):
                is_valid = True
            # Fallback: plain-text match (set via admin panel)
            elif password == settings_obj.password_hash:
                is_valid = True

            if is_valid:
                request.session['gallery_authenticated'] = True
                return redirect('gallery')
            else:
                error = "Incorrect password."

    return render(request, 'gallery/enter.html', {'error': error})


@require_POST
def lock_view(request):
    if 'gallery_authenticated' in request.session:
        del request.session['gallery_authenticated']
    return redirect('enter')


@gallery_authenticated
def gallery_list_view(request):
    photos = Photo.objects.all()
    return render(request, 'gallery/gallery.html', {'photos': photos})


@gallery_authenticated
@require_POST
def photo_delete_view(request, photo_id):
    photo = get_object_or_404(Photo, id=photo_id)
    # Cloudinary deletion is handled by django-cloudinary-storage automatically
    photo.delete()
    return redirect('gallery')


