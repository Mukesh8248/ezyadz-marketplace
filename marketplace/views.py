from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Q

from .forms import ServiceForm
from .models import Category, Service, ServiceImage


def home_view(request):
    """
    Display the homepage with categories and recently added services.
    """

    categories = Category.objects.all().order_by("name")

    services = (
        Service.objects
        .filter(
            is_active=True,
            is_available=True,
            provider__provider_profile__is_approved=True,
        )
        .select_related(
            "provider",
            "category",
        )
        .prefetch_related("images")
        .order_by("-created_at")[:6]
    )

    return render(
        request,
        "home.html",
        {
            "categories": categories,
            "services": services,
        },
    )


def service_list_view(request):
    """
    Display all active services with search and category filters.
    """

    services = (
        Service.objects
        .filter(
            is_active=True,
            provider__provider_profile__is_approved=True,
        )
        .select_related(
            "provider",
            "category",
        )
        .prefetch_related("images")
        .order_by("-created_at")
    )

    categories = Category.objects.all().order_by("name")

    search_query = request.GET.get("q", "").strip()
    category_id = request.GET.get("category", "").strip()

    if search_query:
        services = services.filter(
            Q(title__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(category__name__icontains=search_query)
            | Q(provider__username__icontains=search_query)
            | Q(
                provider__provider_profile__business_name__icontains=
                search_query
            )
        )

    if category_id:
        services = services.filter(
            category_id=category_id
        )

    return render(
        request,
        "marketplace/service_list.html",
        {
            "services": services,
            "categories": categories,
            "search_query": search_query,
            "selected_category": category_id,
        },
    )


def service_detail_view(request, pk):
    """
    Display the full details of one active service.
    """

    service = get_object_or_404(
        Service.objects
        .select_related(
            "provider",
            "category",
        )
        .prefetch_related("images"),
        pk=pk,
        is_active=True,
    )

    return render(
        request,
        "marketplace/service_detail.html",
        {
            "service": service,
        },
    )


@login_required
def add_service_view(request):
    """
    Allow an approved provider to add a new service.
    """

    if request.user.user_type != "provider":
        return HttpResponseForbidden(
            "Only service providers can add services."
        )

    provider_profile = getattr(
        request.user,
        "provider_profile",
        None,
    )

    if provider_profile is None:
        messages.error(
            request,
            "Please complete your provider profile first.",
        )
        return redirect("profile")

    if not provider_profile.is_approved:
        messages.warning(
            request,
            "Your provider account must be approved by the "
            "administrator before adding services.",
        )
        return redirect("dashboard")

    if request.method == "POST":
        form = ServiceForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():
            service = form.save(commit=False)
            service.provider = request.user
            service.save()

            uploaded_images = request.FILES.getlist(
                "images"
            )

            for uploaded_image in uploaded_images:
                ServiceImage.objects.create(
                    service=service,
                    image=uploaded_image,
                )

            messages.success(
                request,
                "Service added successfully.",
            )
            return redirect(
                "service_detail",
                pk=service.pk,
            )

    else:
        form = ServiceForm()

    return render(
        request,
        "marketplace/service_form.html",
        {
            "form": form,
            "service": None,
            "page_title": "Add Service",
        },
    )


@login_required
def edit_service_view(request, pk):
    """
    Allow a provider to edit only their own service.
    """

    if request.user.user_type != "provider":
        return HttpResponseForbidden(
            "Only service providers can edit services."
        )

    service = get_object_or_404(
        Service,
        pk=pk,
        provider=request.user,
    )

    if request.method == "POST":
        form = ServiceForm(
            request.POST,
            request.FILES,
            instance=service,
        )

        if form.is_valid():
            service = form.save()

            uploaded_images = request.FILES.getlist(
                "images"
            )

            for uploaded_image in uploaded_images:
                ServiceImage.objects.create(
                    service=service,
                    image=uploaded_image,
                )

            messages.success(
                request,
                "Service updated successfully.",
            )
            return redirect(
                "service_detail",
                pk=service.pk,
            )

    else:
        form = ServiceForm(
            instance=service
        )

    return render(
        request,
        "marketplace/service_form.html",
        {
            "form": form,
            "service": service,
            "page_title": "Edit Service",
        },
    )


@login_required
def delete_service_view(request, pk):
    """
    Allow a provider to delete only their own service.
    """

    if request.user.user_type != "provider":
        return HttpResponseForbidden(
            "Only service providers can delete services."
        )

    service = get_object_or_404(
        Service,
        pk=pk,
        provider=request.user,
    )

    if request.method != "POST":
        return HttpResponseForbidden(
            "Service deletion requires a POST request."
        )

    service_title = service.title
    service.delete()

    messages.success(
        request,
        f'"{service_title}" was deleted successfully.',
    )

    return redirect("dashboard")


@login_required
def toggle_service_availability_view(request, pk):
    """
    Allow a provider to enable or disable their service availability.
    """

    if request.user.user_type != "provider":
        return HttpResponseForbidden(
            "Only service providers can manage availability."
        )

    service = get_object_or_404(
        Service,
        pk=pk,
        provider=request.user,
    )

    if request.method != "POST":
        return HttpResponseForbidden(
            "Availability updates require a POST request."
        )

    service.is_available = not service.is_available
    service.save(
        update_fields=[
            "is_available",
            "updated_at",
        ]
    )

    if service.is_available:
        message = "Service is now available."
    else:
        message = "Service is now unavailable."

    messages.success(
        request,
        message,
    )

    return redirect("dashboard")


@login_required
def delete_service_image_view(request, image_id):
    """
    Allow a provider to delete an image belonging to their service.
    """

    if request.user.user_type != "provider":
        return HttpResponseForbidden(
            "Only service providers can delete service images."
        )

    service_image = get_object_or_404(
        ServiceImage.objects.select_related("service"),
        pk=image_id,
        service__provider=request.user,
    )

    service_id = service_image.service_id

    if request.method != "POST":
        return HttpResponseForbidden(
            "Image deletion requires a POST request."
        )

    service_image.delete()

    messages.success(
        request,
        "Service image deleted successfully.",
    )

    return redirect(
        "edit_service",
        pk=service_id,
    )