from django.urls import path
from .views import account,auth,problem, script,submission,topic,collection


urlpatterns = [
    path("login",auth.login),
    path("logout",auth.logout),
    path('token',auth.get_authorization),

    path("accounts",account.account_collection),
    path("accounts/<int:account_id>",account.get_account),
    path("accounts/<int:account_id>/daily-submissions",account.get_daily_submission),
    path("accounts/<int:account_id>/password",account.change_password),

    path('accounts/<int:account_id>/problems',problem.create_problem),
    path('problems',problem.all_problem),
    path('problems/<int:problem_id>',problem.one_problem),

    path('problems/<int:problem_id>/<int:account_id>',submission.submit_problem),
    path('submissions',submission.view_all_submission),
    path('submissions/<int:submission_id>',submission.get_submission_detail),

    path('accounts/<int:account_id>/topics',topic.create_topic),
    path('topics',topic.all_topic),
    path('topics/<int:topic_id>',topic.one_topic),
    path('topics/<int:topic_id>/access',topic.account_access),
    path('topics/<int:topic_id>/collections/<str:method>',topic.topic_collection),

    path('accounts/<int:account_id>/collections',collection.create_collections),
    path('collections',collection.all_collections),
    path('collections/<int:collection_id>',collection.one_collection),
    path('collections/<int:collection_id>/problems/<str:method>',collection.collection_problems),

    path('script',script.run_script),
]