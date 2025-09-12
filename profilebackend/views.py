import os
import mimetypes
from django.http import JsonResponse, HttpResponse, Http404
from rest_framework.decorators import api_view
from rest_framework import status
from pymongo import MongoClient
from bson import ObjectId
import gridfs
from django.contrib.auth.hashers import check_password, make_password
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("GLOBAL_DB_HOST")
DB_NAME = os.getenv("GLOBAL_DB_NAME")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# Collections
profile_col = db["backend_diagnostics_profile"]
dept_col = db["backend_diagnostics_Departments"]
desig_col = db["backend_diagnostics_Designation"]
role_col = db["backend_diagnostics_RoleMapping"]
user_col = db["backend_diagnostics_user"]

# GridFS bucket
fs = gridfs.GridFS(db, collection="fs")


@api_view(['GET'])
def get_employee_profile(request):
    employee_id = request.GET.get("employeeId")
    if not employee_id:
        return JsonResponse({"error": "employeeId missing"}, status=status.HTTP_400_BAD_REQUEST)

    profile = profile_col.find_one({"employeeId": employee_id})
    if not profile:
        return JsonResponse({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)

    # Convert ObjectId
    if "_id" in profile:
        profile["_id"] = str(profile["_id"])

    # Department
    if "department" in profile:
        dept = dept_col.find_one({"department_code": profile["department"]})
        if dept:
            profile["department"] = dept.get("department_name")

    # Designation
    if "designation" in profile:
        desig = desig_col.find_one({"Designation_code": profile["designation"]})
        if desig:
            profile["designation"] = desig.get("designation")

    # Primary Role
    if "primaryRole" in profile:
        role = role_col.find_one({"role_code": profile["primaryRole"]})
        if role:
            profile["primaryRole"] = role.get("role_name")

    # Additional Roles
    if "additionalRoles" in profile and isinstance(profile["additionalRoles"], list):
        role_names = []
        for code in profile["additionalRoles"]:
            role = role_col.find_one({"role_code": code})
            if role:
                role_names.append(role.get("role_name"))
        profile["additionalRoles"] = role_names

    # Profile Image
    if "profileImage" in profile:
        file_id = profile["profileImage"]
        profile["profileImageUrl"] = f"_b_a_c_k_e_n_d/profile/file/{file_id}/"
        del profile["profileImage"]

    return JsonResponse(profile, status=status.HTTP_200_OK, safe=False)


from django.http import FileResponse, Http404
from rest_framework.decorators import api_view
from pymongo import MongoClient
from gridfs import GridFS
from bson import ObjectId
import os, mimetypes

@api_view(['GET'])
def serve_file(request, file_id):
    try:
        client = MongoClient(os.getenv('GLOBAL_DB_HOST'))
        db = client[os.getenv('GLOBAL_DB_NAME', 'Global')]
        fs = GridFS(db)

        file_id = ObjectId(file_id)
        file = fs.get(file_id)

        # Guess MIME type
        content_type, _ = mimetypes.guess_type(file.filename)
        if not content_type:
            content_type = file.content_type or 'application/octet-stream'

        response = FileResponse(file, content_type=content_type)
        response['Content-Disposition'] = f'inline; filename="{file.filename}"'
        return response
    except Exception as e:
        raise Http404(f"File not found or invalid: {str(e)}")



@api_view(['PUT'])
def update_profile_image(request):
    employee_id = request.data.get("employeeId")
    image_file = request.FILES.get("profileImage")

    if not employee_id or not image_file:
        return JsonResponse({"error": "employeeId and profileImage required"}, status=400)

    # Remove old image if exists
    profile = profile_col.find_one({"employeeId": employee_id})
    if profile and "profileImage" in profile:
        try:
            fs.delete(ObjectId(profile["profileImage"]))
        except Exception:
            pass

    # Save new image into GridFS
    file_id = fs.put(image_file, filename=f"{employee_id}_profile")

    # Update profile with reference ID
    result = profile_col.update_one(
        {"employeeId": employee_id},
        {"$set": {"profileImage": str(file_id)}}
    )

    if result.matched_count == 0:
        return JsonResponse({"error": "Profile not found"}, status=404)

    return JsonResponse({"success": True, "profileImage": str(file_id)})

@api_view(['PUT'])
def update_employee_profile(request):
    employee_id = request.data.get("employeeId")
    email = request.data.get("email")
    mobile = request.data.get("mobileNumber")

    result = profile_col.update_one(
        {"employeeId": employee_id},
        {"$set": {"email": email, "mobileNumber": mobile}}
    )

    if result.matched_count == 0:
        return JsonResponse({"error": "Profile not found"}, status=404)

    return JsonResponse({"success": True, "message": "Profile updated"})

@api_view(['PUT'])
def change_password(request):
    employee_id = request.data.get("employeeId")
    old_password = request.data.get("oldPassword")
    new_password = request.data.get("newPassword")

    if not employee_id or not old_password or not new_password:
        return JsonResponse({"error": "Missing fields"}, status=status.HTTP_400_BAD_REQUEST)

    # Find user
    user = user_col.find_one({"employeeId": employee_id})
    if not user:
        return JsonResponse({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    stored_hash = user.get("password")
    if not stored_hash:
        return JsonResponse({"error": "Password not set"}, status=status.HTTP_400_BAD_REQUEST)

    # Verify old password
    if not check_password(old_password, stored_hash):
        return JsonResponse({"error": "Old password incorrect"}, status=status.HTTP_400_BAD_REQUEST)

    # Hash new password
    new_hash = make_password(new_password)

    # Update MongoDB
    result = user_col.update_one(
        {"employeeId": employee_id},
        {"$set": {"password": new_hash}}
    )

    if result.modified_count == 1:
        return JsonResponse({"success": True, "message": "Password updated"})
    else:
        return JsonResponse({"error": "Password update failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
