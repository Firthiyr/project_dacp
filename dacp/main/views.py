from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, DetailView
from django.template.response import TemplateResponse
from django.db.models import Q
from .models import Category, Product, Size, Banner


class IndexView(TemplateView):
    template_name = "main/base.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["banners"] = Banner.objects.filter(is_active=True).order_by("order")
        context["categories"] = Category.objects.all()
        context["new_arrivals"] = Product.objects.all().order_by("-created_at")[:4]
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if request.headers.get("Hx-Request"):
            return TemplateResponse(request, "main/home_content.html", context)
        return TemplateResponse(request, self.template_name, context)


class AboutView(TemplateView):
    template_name = "main/about.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        # Logic for HTMX
        if request.headers.get("Hx-Request"):
            # Якщо запит від HTMX, використовуємо порожню обгортку (тільки контент)
            context["base_template"] = "main/base_htmx.html"
        else:
            # Якщо звичайний захід, використовуємо повну обгортку (з шапкою і футером
            context["base_template"] = "main/base.html"

        return TemplateResponse(request, self.template_name, context)


class ContactView(TemplateView):
    template_name = "main/contact.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        if request.headers.get("Hx-Request"):
            context["base_template"] = "main/base_htmx.html"
        else:
            context["base_template"] = "main/base.html"

        return TemplateResponse(request, self.template_name, context)


class CatalogView(TemplateView):
    template_name = "main/catalog.html"

    FILTER_MAPPING = {
        "color": lambda queryset, value: queryset.filter(color__iexact=value),
        "min_price": lambda queryset, value: queryset.filter(price__gte=value),
        "max_price": lambda queryset, value: queryset.filter(price__lte=value),
        "size": lambda queryset, value: queryset.filter(
            product_sizes__size__name=value
        ),
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_slug = kwargs.get("category_slug")
        categories = Category.objects.all()
        products = Product.objects.all().order_by("-created_at")
        current_category = None

        if category_slug:
            current_category = get_object_or_404(Category, slug=category_slug)
            products = products.filter(category=current_category)

        query = self.request.GET.get("q")
        if query:
            products = products.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            )

        sort_by = self.request.GET.get("sort")
        if sort_by == "price_low":
            products = products.order_by("price")
        elif sort_by == "price_high":
            products = products.order_by("-price")
        elif sort_by == "newest":
            products = products.order_by("-created_at")

        filter_params = {}
        for param, filter_func in self.FILTER_MAPPING.items():
            value = self.request.GET.get(param)
            if value:
                products = filter_func(products, value).distinct()
                filter_params[param] = value
            else:
                filter_params[param] = ""

        filter_params["q"] = query or ""

        context.update(
            {
                "categories": categories,
                "products": products,
                "current_category": current_category,
                "filter_params": filter_params,
                "sizes": Size.objects.all(),
                "search_query": query or "",
            }
        )

        # Для HTMX рендерінгу
        if self.request.GET.get("show_search") == "true":
            context["show_search"] = True
        elif self.request.GET.get("reset_search") == "true":
            context["reset_search"] = True
        if self.request.headers.get("Hx-Request"):
            context["is_htmx"] = True

        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        if request.headers.get("Hx-Request"):
            context["base_template"] = "main/base_htmx.html"
        else:
            context["base_template"] = "main/base.html"

        if request.headers.get("Hx-Request"):
            if context.get("show_search"):
                return TemplateResponse(request, "main/search_input.html", context)
            elif context.get("reset_search"):
                return TemplateResponse(request, "main/search_button.html", {})
            elif request.GET.get("show_filters") == "true":
                return TemplateResponse(request, "main/filter_modal.html", context)

            context["base_template"] = "main/base_htmx.html"
            return TemplateResponse(request, self.template_name, context)

        return TemplateResponse(request, self.template_name, context)


class ProductDetailView(DetailView):
    model = Product
    template_name = "main/product_detail.html"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        context["categories"] = Category.objects.all()
        context["related_products"] = Product.objects.filter(
            category=product.category
        ).exclude(id=product.id)[:4]
        context["current_category"] = product.category
        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(**kwargs)
        if request.headers.get("Hx-Request"):
            context["base_template"] = "main/base_htmx.html"
        else:
            context["base_template"] = "main/base.html"

        return TemplateResponse(request, self.template_name, context)
