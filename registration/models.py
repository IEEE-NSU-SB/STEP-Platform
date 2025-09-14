from django.db import models

class EventFormStatus(models.Model):
    """Control publish/unpublish of the registration form"""
    is_published = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Published" if self.is_published else "Unpublished"


class Form_Participant(models.Model):
    MEMBERSHIP_CHOICES = [
        ("student", "IEEE Student Member"),
        ("member", "IEEE Member"),
        ("non_ieee", "Non-IEEE Member"),
    ]
    SIZE_CHOICES = [("S","S"),("M","M"),("L","L"),("XL","XL"),("2XL","2XL"),("3XL","3XL")]

    name = models.CharField(max_length=200, null=False, blank=False)
    email = models.EmailField(unique=False, null=False, blank=False)
    contact_number = models.CharField(max_length=20, null=False, blank=False)
    membership_type = models.CharField(max_length=20, choices=MEMBERSHIP_CHOICES)
    ieee_id = models.CharField(max_length=50, blank=True, null=True)
    university = models.CharField(max_length=200, null=False, blank=True, default="")
    department = models.CharField(max_length=200, null=False, blank=False)
    university_id = models.CharField(max_length=50, null=False, blank=False)

    # Store all questionnaire answers in JSON
    answers = models.JSONField(default=dict)

    # Payment
    payment_method = models.CharField(max_length=20, choices=[("Nagad","Nagad"),("Bkash","Bkash")], default="NO method")
    transaction_id = models.CharField(max_length=100, null=False, blank=False)
    tshirt_size = models.CharField(max_length=5, choices=SIZE_CHOICES, null=False, blank=False)
    comments = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.email}"
