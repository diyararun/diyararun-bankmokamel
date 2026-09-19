#!/bin/sh
# این اسکریپت در زمان *start شدن کانتینر* اجرا می‌شود (نه در زمان build
# ایمیج) — دقیقاً همان چیزی که TODO فاز ۰ در Dockerfile منتظرش بود.
#
# چرا اینجا و نه داخل RUN در Dockerfile: در زمان "docker build"، هیچ‌کدام
# از متغیرهای SECRET_KEY / ALLOWED_HOSTS / POSTGRES_* روی سیستم وجود
# ندارند (اینها فقط در زمان "docker compose up" و از طریق "env_file: .env"
# به کانتینر تزریق می‌شوند)، و base.py/prod.py هم دقیقاً با همین فرض
# نوشته شده‌اند (env("SECRET_KEY") بدون default، چک ALLOWED_HOSTS در
# prod.py). یعنی collectstatic نه به‌خاطر باگی در settings.py، بلکه به
# این دلیل ساختاری در build fail می‌کرد که اصلاً زمان درستی برای اجرای
# آن نبود. راه‌حل، جابه‌جا کردن آن به اینجاست، نه دستکاری settings.py.
set -e

echo "[entrypoint] در حال اجرای collectstatic..."
python manage.py collectstatic --noinput

# اختیاری ولی توصیه‌شده: اجرای خودکار migration در هر استارت. اگر ترجیح
# می‌دهی migration را دستی و آگاهانه (مثلاً قبل از هر ریلیز) بزنی، همین دو
# خط را حذف کن — چیزی که این اسکریپت را می‌شکند نیست.
echo "[entrypoint] در حال اجرای migrate..."
python manage.py migrate --noinput

# "exec" مهم است: یعنی گانیکورن جای همین شل (PID 1) می‌نشیند، پس
# سیگنال‌های docker stop/restart درست به آن می‌رسند (نه به یک شل واسط).
exec "$@"