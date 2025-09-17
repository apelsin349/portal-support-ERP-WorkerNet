"""
API serializers for WorkerNet Portal.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model

from app.models.ticket import Ticket, TicketComment, TicketAttachment, Tag, SLA, TicketSLA
from app.models.knowledge import KnowledgeArticle, KnowledgeCategory, KnowledgeArticleRating
from app.models.tenant import Tenant, TenantConfiguration
from django.contrib.auth import get_user_model

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tag model."""
    
    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'description', 'created_at']


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'avatar', 'phone', 'department', 'position', 'is_active',
            'is_verified', 'date_joined', 'last_login'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']


class TenantSerializer(serializers.ModelSerializer):
    """Serializer for Tenant model."""
    
    class Meta:
        model = Tenant
        fields = [
            'id', 'name', 'slug', 'domain', 'is_active',
            'logo', 'primary_color', 'secondary_color',
            'features', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TicketCommentSerializer(serializers.ModelSerializer):
    """Serializer for TicketComment model."""
    
    author = UserSerializer(read_only=True)
    
    class Meta:
        model = TicketComment
        fields = [
            'id', 'author', 'content', 'is_internal',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']


class TicketAttachmentSerializer(serializers.ModelSerializer):
    """Serializer for TicketAttachment model."""
    
    uploaded_by = UserSerializer(read_only=True)
    
    class Meta:
        model = TicketAttachment
        fields = [
            'id', 'uploaded_by', 'file', 'filename',
            'file_size', 'mime_type', 'created_at'
        ]
        read_only_fields = ['id', 'uploaded_by', 'filename', 'file_size', 'mime_type', 'created_at']


class TicketSerializer(serializers.ModelSerializer):
    """Serializer for Ticket model."""
    
    created_by = UserSerializer(read_only=True)
    assigned_to = UserSerializer(read_only=True)
    tenant = TenantSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    comments = TicketCommentSerializer(many=True, read_only=True)
    attachments = TicketAttachmentSerializer(many=True, read_only=True)
    
    # For creating/updating
    assigned_to_id = serializers.IntegerField(write_only=True, required=False)
    tag_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Ticket
        fields = [
            'id', 'ticket_id', 'title', 'description', 'priority',
            'status', 'category', 'created_by', 'assigned_to',
            'assigned_to_id', 'tenant', 'sla_hours', 'due_date',
            'resolved_at', 'created_at', 'updated_at', 'custom_fields',
            'tags', 'tag_ids', 'comments', 'attachments'
        ]
        read_only_fields = [
            'id', 'ticket_id', 'created_by', 'created_at',
            'updated_at', 'resolved_at'
        ]
    
    def create(self, validated_data):
        """Create a new ticket."""
        # Remove write-only fields
        assigned_to_id = validated_data.pop('assigned_to_id', None)
        tag_ids = validated_data.pop('tag_ids', [])
        
        # Set created_by to current user
        validated_data['created_by'] = self.context['request'].user
        validated_data['tenant'] = self.context['request'].user.tenant
        
        # Create ticket
        ticket = super().create(validated_data)
        
        # Set assigned_to if provided
        if assigned_to_id:
            try:
                assigned_to = User.objects.get(id=assigned_to_id, tenant=ticket.tenant)
                ticket.assigned_to = assigned_to
                ticket.save()
            except User.DoesNotExist:
                pass
        
        # Add tags
        if tag_ids:
            tags = Tag.objects.filter(id__in=tag_ids)
            ticket.tags.set(tags)
        
        return ticket
    
    def update(self, instance, validated_data):
        """Update a ticket."""
        # Remove write-only fields
        assigned_to_id = validated_data.pop('assigned_to_id', None)
        tag_ids = validated_data.pop('tag_ids', None)
        
        # Update ticket
        ticket = super().update(instance, validated_data)
        
        # Update assigned_to if provided
        if assigned_to_id is not None:
            if assigned_to_id:
                try:
                    assigned_to = User.objects.get(id=assigned_to_id, tenant=ticket.tenant)
                    ticket.assigned_to = assigned_to
                except User.DoesNotExist:
                    pass
            else:
                ticket.assigned_to = None
            ticket.save()
        
        # Update tags if provided
        if tag_ids is not None:
            tags = Tag.objects.filter(id__in=tag_ids)
            ticket.tags.set(tags)
        
        return ticket


class KnowledgeCategorySerializer(serializers.ModelSerializer):
    """Serializer for KnowledgeCategory model."""
    
    children = serializers.SerializerMethodField()
    articles_count = serializers.SerializerMethodField()
    
    class Meta:
        model = KnowledgeCategory
        fields = [
            'id', 'name', 'description', 'parent', 'children',
            'order', 'is_active', 'created_at', 'updated_at',
            'articles_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'articles_count']
    
    def get_children(self, obj):
        """Get child categories."""
        children = obj.children.filter(is_active=True)
        return self.__class__(children, many=True, context=self.context).data
    
    def get_articles_count(self, obj):
        """Get articles count for this category."""
        return obj.articles.filter(status='published').count()


class KnowledgeArticleSerializer(serializers.ModelSerializer):
    """Serializer for KnowledgeArticle model."""
    
    author = UserSerializer(read_only=True)
    category = KnowledgeCategorySerializer(read_only=True)
    tenant = TenantSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    
    # For creating/updating
    category_id = serializers.IntegerField(write_only=True)
    tag_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = KnowledgeArticle
        fields = [
            'id', 'title', 'slug', 'content', 'excerpt', 'category',
            'category_id', 'status', 'author', 'tenant', 'meta_title',
            'meta_description', 'keywords', 'view_count', 'helpful_count',
            'not_helpful_count', 'published_at', 'created_at', 'updated_at',
            'custom_fields', 'tags', 'tag_ids'
        ]
        read_only_fields = [
            'id', 'author', 'tenant', 'view_count', 'helpful_count',
            'not_helpful_count', 'published_at', 'created_at', 'updated_at'
        ]
    
    def create(self, validated_data):
        """Create a new knowledge article."""
        # Remove write-only fields
        category_id = validated_data.pop('category_id')
        tag_ids = validated_data.pop('tag_ids', [])
        
        # Set author and tenant
        validated_data['author'] = self.context['request'].user
        validated_data['tenant'] = self.context['request'].user.tenant
        
        # Set category
        try:
            category = KnowledgeCategory.objects.get(id=category_id, tenant=validated_data['tenant'])
            validated_data['category'] = category
        except KnowledgeCategory.DoesNotExist:
            raise serializers.ValidationError({'category_id': 'Invalid category ID'})
        
        # Create article
        article = super().create(validated_data)
        
        # Add tags
        if tag_ids:
            tags = Tag.objects.filter(id__in=tag_ids)
            article.tags.set(tags)
        
        return article
    
    def update(self, instance, validated_data):
        """Update a knowledge article."""
        # Remove write-only fields
        category_id = validated_data.pop('category_id', None)
        tag_ids = validated_data.pop('tag_ids', None)
        
        # Update category if provided
        if category_id is not None:
            try:
                category = KnowledgeCategory.objects.get(id=category_id, tenant=instance.tenant)
                validated_data['category'] = category
            except KnowledgeCategory.DoesNotExist:
                raise serializers.ValidationError({'category_id': 'Invalid category ID'})
        
        # Update article
        article = super().update(instance, validated_data)
        
        # Update tags if provided
        if tag_ids is not None:
            tags = Tag.objects.filter(id__in=tag_ids)
            article.tags.set(tags)
        
        return article


class KnowledgeArticleRatingSerializer(serializers.ModelSerializer):
    """Serializer for KnowledgeArticleRating model."""
    
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = KnowledgeArticleRating
        fields = [
            'id', 'user', 'rating', 'comment',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class SLASerializer(serializers.ModelSerializer):
    """Serializer for SLA model."""
    
    class Meta:
        model = SLA
        fields = [
            'id', 'name', 'description', 'response_time',
            'resolution_time', 'priority', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TicketSLASerializer(serializers.ModelSerializer):
    """Serializer for TicketSLA model."""
    
    sla = SLASerializer(read_only=True)
    
    class Meta:
        model = TicketSLA
        fields = [
            'id', 'sla', 'first_response_at', 'resolution_at',
            'is_breached', 'breach_reason', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
