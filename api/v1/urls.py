from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.v1.views import ChoiceViewSet, PollModelViewSet, QuestionViewSet

router_v1 = DefaultRouter()
router_v1.register("polls", PollModelViewSet, basename="poll")
router_v1.register(
    r"polls/(?P<poll_pk>\d+)/questions",
    QuestionViewSet,
    basename="question",
)
router_v1.register(
    r"questions/(?P<question_pk>\d+)/choices",
    ChoiceViewSet,
    basename="choice",
)

urlpatterns_v1 = [
    path("", include(router_v1.urls)),
]
