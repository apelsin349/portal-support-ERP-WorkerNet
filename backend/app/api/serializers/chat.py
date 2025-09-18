"""
Сериализаторы для системы чата.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model

from app.models import ChatMessage

User = get_user_model()


class ChatMessageSerializer(serializers.ModelSerializer):
    """Сериализатор для сообщений чата."""
    
    sender_name = serializers.CharField(source='sender.get_full_name', read_only=True)
    sender_avatar = serializers.ImageField(source='sender.avatar', read_only=True)
    
    class Meta:
        model = ChatMessage
        fields = [
            'id', 'room_name', 'sender', 'sender_name', 'sender_avatar',
            'content', 'message_type', 'timestamp'
        ]
        read_only_fields = ['id', 'timestamp']


class ChatMessageCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания сообщений чата."""
    
    class Meta:
        model = ChatMessage
        fields = ['room_name', 'content', 'message_type']
    
    def create(self, validated_data):
        """Создание сообщения."""
        validated_data['sender'] = self.context['request'].user
        return super().create(validated_data)


class ChatMessageUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления сообщений чата."""
    
    class Meta:
        model = ChatMessage
        fields = ['content']
    
    def update(self, instance, validated_data):
        """Обновление сообщения."""
        return super().update(instance, validated_data)


class ChatConversationSerializer(serializers.Serializer):
    """Сериализатор для беседы в чате."""
    
    user = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    last_message_time = serializers.SerializerMethodField()
    
    def get_user(self, obj):
        """Информация о пользователе."""
        from app.api.serializers.auth import UserSerializer
        return UserSerializer(obj).data
    
    def get_last_message(self, obj):
        """Последнее сообщение."""
        last_message = ChatMessage.objects.filter(
            Q(sender=obj, recipient=self.context['request'].user) |
            Q(sender=self.context['request'].user, recipient=obj)
        ).order_by('-created_at').first()
        
        if last_message:
            return ChatMessageSerializer(last_message).data
        return None
    
    def get_unread_count(self, obj):
        """Количество непрочитанных сообщений."""
        return ChatMessage.objects.filter(
            sender=obj,
            recipient=self.context['request'].user,
            is_read=False
        ).count()
    
    def get_last_message_time(self, obj):
        """Время последнего сообщения."""
        last_message = ChatMessage.objects.filter(
            Q(sender=obj, recipient=self.context['request'].user) |
            Q(sender=self.context['request'].user, recipient=obj)
        ).order_by('-created_at').first()
        
        if last_message:
            return last_message.created_at
        return None


class ChatStatsSerializer(serializers.Serializer):
    """Сериализатор для статистики чата."""
    
    total_messages = serializers.IntegerField()
    unread_messages = serializers.IntegerField()
    active_conversations = serializers.IntegerField()
    
    messages_by_type = serializers.DictField()
    messages_by_hour = serializers.DictField()
    
    most_active_users = serializers.ListField()
    recent_conversations = serializers.ListField()


class ChatMessageSearchSerializer(serializers.Serializer):
    """Сериализатор для поиска сообщений."""
    
    query = serializers.CharField(max_length=255)
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False
    )
    message_type = serializers.ChoiceField(choices=[
        ("text", "text"),
        ("image", "image"),
        ("file", "file"),
        ("system", "system"),
    ], required=False)
    date_from = serializers.DateTimeField(required=False)
    date_to = serializers.DateTimeField(required=False)
    
    def validate(self, attrs):
        """Валидация параметров поиска."""
        if attrs.get('date_from') and attrs.get('date_to'):
            if attrs['date_from'] > attrs['date_to']:
                raise serializers.ValidationError(
                    "Дата начала не может быть больше даты окончания"
                )
        return attrs


class ChatMessageReactionSerializer(serializers.Serializer):
    """Сериализатор для реакций на сообщения."""
    
    emoji = serializers.CharField(max_length=10)
    message_id = serializers.IntegerField()
    
    def validate_emoji(self, value):
        """Валидация эмодзи."""
        # Простая валидация эмодзи
        if not value or len(value) > 10:
            raise serializers.ValidationError("Некорректное эмодзи")
        return value


class ChatTypingSerializer(serializers.Serializer):
    """Сериализатор для статуса набора текста."""
    
    user_id = serializers.IntegerField()
    is_typing = serializers.BooleanField()
    conversation_id = serializers.IntegerField(required=False)


class ChatOnlineStatusSerializer(serializers.Serializer):
    """Сериализатор для статуса онлайн."""
    
    user_id = serializers.IntegerField()
    is_online = serializers.BooleanField()
    last_seen = serializers.DateTimeField()
