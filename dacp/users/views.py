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
from orders.models import Order


# Допоміжна функція, щоб не дублювати код
def get_base_template(request):
    if request.headers.get("HX-Request"):
        return "main/base_htmx.html"
    return "main/base.html"


def register(request):
    base_template = get_base_template(request)

    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            return redirect("main:index")
    else:
        form = CustomUserCreationForm()

    return render(
        request, "users/register.html", {"form": form, "base_template": base_template}
    )


def login_view(request):
    base_template = get_base_template(request)

    if request.method == "POST":
        form = CustomUserLoginForm(request=request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            return redirect("main:index")
    else:
        form = CustomUserLoginForm()

    return render(
        request, "users/login.html", {"form": form, "base_template": base_template}
    )


@login_required(login_url="/users/login")
def profile_view(request):
    base_template = get_base_template(request)

    if request.method == "POST":
        form = CustomUserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            # Для HTMX оновлюємо тільки контент або робимо редирект
            if request.headers.get("HX-Request"):
                return HttpResponse(headers={"HX-Redirect": reverse("users:profile")})
            return redirect("users:profile")
    else:
        form = CustomUserUpdateForm(instance=request.user)

    recommended_product = Product.objects.all().order_by("id")[:4]

    return TemplateResponse(
        request,
        "users/profile.html",
        {
            "form": form,
            "user": request.user,
            "recommended_products": recommended_product,
            "base_template": base_template,
        },
    )


@login_required(login_url="/users/login")
def account_details(request):
    # Використовуємо request.user безпосередньо, зайвий запит до БД не обов'язковий
    return TemplateResponse(
        request, "users/partials/account_details.html", {"user": request.user}
    )


@login_required(login_url="/users/login")
def edit_account_details(request):
    form = CustomUserUpdateForm(instance=request.user)
    return TemplateResponse(
        request,
        "users/partials/edit_account_details.html",
        {"user": request.user, "form": form},
    )


@login_required(login_url="/users/login")
def update_account_details(request):
    if request.method == "POST":
        form = CustomUserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            user = form.save(commit=False)
            user.clean()
            user.save()

            # Оновлюємо об'єкт user в request, щоб відобразити актуальні дані відразу (Django може зробити це сам, але для надійності)

            if request.headers.get("HX-Request"):
                return TemplateResponse(
                    request,
                    "users/partials/account_details.html",
                    {"user": user},
                )
            return redirect("users:profile")
        else:
            return TemplateResponse(
                request,
                "users/partials/edit_account_details.html",
                {"user": request.user, "form": form},
            )

    return redirect("users:profile")


def logout_view(request):
    logout(request)
    if request.headers.get("HX-Request"):
        return HttpResponse(headers={"HX-Redirect": reverse("main:index")})
    return redirect("main:index")


@login_required(login_url="/users/login/")
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    return TemplateResponse(
        request, "users/partials/order_history.html", {"orders": orders}
    )


@login_required(login_url="/users/login/")
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return TemplateResponse(
        request, "users/partials/order_detail.html", {"order": order}
    )
