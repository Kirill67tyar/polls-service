from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.v1.views import (
    ChoiceDetailViewSet,
    ChoiceViewSet,
    PollViewSet,
    QuestionViewSet,
)

router_v1 = DefaultRouter()
router_v1.register("polls", PollViewSet, basename="poll")

urlpatterns_v1 = [
    path("", include(router_v1.urls)),
    path(
        "polls/<int:poll_pk>/questions/",
        QuestionViewSet.as_view({"get": "list", "post": "create"}),
    ),
    path(
        "questions/<int:pk>/",
        QuestionViewSet.as_view(
            {
                "get": "retrieve",
                "patch": "partial_update",
                "delete": "destroy",
            },
        ),
    ),
    path(
        "questions/<int:question_pk>/choices/",
        ChoiceViewSet.as_view({"get": "list", "post": "create"}),
    ),
    path(
        "choices/<int:pk>/",
        ChoiceDetailViewSet.as_view(
            {"patch": "partial_update", "delete": "destroy"},
        ),
    ),
]
