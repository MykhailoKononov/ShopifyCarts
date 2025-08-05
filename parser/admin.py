import re

from django.contrib import admin, messages
from django.http import HttpRequest, HttpResponseRedirect, HttpResponse
from django.urls import path, reverse
from django.shortcuts import render
from django.utils.html import format_html

from .forms import UploadFileForm
from .models import Shop
from .tasks import parse_and_save, retry_failed_shops
from .views import celery_task_status


class ShopAdmin(admin.ModelAdmin):
    change_list_template = "admin/parser/shop/change_list.html"
    list_display = ("url", "cart_link", "status", "error_message", "updated_at")

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [
            path('upload-file/', self.upload_file),
            path("retry-failed/", self.admin_site.admin_view(self.retry_failed_view), name="parser_shop_retry_failed"),
            path('task-status/', self.admin_site.admin_view(celery_task_status), name="parser_shop_task_status"),
            path('generate-file/', self.admin_site.admin_view(self.generate_file), name='parser_shop_generate_file'),
        ]
        return new_urls + urls

    def upload_file(self, request: HttpRequest):
        if request.method == "POST":
            form = UploadFileForm(request.POST, request.FILES)
            if form.is_valid():
                raw_lines = form.cleaned_data['file'].read().decode('utf-8').splitlines()

                cleaned_lines = []
                for line in raw_lines:
                    no_ctrl = re.sub(r'[\r\n\t]+', '', line)
                    printable = re.sub(r'[^\x20-\x7E]', '', no_ctrl)
                    stripped = printable.strip()
                    if stripped:
                        cleaned_lines.append(stripped)

                result = parse_and_save.apply_async(args=[cleaned_lines])
                changelist_url = reverse("admin:parser_shop_changelist")
                redirect_url = f"{changelist_url}?task_id={result.id}"
                messages.info(request, "Please wait, we are generating carts…")

                return HttpResponseRedirect(redirect_url)
        else:
            form = UploadFileForm()

        return render(request, 'admin/upload_file.html', {'form': form})

    def generate_file(self, request):
        shops = Shop.objects.all()
        lines = ["URL | Cart Url | Status | Error Message"]

        for shop in shops:
            line = f"{shop.url} | {shop.cart_url or '-'} | {shop.status} | {shop.error_message or '-'}"
            lines.append(line)

        content = "\n".join(lines)
        filename = "shops_list.txt"

        response = HttpResponse(content, content_type="text/plain; charset=utf-8")
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    def retry_failed_view(self, request):
        failed_qs = Shop.objects.filter(status="error")
        urls = list(failed_qs.values_list("url", flat=True))
        if not urls:
            self.message_user(request, "No stores with 'error' status. Nothing to retry.", level=messages.WARNING)
            return HttpResponseRedirect(reverse("admin:parser_shop_changelist"))

        result = retry_failed_shops.apply_async(args=[urls])
        changelist_url = reverse("admin:parser_shop_changelist")
        redirect_url = f"{changelist_url}?task_id={result.id}"
        messages.info(request, "Please wait, we are generating carts…")

        return HttpResponseRedirect(redirect_url)

    def cart_link(self, obj: Shop):
        if not obj.cart_url:
            return "-"
        max_len = 40
        text = (
            obj.cart_url if len(obj.cart_url) <= max_len
            else f"{obj.cart_url[:max_len]}…"
        )
        return format_html(
            '<a href="{0}" target="_blank" rel="noopener">{1}</a>',
            obj.cart_url,
            text
        )

    cart_link.short_description = "Cart URL"
    cart_link.admin_order_field = "cart_url"

    def changelist_view(self, request, extra_context=None):
        # 1) Pull out task_id (if present) so we can give it to the template
        task_id = request.GET.get("task_id")
        if extra_context is None:
            extra_context = {}
        extra_context["task_id"] = task_id

        # 2) Remove it from GET so Django Admin’s “clean URL” logic won’t redirect away
        if "task_id" in request.GET:
            mutable = request.GET._mutable
            request.GET._mutable = True
            del request.GET["task_id"]
            request.GET._mutable = mutable

        # 3) Call the real changelist_view with our extra_context
        return super().changelist_view(request, extra_context=extra_context)


admin.site.register(Shop, ShopAdmin)
