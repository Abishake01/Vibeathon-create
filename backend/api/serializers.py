from rest_framework import serializers
from .models import Project, User


class UserRegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class TokenSerializer(serializers.Serializer):
    access_token = serializers.CharField()
    token_type = serializers.CharField(default='bearer')


class ProjectCreateSerializer(serializers.Serializer):
    name = serializers.CharField()
    description = serializers.CharField(required=False, allow_blank=True)


class ProjectUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(required=False)
    description = serializers.CharField(required=False, allow_blank=True)


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'user_id', 'name', 'description', 'created_at', 'updated_at']


class FileContentSerializer(serializers.Serializer):
    filename = serializers.CharField()
    content = serializers.CharField()


class ProjectFilesResponseSerializer(serializers.Serializer):
    project_id = serializers.CharField()
    files = FileContentSerializer(many=True)


class FileUpdateSerializer(serializers.Serializer):
    content = serializers.CharField()


class FileResponseSerializer(serializers.Serializer):
    filename = serializers.CharField()
    content = serializers.CharField()
    project_id = serializers.CharField()


class ChatMessageSerializer(serializers.Serializer):
    message = serializers.CharField()


class TodoItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    task = serializers.CharField()
    completed = serializers.BooleanField()


class AIProjectCreateSerializer(serializers.Serializer):
    prompt = serializers.CharField()
    name = serializers.CharField(required=False, allow_blank=True)
    provider = serializers.CharField(default='ollama')
    design_reference = serializers.CharField(required=False, allow_blank=True)
    design_examples = serializers.ListField(child=serializers.CharField(), required=False)


class AIProjectResponseSerializer(serializers.Serializer):
    project_id = serializers.CharField()
    todo_list = TodoItemSerializer(many=True)
    description = serializers.CharField()
    remaining_tokens = serializers.IntegerField(required=False, allow_null=True)


class TokenInfoSerializer(serializers.Serializer):
    remaining = serializers.IntegerField(required=False, allow_null=True)
    limit = serializers.IntegerField()
    used = serializers.IntegerField()

