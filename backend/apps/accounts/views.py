import json

from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from django_ratelimit.decorators import ratelimit

from apps.cart.services import merge_guest_cart_into_user
from apps.orders.models import Order, OrderItem

from .forms import AddressForm, OtpVerifyForm, PhoneForm, ProfileForm
from .models import Address, PhoneOTP

User = get_user_model()


def auth_page(request):
    """صفحه‌ی ورود / ثبت‌نام (همان auth.html سابق)."""
    if request.user.is_authenticated:
        return redirect("store:index")
    return render(request, "accounts/auth.html")


@require_POST
# Two independent limits, checked together:
#   - "post:phone": max 3 requests per minute for the SAME phone number,
#     so one number can't be spammed with SMS codes.
#   - "ip": max 10 requests per minute from the SAME IP address, so one
#     visitor can't spam OTP requests for many different phone numbers.
# block=False (instead of block=True) so we can return our own JSON error
# below, matching the JSON-based API style of this view, instead of
# django-ratelimit's default plain-text 403 response.
@ratelimit(key="post:phone", rate="3/m", method="POST", block=False)
@ratelimit(key="ip", rate="10/m", method="POST", block=False)
def request_otp(request):
    """مرحله‌ی اول: دریافت شماره و ارسال کد تایید."""
    if getattr(request, "limited", False):
        return JsonResponse(
            {
                "ok": False,
                "message": "تعداد درخواست‌های شما بیش از حد مجاز است. کمی صبر کنید و دوباره تلاش کنید.",
            },
            status=429,
        )

    form = PhoneForm(request.POST)
    if not form.is_valid():
        return JsonResponse({"ok": False, "errors": form.errors}, status=400)

    phone = form.cleaned_data["phone"]
    otp = PhoneOTP.generate_for(phone)
    # TODO: اتصال به سرویس پیامک واقعی برای ارسال otp.code
    return JsonResponse({"ok": True, "phone": phone, "expires_in": PhoneOTP.EXPIRY_SECONDS})


@require_POST
def verify_otp(request):
    """مرحله‌ی دوم: تایید کد و ورود/ثبت‌نام خودکار کاربر."""
    form = OtpVerifyForm(request.POST)
    if not form.is_valid():
        return JsonResponse({"ok": False, "message": "اطلاعات ارسالی نامعتبر است."}, status=400)

    phone = form.cleaned_data["phone"]
    code = form.cleaned_data["code"]

    otp = (
        PhoneOTP.objects.filter(phone=phone, is_used=False)
        .order_by("-created_at")
        .first()
    )
    if not otp or otp.is_expired():
        return JsonResponse({"ok": False, "message": "کد منقضی شده است. دوباره تلاش کنید."}, status=400)
    if otp.code != code:
        return JsonResponse({"ok": False, "message": "کد تایید نادرست است."}, status=400)

    otp.is_used = True
    otp.save(update_fields=["is_used"])

    user, _created = User.objects.get_or_create(phone=phone, defaults={"username": phone})

    # Must read the session key BEFORE login(): login() rotates it for
    # session-fixation security, so it has to be captured while it still
    # points at whatever guest cart this visitor built up before logging in.
    guest_session_key = request.session.session_key
    login(request, user)
    merge_guest_cart_into_user(guest_session_key, user)

    # "next" is what LoginRequiredMixin (e.g. on checkout) put in the URL
    # when it redirected here — without honoring it, a customer sent to
    # log in from checkout would land back on the homepage instead of
    # picking up where they left off. url_has_allowed_host_and_scheme
    # guards against an open-redirect (never trust a raw "next" value).
    next_url = request.POST.get("next", "")
    if next_url and url_has_allowed_host_and_scheme(
        next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        redirect_url = next_url
    else:
        redirect_url = "/"

    return JsonResponse({"ok": True, "redirect_url": redirect_url})


@login_required
def logout_view(request):
    logout(request)
    return redirect("store:index")


@login_required
def profile_view(request):
    """صفحه‌ی استاندارد پروفایل کاربر - نمایش و ویرایش اطلاعات."""
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "اطلاعات شما با موفقیت ذخیره شد.")
            return redirect("accounts:profile")
    else:
        form = ProfileForm(instance=request.user)

    return render(request, "accounts/profile.html", {"form": form, "active_page": "profile"})


@login_required
def order_list_view(request):
    """صفحه‌ی «سفارش‌های من» - سفارش‌های واقعی کاربر جاری.

    select_related/prefetch_related هر دو اینجا لازم‌اند: هر سفارش خودش
    یک بار کوئری برای آیتم‌هاش می‌خورد (prefetch_related روی items) و هر
    آیتم هم برای عکسش به variant/product نیاز دارد (select_related داخل
    Prefetch) — بدون این‌ها، صفحه‌ای با ۱۰ سفارش دوتایی، ده‌ها کوئری
    اضافه به دیتابیس می‌زد (N+1).
    """
    orders = (
        request.user.orders.prefetch_related(
            Prefetch(
                "items",
                queryset=OrderItem.objects.select_related("variant__product"),
            )
        )
        .order_by("-created_at")
    )
    return render(request, "accounts/orders.html", {"orders": orders, "active_page": "orders"})


@login_required
@require_POST
def mark_order_paid(request, tracking_code):
    """شبیه‌سازی «پرداخت موفق» — دکمه‌ی «کلیک کنید برای پرداخت» در
    order_detail.html به همین view پست می‌کند.

    طبق تصمیم صریح‌ای که قبلاً روی همین پروژه گرفته شد، اتصال واقعی به
    درگاه بانکی یک فاز جداگانه‌ی بعدی نقشه راه است (نه بخشی از این نشست).
    پس این view ادعای پرداخت واقعی ندارد: فقط وضعیت سفارش را از
    "pending_payment" به "paid" تغییر می‌دهد تا کل جریان (دکمه‌ی پرداخت ←
    فعال شدن دکمه‌ی دریافت فاکتور ← تعویض هدر از حالت «مراحل ثبت سفارش»
    به هدر اصلی سایت) قابل نمایش و تست باشد. وقتی درگاه واقعی وصل شود،
    فقط همین یک view باید عوض شود؛ بقیه‌ی سایت (تمپلیت‌ها، لیست سفارش‌ها،
    فاکتور) از روی `order.status`/`order.is_paid` کار می‌کنند و دست‌نخورده
    می‌مانند.

    اگر سفارش از قبل پرداخت شده یا لغو شده باشد (مثلاً کاربر روی دکمه
    دوبار کلیک کرده یا صفحه را رفرش کرده)، کاری انجام نمی‌دهیم — فقط به
    همان صفحه‌ی جزئیات برمی‌گردیم، بدون خطا.
    """
    order = get_object_or_404(Order, tracking_code=tracking_code, user=request.user)
    if order.status == "pending_payment":
        order.status = "paid"
        order.save(update_fields=["status"])
        messages.success(request, "پرداخت با موفقیت انجام شد.")
    return redirect("accounts:order_detail", tracking_code=order.tracking_code)


@login_required
def order_invoice_view(request, tracking_code):
    """صفحه‌ی «دریافت فاکتور» — یک نسخه‌ی قابل‌چاپ از سفارش (چاپ مرورگر →
    ذخیره به‌صورت PDF)، نه یک فایل PDF واقعی تولیدشده در سرور. این انتخاب
    عمدی است: افزودن یک کتابخانه‌ی تولید PDF (مثل WeasyPrint) یک وابستگی
    جدید و سنگین به پروژه اضافه می‌کند که فعلاً برایش نیازی مشخص نشده؛
    قابلیت "چاپ به PDF" مرورگر همان نتیجه (یک فاکتور قابل ذخیره/چاپ) را
    بدون هیچ وابستگی‌ای می‌دهد. اگر بعداً یک فاکتور رسمی/قالب‌بندی‌شده‌ی
    ثابت لازم شد، همین‌جا می‌شود کتابخانه‌ی تولید PDF اضافه کرد.

    دسترسی فقط برای سفارش‌های پرداخت‌شده باز است — دریافت فاکتور برای
    سفارشی که هنوز پرداخت نشده معنی ندارد.
    """
    order = get_object_or_404(
        Order.objects.prefetch_related(
            Prefetch(
                "items",
                queryset=OrderItem.objects.select_related("variant__product"),
            )
        ),
        tracking_code=tracking_code,
        user=request.user,
    )
    if not order.is_paid:
        messages.error(request, "برای دریافت فاکتور، ابتدا باید سفارش را پرداخت کنید.")
        return redirect("accounts:order_detail", tracking_code=order.tracking_code)
    return render(request, "accounts/order_invoice.html", {"order": order})


@login_required
def order_detail_view(request, tracking_code):
    """جزئیات کامل یک سفارش. عمداً با `tracking_code` واقعی پیدا می‌شود، نه
    `pk` — همان دلیل امنیتی/طراحی که خودِ فیلد `tracking_code` را ساختیم:
    یک شناسه‌ی ترتیبی نباید توی URL عمومی باشد. فیلتر `user=request.user`
    هم تضمین می‌کند کاربر فقط بتواند سفارش خودش را ببیند، حتی اگر
    tracking_code یک سفارش دیگر را حدس بزند (که عملاً غیرممکن است) یا
    لینکش را از جایی دیگر پیدا کند.
    """
    order = get_object_or_404(
        Order.objects.prefetch_related(
            Prefetch(
                "items",
                queryset=OrderItem.objects.select_related("variant__product"),
            )
        ),
        tracking_code=tracking_code,
        user=request.user,
    )
    # این صفحه از سایدبار مستقیماً باز نمی‌شود (از کارت سفارش در
    # «سفارش‌های من» باز می‌شود)، ولی همان سایدبار مشترک را دارد — پس
    # منطقی است که همچنان «سفارش‌های من» را در آن فعال نشان دهیم.
    return render(request, "accounts/order_detail.html", {"order": order, "active_page": "orders"})


@login_required
def address_list_view(request):
    """صفحه‌ی «آدرس‌های من» — لیست آدرس‌های ذخیره‌شده‌ی کاربر."""
    addresses = request.user.addresses.all()
    return render(request, "accounts/addresses.html", {"addresses": addresses, "active_page": "addresses"})


@login_required
def address_create_view(request):
    # اولین آدرسی که کاربر ثبت می‌کند، خودکار پیش‌فرض می‌شود — دیگر
    # نیازی نیست کاربری که فقط یک آدرس دارد حتماً چک‌باکس «پیش‌فرض» را
    # هم بزند تا این آدرس واقعاً جایی استفاده شود.
    is_first_address = not request.user.addresses.exists()

    if request.method == "POST":
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            if is_first_address:
                address.is_default = True
            address.save()
            messages.success(request, "آدرس با موفقیت ثبت شد.")
            return redirect("accounts:addresses")
    else:
        form = AddressForm(initial={"is_default": is_first_address})

    return render(
        request,
        "accounts/address_form.html",
        {"form": form, "active_page": "addresses", "is_new": True},
    )


@login_required
def address_edit_view(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)

    if request.method == "POST":
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, "آدرس با موفقیت ویرایش شد.")
            return redirect("accounts:addresses")
    else:
        form = AddressForm(instance=address)

    return render(
        request,
        "accounts/address_form.html",
        {"form": form, "active_page": "addresses", "is_new": False, "address": address},
    )


@login_required
@require_POST
def address_delete_view(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    was_default = address.is_default
    address.delete()

    # اگر آدرس حذف‌شده پیش‌فرض بود و کاربر آدرس دیگری هم دارد، یکی از
    # بقیه را (جدیدترین) خودکار پیش‌فرض می‌کنیم — بدون این کار، کاربر با
    # چند آدرس باقی می‌ماند که هیچ‌کدام پیش‌فرض نیست.
    if was_default:
        next_address = request.user.addresses.order_by("-created_at").first()
        if next_address:
            next_address.is_default = True
            next_address.save(update_fields=["is_default"])

    messages.success(request, "آدرس حذف شد.")
    return redirect("accounts:addresses")


@login_required
@require_POST
def address_set_default_view(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    address.is_default = True
    address.save()  # save() خودش بقیه‌ی آدرس‌های همین کاربر را از پیش‌فرض بودن خارج می‌کند
    messages.success(request, "آدرس پیش‌فرض به‌روزرسانی شد.")
    return redirect("accounts:addresses")