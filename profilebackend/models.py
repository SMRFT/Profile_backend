from django.db import models
from django.utils.timezone import now
from djongo import models

class Profile(models.Model):
    employeeId = models.CharField(max_length=100, unique=True,primary_key=True)
    employeeName = models.CharField(max_length=255)
    fatherName = models.CharField(max_length=255, null=True, blank=True)
    motherName = models.CharField(max_length=255, null=True, blank=True)
    gender = models.CharField(max_length=10)
    mobileNumber = models.CharField(max_length=15)
    bloodGroup = models.CharField(max_length=5, null=True, blank=True)
    maritalStatus = models.CharField(max_length=20, null=True, blank=True)
    guardianNumber = models.CharField(max_length=15, null=True, blank=True)
    dateOfBirth = models.DateField(null=True, blank=True)
    email = models.EmailField()

    department = models.CharField(max_length=100, null=True, blank=True)
    designation = models.CharField(max_length=100, null=True, blank=True)
    primaryRole = models.CharField(max_length=100)
    additionalRoles = models.JSONField(default=list)
    dataEntitlements = models.JSONField(default=list)

    employmentStatus = models.CharField(max_length=20)
    registrationNumber = models.CharField(max_length=100, null=True, blank=True)
    validityDate = models.DateField(null=True, blank=True)

    kycDetails = models.JSONField(default=dict)
    familyDetails = models.JSONField(default=dict)
    qualifications = models.JSONField(default=list)
    experiences = models.JSONField(default=list)

    bankDetails = models.JSONField(default=dict)
    salaryDetails = models.JSONField(default=dict)
    fnfStatus = models.JSONField(default=dict)

    profileImage = models.CharField(max_length=255, null=True, blank=True)
    created_by = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now_add=True)
    lastmodified_by = models.CharField(max_length=100)
    lastmodified_date = models.DateTimeField(auto_now=True)
    