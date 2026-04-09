from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Poll(models.Model):
    title = models.CharField(max_length=500, verbose_name="Название опроса")
    owner = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name="own_polls",
        verbose_name="Владелец опроса",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    is_published = models.BooleanField(default=False, verbose_name="Опубликован")

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Опрос"
        verbose_name_plural = "Опросы"

    def __str__(self) -> str:
        return self.title


class Question(models.Model):
    poll = models.ForeignKey(
        to=Poll,
        on_delete=models.CASCADE,
        related_name="questions",
        verbose_name="Опрос",
    )
    text = models.TextField(verbose_name="Текст вопроса")
    order = models.PositiveSmallIntegerField(verbose_name="Порядок вопроса")

    class Meta:
        ordering = ("order",)
        constraints = [
            models.UniqueConstraint(
                fields=["poll", "order"],
                name="unique_poll_order",
            ),
        ]
        indexes = [
            models.Index(fields=["poll", "order"]),
        ]

    def __str__(self) -> str:
        return f"Question {self.pk}"


class Choice(models.Model):
    question = models.ForeignKey(
        to=Question,
        on_delete=models.CASCADE,
        related_name="choices",
        verbose_name="Вопрос",
    )
    text = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Текст варианта ответа",
    )
    order = models.PositiveIntegerField(verbose_name="Порядок варианта ответа")

    class Meta:
        ordering = ("order",)
        constraints = [
            models.UniqueConstraint(
                fields=["question", "order"],
                name="unique_question_order",
            ),
        ]
        indexes = [
            models.Index(fields=["question", "order"]),
        ]

    def __str__(self) -> str:
        return self.text or "(custom)"


class PollRun(models.Model):
    poll = models.ForeignKey(
        to=Poll,
        on_delete=models.CASCADE,
        related_name="runs",
        verbose_name="Опрос",
    )
    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name="poll_runs",
        verbose_name="Пользователь",
    )
    started_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата начала")
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Дата завершения",
    )

    class Meta:
        db_table = "polls_poll_runs"
        constraints = [
            models.UniqueConstraint(
                fields=["poll", "user"],
                name="unique_poll_user",
            ),
        ]
        indexes = [
            models.Index(fields=["poll", "user"]),
            models.Index(fields=["poll", "completed_at"]),
        ]

    def __str__(self) -> str:
        return self.pk


class QuestionAnswer(models.Model):
    poll_run = models.ForeignKey(
        PollRun,
        on_delete=models.CASCADE,
        related_name="answers",
        verbose_name="Проходимый опрос",
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="answers",
        verbose_name="Вопрос",
    )
    selected_choice = models.ForeignKey(
        Choice,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="selected_in_answers",
        verbose_name="Выбранный вариант ответа",
    )
    custom_text = models.TextField(
        blank=True,
        verbose_name="Текст пользовательского ответа",
    )

    class Meta:
        db_table = "polls_question_answers"
        constraints = [
            models.UniqueConstraint(
                fields=["poll_run", "question"],
                name="unique_poll_run_question",
            ),
        ]

    def __str__(self) -> str:
        return self.pk
