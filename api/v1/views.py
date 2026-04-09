from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.v1.serializers import (
    ChoiceSerializer,
    ChoiceWriteSerializer,
    PollCreateSerializer,
    PollDetailSerializer,
    PollListSerializer,
    PollRunSerializer,
    QuestionSerializer,
    QuestionWriteSerializer,
)
from polls.models import Choice, Poll, PollRun, Question


class PollModelViewSet(viewsets.ModelViewSet):
    http_method_names = ("get", "post", "delete", "head", "options")
    queryset = Poll.objects.all()

    def get_queryset(self):
        user = self.request.user
        respondent_ok = Q(is_published=True) | Q(owner_id=user.id)
        if self.action in ("retrieve", "start"):
            return self.queryset.filter(respondent_ok).order_by("-created_at")
        return self.queryset.filter(owner=user).order_by("-created_at")

    def get_serializer_class(self):
        if self.action == "create":
            return PollCreateSerializer
        if self.action == "retrieve":
            return PollDetailSerializer
        return PollListSerializer

    @action(detail=False, methods=["get"], url_path="all")
    def all(self, request):
        qs = self.queryset.filter(is_published=True).order_by("-created_at")
        return Response(data=PollListSerializer(qs, many=True).data)

    @action(detail=True, methods=["post"], url_path="start")
    def start(self, request, pk=None):
        poll = self.get_object()
        run, created = PollRun.objects.get_or_create(poll=poll, user=request.user)
        data = PollRunSerializer(run).data
        st = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(data=data, status=st)

    @action(detail=True, methods=["post"], url_path="publish")
    def publish(self, request, pk=None):
        poll = self.get_object()
        poll.is_published = True
        poll.save(update_fields=["is_published", "updated_at"])
        poll.refresh_from_db()
        return Response(data=PollDetailSerializer(poll).data)

    @action(detail=True, methods=["post"], url_path="unpublish")
    def unpublish(self, request, pk=None):
        poll = self.get_object()
        poll.is_published = False
        poll.save(update_fields=["is_published", "updated_at"])
        poll.refresh_from_db()
        return Response(data=PollDetailSerializer(poll).data)


class QuestionViewSet(viewsets.ModelViewSet):
    http_method_names = ("get", "post", "delete", "head", "options")
    queryset = Question.objects.all()

    def get_queryset(self):
        user = self.request.user
        poll_pk = self.kwargs["poll_pk"]
        visible = Q(poll__is_published=True) | Q(poll__owner_id=user.id)
        owned = Q(poll__owner_id=user.id)
        if self.action in ("list", "retrieve"):
            qs = self.queryset.filter(visible)
        else:
            qs = self.queryset.filter(owned)
        return qs.filter(poll_id=poll_pk).order_by("order")

    def get_serializer_class(self):
        if self.action == "create":
            return QuestionWriteSerializer
        return QuestionSerializer

    def perform_create(self, serializer):
        poll_pk = self.kwargs["poll_pk"]
        poll = get_object_or_404(Poll, pk=poll_pk, owner_id=self.request.user.id)
        serializer.save(poll=poll)


class ChoiceViewSet(viewsets.ModelViewSet):
    http_method_names = ("get", "post", "delete", "head", "options")
    queryset = Choice.objects.all()

    def get_queryset(self):
        user = self.request.user
        visible = Q(question__poll__is_published=True) | Q(
            question__poll__owner_id=user.id,
        )
        owned = Q(question__poll__owner_id=user.id)
        question_pk = self.kwargs["question_pk"]
        if self.action == "destroy":
            return (
                self.queryset.filter(owned)
                .filter(question_id=question_pk)
                .order_by("order")
            )
        return (
            self.queryset.filter(visible)
            .filter(question_id=question_pk)
            .order_by("order")
        )

    def get_serializer_class(self):
        if self.action == "create":
            return ChoiceWriteSerializer
        return ChoiceSerializer

    def perform_create(self, serializer):
        q_id = self.kwargs["question_pk"]
        question = get_object_or_404(
            Question,
            pk=q_id,
            poll__owner_id=self.request.user.id,
        )
        serializer.save(question=question)
