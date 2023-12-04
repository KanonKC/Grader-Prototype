from api.utility import passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.sandbox.grader import PythonGrader
from ...constant import GET,POST,PUT,DELETE
from ...models import *
from rest_framework import status
from django.forms.models import model_to_dict
from ...serializers import *

def add_problems_to_collection(collection:Collection,request):
    populated_problems = []

    index = 0
    for problem_id in request.data['problem_ids']:

        problem = Problem.objects.get(problem_id=problem_id)

        alreadyExist = CollectionProblem.objects.filter(problem=problem,collection=collection)
        if alreadyExist:
            alreadyExist.delete()
        
        collection_problem = CollectionProblem(
            problem=problem,
            collection=collection,
            order=index
        )
        collection_problem.save()
        index += 1
        populated_problems.append(collection_problem)
    
    problem_serialize = CollectionProblemPopulateProblemSecureSerializer(populated_problems,many=True)
    collection_serialize = CollectionSerializer(collection)

    return Response({
        **collection_serialize.data,
        'problems': problem_serialize.data
    },status=status.HTTP_201_CREATED)