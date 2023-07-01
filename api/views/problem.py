# from ..utility import JSONParser, JSONParserOne, passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.sandbox.grader import grading, checker
from ..constant import GET,POST,PUT,DELETE
from ..models import Account, Problem,Testcase
from rest_framework import status
from django.forms.models import model_to_dict
from ..serializers import *
from ..utility import handle_uploaded_file


# Create your views here.
@api_view([POST])
def create_problem(request,account_id):
    request._mutable = True
    account = Account.objects.get(account_id=account_id)
    request.data['account_id'] = account
    
    checked = checker(1,request.data['solution'],request.data['testcases'],request.data.get('time_limit',1.5))

    if checked['has_error'] or checked['has_timeout']:
        return Response({'detail': 'Error during creating. Your code may has an error/timeout!','result': checked},status=status.HTTP_406_NOT_ACCEPTABLE)
        
    problem = Problem(
        language = request.data['language'],
        account = account,
        title = request.data['title'],
        description = request.data['description'],
        solution = request.data['solution'],
        time_limit = request.data['time_limit']
    )
    problem.save()

    testcase_result = []
    for unit in checked['result']:
        testcase = Testcase(
            problem = problem,
            input = unit['input'],
            output = unit['output']
        )
        testcase.save()
        testcase_result.append(model_to_dict(testcase))

    return Response({'detail': 'Problem has been created!','problem': model_to_dict(problem),'testcase': testcase_result},status=status.HTTP_201_CREATED)

@api_view([GET,DELETE])
def all_problem(request):
    if request.method == GET:

        problem = Problem.objects.all()

        get_private = int(request.query_params.get("private",0))
        get_deactive = int(request.query_params.get("deactive",0))
        account_id = int(request.query_params.get("account_id",0))
        
        if not get_private:
            problem = problem.filter(is_private=False)
        if not get_deactive:
            problem = problem.filter(is_active=True)
        if account_id != 0:
            problem = problem.filter(account_id=account_id)

        problem = problem.order_by('-problem_id')

        result = [model_to_dict(i) for i in problem]

        for i in result:
            i['creator'] = model_to_dict(Account.objects.get(account_id=i['account']))

        return Response({'result':result},status=status.HTTP_200_OK)
    elif request.method == DELETE:
        target = request.data.get("problem",[])
        problems = Problem.objects.filter(problem_id__in=target)
        problems.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
@api_view([GET,PUT,DELETE])
def one_problem(request,problem_id: int):
    try:
        problem = Problem.objects.get(problem_id=problem_id)
    except Problem.DoesNotExist:
        return Response({'detail': "Problem doesn't exist!"},status=status.HTTP_404_NOT_FOUND)
    testcases = Testcase.objects.filter(problem_id=problem_id)
    testfiles = TestFile.objects.filter(problem_id=problem_id)

    testcase_serializes = TestcaseSerializer(testcases,many=True)
    testfile_serializes = TestFileSerializer(testfiles,many=True)

    if request.method == GET:
            result = model_to_dict(problem)
            account = Account.objects.get(account_id=result['account'])
            account_serialize = AccountDetailSerializer(account)
            return Response({**result,'creator': account_serialize.data,'testcases':testcase_serializes.data,'testfiles': testfile_serializes.data},status=status.HTTP_200_OK)
    elif request.method == PUT:
        
        problem.title = request.data.get("title",problem.title)
        problem.language = request.data.get("language",problem.language)
        problem.description = request.data.get("description",problem.description)
        problem.solution = request.data.get("solution",problem.solution)
        problem.time_limit = request.data.get("time_limit",problem.time_limit)  
        problem.is_private = request.data.get("is_private",problem.is_private)

        if 'testcases' in request.data:
            checked = checker(1,problem.solution,request.data['testcases'],request.data.get('time_limit',1.5))
            if checked['has_error'] or checked['has_timeout']:
                return Response({'detail': 'Error during editing. Your code may has an error/timeout!'},status=status.HTTP_406_NOT_ACCEPTABLE)

            testcases.delete()
            testcase_result = []
            for unit in checked['result']:
                testcase = Testcase(
                    problem_id = problem,
                    input = unit['input'],
                    output = unit['output']
                )
                testcase.save()
                testcase_result.append(model_to_dict(testcase))
            problem.save()

            return Response({'detail': 'Problem has been edited!','problem': model_to_dict(problem),'testcase': testcase_result},status=status.HTTP_201_CREATED)

        problem.save()
        return Response({'detail': 'Problem has been edited!','problem': model_to_dict(problem)},status=status.HTTP_201_CREATED)

    elif request.method == DELETE:
        problem.delete()
        testcases.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
@api_view([PUT])
def add_testfile(request,problem_id:int):

    problem = Problem.objects.get(problem_id=problem_id)
    problem_serialize = ProblemSerializer(problem)

    testfile_serializes = []
    for file in request.FILES.getlist('testfile'):
        serialize = TestFileSerializer(data={'problem':problem_id,'file':file})
        if serialize.is_valid():
            serialize.save()
            testfile_serializes.append(serialize.data)
        else:
            return Response({'detail': 'Error during creating. Your code may has an error/timeout!'},status=status.HTTP_406_NOT_ACCEPTABLE)
    return Response({**problem_serialize.data,'testfile': testfile_serializes},status=status.HTTP_201_CREATED)

@api_view([PUT])
def remove_testfile(request,problem_id:int):
    problem = Problem.objects.get(problem_id=problem_id)
    problem_serialize = ProblemSerializer(problem)

    TestFile.objects.filter(problem=problem,testfile_id__in=request.data["testfile_ids"]).delete()

    return Response(problem_serialize.data,status=status.HTTP_204_NO_CONTENT)
