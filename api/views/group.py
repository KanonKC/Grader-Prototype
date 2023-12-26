from api.utility import passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.sandbox.grader import PythonGrader
from ..constant import GET,POST,PUT,DELETE
from ..models import *
from rest_framework import status
from django.forms.models import model_to_dict
from ..serializers import *
from ..controllers.group.create_group import create_group
from ..controllers.group.update_group import update_group
from ..controllers.group.delete_group import delete_group
from ..controllers.group.update_members_to_group import update_members_to_group

@api_view([POST])
def all_groups_creator_view(request,account_id:int):
    account = Account.objects.get(account_id=account_id)
    if request.method == POST:
        return create_group(request)

@api_view([PUT,DELETE])
def one_group_creator_view(request,group_id:int):
    group = Group.objects.get(group_id=group_id)
    if request.method == PUT:
        return update_group(group,request)
    elif request.method == DELETE:
        return delete_group(group,request)
    
@api_view([PUT])
def group_members_view(request,group_id:int):
    group = Group.objects.get(group_id=group_id)
    if request.method == PUT:
        return update_members_to_group(group,request)