from rest_framework import serializers
from .models import Profile
from bson import ObjectId

class ProfileSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True, source='employeeId')
    created_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    lastmodified_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = Profile
        fields = [
            'id',
            'employeeId',
            'employeeName',
            'fatherName',
            'motherName',
            'gender',
            'mobileNumber',
            'bloodGroup',
            'maritalStatus',
            'guardianNumber',
            'dateOfBirth',
            'email',
            'department',
            'designation',
            'primaryRole',
            'additionalRoles',
            'dataEntitlements',
            'employmentStatus',
            'registrationNumber',
            'validityDate',
            'kycDetails',
            'familyDetails',
            'qualifications',
            'experiences',
            'bankDetails',
            'salaryDetails',
            'fnfStatus',
            'profileImage',
            'created_by',
            'created_date',
            'lastmodified_by',
            'lastmodified_date',
        ]
        read_only_fields = ['id', 'created_by', 'created_date', 'lastmodified_by', 'lastmodified_date']

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if isinstance(instance.pk, ObjectId):
            ret['id'] = str(instance.pk)
        return ret

    def create(self, validated_data):
        employee_id = self.context.get('employee_id')
        if employee_id:
            validated_data['created_by'] = employee_id
            validated_data['lastmodified_by'] = employee_id
        return Profile.objects.create(**validated_data)

    def update(self, instance, validated_data):
        employee_id = self.context.get('employee_id')
        if employee_id:
            validated_data['lastmodified_by'] = employee_id
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
