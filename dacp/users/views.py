from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponse
from django.template.response import TemplateResponse
from .forms import CustomUserCreationForm, CustomUserLoginForm, CustomUserUpdateForm
from .models import CustomUser
from django.contrib import messages
from main.models import Product

# login_required для того, щоб виділити профіль, функції що будуть доступні для зараєстрвоаних


# Create your views here.
def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            return redirect("main:index")
    else:
        form = CustomUserCreationForm()
    return render(request, "users/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = CustomUserLoginForm(request=request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            return redirect("main:index")
        else:
            form = CustomUserLoginForm()
            return render(request, "users/login.html", {"form": form})


# Якщо клієнт не авторозивонаий і зайде на спец юрл, його перенаправить
@login_required(login_url="/users/login")
# Можливість зміни введених даних у профілі
def profile_view(request):
    if request.method == "POST":
        form = CustomUserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            if request.header.get("HX-Request"):
                return HttpResponse(headers={"HX-Redirect": reverse("user:profile")})
            return redirect("users:profile")
    else:
        form = CustomUserUpdateForm(instance=request.user)

    recommended_product = Product.objects.all().order_by("id")[3:]
    return TemplateResponse(
        request,
        "users/profile.html",
        {
            "form": form,
            "user": request.user,
            "recommended_products": recommended_product,
        },
    )


@login_required(login_url="/users/login")
# Для динамісної зміни інормації у профілі
# account_details - попередній огляд (не розгорнутий)
def account_details(request):
    user = CustomUser.objects.get(id=request.user.id)
    return TemplateResponse(
        request, "users/partials/account_details.html", {"user": user}
    )


@login_required(login_url="/users/login")
def edit_account_details(request):
    form = CustomUserUpdateForm(instance=request.user)
    return TemplateResponse(
        request,
        "users/partials/edit_account_details.html",
        {"users": request.user, "form": form},
    )


# Для оновлення розгорнутої інформації в профілі.
@login_required(login_url="/users/login")
def update_account_details(request):
    if request.method == "POST":
        form = CustomUserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            user = form.save(commit=False)
            user.clean()
            user.save()
            updated_user = CustomUser.objects.get(id=user.id)
            request.user = updated_user
            if request.headers.get("HX-Request"):
                return TemplateResponse(
                    request,
                    "users/partials/account_details.html",
                    {"user": updated_user},
                )
            return TemplateResponse(
                request, "users/partials/account_details.html", {"user": updated_user}
            )
        else:
            return TemplateResponse(
                request,
                "users/partials/edit_account_details.html",
                {"user": request.user, "form": form},
            )
    if request.headers.get("HX-Request"):
        return HttpResponse(headers={"HX-Redirect": reverse("user:profile")})
    return redirect("users:profile")


# Визід, також через request щоб було динамічно
def logout_view(request):
    logout(request)
    if request.headers.get("HX-Request"):
        return HttpResponse(headers={"HX-Redirect": reverse("main:index")})
    return redirect("main:index")
