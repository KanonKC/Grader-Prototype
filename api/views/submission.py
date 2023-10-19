from statistics import mode
from rest_framework.response import Response
from rest_framework.decorators import api_view

from api.serializers import SubmissionPopulateAllSerializer
from ..constant import GET,POST,PUT,DELETE
from ..models import Account, Problem, Submission,Testcase, SubmissionOutput
from rest_framework import status
from django.forms.models import model_to_dict
from ..sandbox import grader
from time import sleep
from ..serializers import *

QUEUE = [0,0,0,0,0,0,0,0,0,0]

def avaliableQueue():
    global QUEUE
    for i in range(len(QUEUE)):
        if QUEUE[i] == 0:
            return i
    return -1

@api_view([POST])
def submit_problem(request,problem_id,account_id):
    global QUEUE
    problem = Problem.objects.get(problem_id=problem_id)
    testcases = Testcase.objects.filter(problem=problem)

    submission_code = request.data['submission_code']
    solution_input = [model_to_dict(i)['input'] for i in testcases]
    solution_output = [model_to_dict(i)['output'] for i in testcases]

    empty_queue = avaliableQueue()
    while empty_queue == -1:
        empty_queue = avaliableQueue()
        sleep(5)
    QUEUE[empty_queue] = 1
    [grading_result,output] = grader.grading(empty_queue+1,submission_code,solution_input,solution_output)
    QUEUE[empty_queue] = 0

    if '-' in grading_result or 'E' in grading_result or 'T' in grading_result:
        is_passed = False
    else:
        is_passed = True

    submission = Submission(
        problem = problem,
        account = Account.objects.get(account_id=account_id),
        submission_code = request.data['submission_code'],
        result = grading_result,
        is_passed = is_passed,
        score = grading_result.count('P'),
        max_score = len(grading_result),
        passed_ratio = grading_result.count('P')/len(grading_result)
    )
    submission.save()

    submission_output = [
        SubmissionOutput(submission=submission,output=i['output'],runtime_status=i['runtime_status'],is_passed=i["is_passed"]) for i in output
    ]
    SubmissionOutput.objects.bulk_create(submission_output)

    submission_serializer = SubmissionSerializer(submission)
    submission_output_serializer = SubmissionOutputSerializer(submission_output,many=True)

    return Response({
        **submission_serializer.data
    },status=status.HTTP_201_CREATED)

@api_view([GET])
def get_submission_detail(request,submission_id:int):
    try:
        submission = Submission.objects.get(submission_id=submission_id)
        submission_output = SubmissionOutput.objects.filter(submission=submission)
        testcases = Testcase.objects.filter(problem=submission.problem)
        
        submission_serializer = SubmissionSerializer(submission)
        submission_output_serializer = SubmissionOutputSerializer(submission_output,many=True)
        testcases_serializer = TestcaseSerializer(testcases,many=True)

        return Response(
            {
                **submission_serializer.data,
                "submission_output": submission_output_serializer.data,
                "testcases": testcases_serializer.data
            },
            status=status.HTTP_200_OK
        )
    except Submission.DoesNotExist:
        return Response({'message': 'Submission not found'},status=status.HTTP_404_NOT_FOUND)

@api_view([GET])
def view_all_submission(request):
    
    problem_id = int(request.query_params.get("problem_id", 0))
    account_id = int(request.query_params.get("account_id", 0))
    # topic_id = int(request.query_params.get("topic_id", 0))
    passed = int(request.query_params.get("passed", -1))
    sort_score = int(request.query_params.get("sort_score", 0))
    sort_date = int(request.query_params.get("sort_date", 0))

    max_data = int(request.query_params.get("max_data", 50))
    
    submission = Submission.objects.all()

    if problem_id != 0:
        submission = submission.filter(problem_id=problem_id)
    if account_id != 0:
        submission = submission.filter(account_id=account_id)
    # if topic_id != 0:
    #     submission = submission.filter(account_id=account_id)

    if passed == 0:
        submission = submission.filter(is_passed=False)
    elif passed == 1:
        submission = submission.filter(is_passed=True)
    
    if sort_score == -1:
        submission = submission.order_by('passed_ratio')
    elif sort_score == 1:
        submission = submission.order_by('-passed_ratio')

    if sort_date == -1:
        submission = submission.order_by('date')
    elif sort_date == 1:
        submission = submission.order_by('-date')

    # submission = submission[:max_data]
        
    # result = [model_to_dict(i) for i in submission]
    serialize = SubmissionPopulateAllSerializer(submission,many=True)
    return Response({"result": serialize.data[:-100]},status=status.HTTP_200_OK)
    # result = serialize.data

    # print(result[0])

    # for row in result:
    #     count = 0
    #     for j in row.get('result'):
    #         if j == 'P':
    #             count += 1
    #     row['score'] = count

    # if passed == 0:
    #     result = [i for i in result if not i['is_passed']]
    # elif passed == 1:
    #     result = [i for i in result if i['is_passed']]

    # if sort_score == -1:
    #     result.sort(key=lambda value: value['score'])
    # if sort_score == 1:
    #     result.sort(key=lambda value: value['score'],reverse=True)
    
    # result = [{'problem': model_to_dict(Problem.objects.get(problem_id=i['problem'])),**i} for i in result]
    # return Response({'count':len(result),'result':result},status=status.HTTP_200_OK)