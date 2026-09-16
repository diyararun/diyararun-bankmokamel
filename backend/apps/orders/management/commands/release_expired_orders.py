from django.core.management.base import BaseCommand

from apps.orders.models import Order


class Command(BaseCommand):
    """نشست ۴۳: نیمه‌ی «سختِ» مکانیزمِ رزروِ موجودی.

    هر سفارشِ «در انتظار پرداخت» که مهلتش (CheckoutSettings.
    reservation_minutes) تمام شده باشد را «لغوشده» می‌کند و موجودیِ
    کالاهایش را برمی‌گرداند — دقیقاً همان کاری که چند view در سایت هم
    به‌صورتِ تنبل (هر بار که کسی به آن‌ها سر بزند) انجام می‌دهند
    (Order.release_expired_pending_orders، تعریف در apps/orders/models.py).

    تفاوت این‌جا این است: این دستور باید طبقِ یک زمان‌بندیِ ثابت (مثلاً
    هر ۱-۲ دقیقه) از crontab سرور اجرا شود — نه فقط وقتی کسی سایت را باز
    می‌کند. چون این پروژه Celery/کرونِ داخلیِ جنگو ندارد، تنها راهِ
    تضمینِ آزادشدنِ به‌موقعِ رزروها (حتی در ساعاتی که هیچ بازدیدکننده‌ای
    نیست) همین است: یک خطِ ساده در crontab خودِ سرور، نه یک وابستگیِ
    جدید به پروژه.

    نمونه‌ی خط crontab (هر ۲ دقیقه یک‌بار):
        */2 * * * * cd /path/to/project/backend && /path/to/venv/bin/python manage.py release_expired_orders
    """

    help = (
        "سفارش‌های «در انتظار پرداخت» که مهلتِ رزروشان تمام شده را لغو "
        "می‌کند و موجودیِ کالاهایشان را به فروشگاه برمی‌گرداند. برای "
        "اجرای دوره‌ای از crontab سرور در نظر گرفته شده — safe به اجرای "
        "مکرر (هر بار فقط سفارش‌های واقعاً منقضی‌شده را پردازش می‌کند)."
    )

    def handle(self, *args, **options):
        released_count = Order.release_expired_pending_orders()
        if released_count == 0:
            self.stdout.write("هیچ سفارشِ منقضی‌شده‌ای برای آزادکردن نبود.")
            return
        self.stdout.write(
            self.style.SUCCESS(f"{released_count} سفارش لغو شد و موجودیِ کالاهایشان برگشت.")
        )
