from django.db import models


STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('error', 'Error'),
        ('retrying', 'Retrying'),
        ('failed', 'Failed'),
    ]


class Shop(models.Model):
    url = models.CharField(max_length=255,  unique=True, verbose_name='Shopify Store URL')
    cart_url = models.CharField(max_length=512, blank=True, verbose_name='Link to cart')
    error_message = models.TextField(blank=True, verbose_name='Error Message')
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        db_index=True,
        default="pending",
        verbose_name="Status"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.url
