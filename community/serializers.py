from rest_framework import serializers

from account.models import CustomUser as User

from .models import Comment, Post


class PostSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    author = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Post
        fields = [
            "id",
            "author",
            "username",
            "title",
            "content",
            "created_at",
            "updated_at",
            "view_count",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "view_count",
        ]

    def get_username(self, obj):
        return obj.author.username if obj.author else None


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["id", "post", "author", "content", "created_at"]
        read_only_fields = ["author", "created_at"]
