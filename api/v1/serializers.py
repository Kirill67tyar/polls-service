from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from polls.models import Choice, Poll, PollRun, Question


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = (
            "id",
            "text",
            "order",
        )


class ChoiceWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = (
            "text",
            "order",
        )


class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = (
            "id",
            "text",
            "order",
            "choices",
        )


class QuestionWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ("text", "order")


class PollListSerializer(serializers.ModelSerializer):
    owner = SlugRelatedField(slug_field="username", read_only=True)

    class Meta:
        model = Poll
        fields = (
            "id",
            "title",
            "owner",
            "is_published",
            "created_at",
        )


class PollDetailSerializer(serializers.ModelSerializer):
    owner = SlugRelatedField(slug_field="username", read_only=True)
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Poll
        fields = (
            "id",
            "title",
            "owner",
            "is_published",
            "created_at",
            "updated_at",
            "questions",
        )


class PollRunSerializer(serializers.ModelSerializer):
    class Meta:
        model = PollRun
        fields = (
            "id",
            "poll",
            "started_at",
            "completed_at",
        )
        read_only_fields = (
            "id",
            "poll",
            "started_at",
            "completed_at",
        )


class PollCreateSerializer(serializers.ModelSerializer):
    questions = QuestionWriteSerializer(many=True, required=False)

    class Meta:
        model = Poll
        fields = (
            "title",
            "is_published",
            "questions",
        )

    def create(self, validated_data: dict) -> Poll:
        questions_data = validated_data.pop("questions", [])
        request = self.context.get("request")
        owner = request.user
        poll = Poll.objects.create(owner=owner, **validated_data)
        if questions_data:
            Question.objects.bulk_create(
                [Question(poll=poll, **q) for q in questions_data],
            )
        return poll
