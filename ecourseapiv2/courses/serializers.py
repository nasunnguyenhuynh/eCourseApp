from courses.models import Category, Course, Lesson, Tag, User, Comment
from rest_framework import serializers


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ItemSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):  # Rewrite image field
        rep = super().to_representation(instance)
        rep['image'] = instance.image.url

        return rep


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']


class CourseSerializer(ItemSerializer):
    class Meta:
        model = Course
        fields = ['id', 'name', 'image', 'created_date']


class LessonSerializer(ItemSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'subject', 'image', 'created_date']


class LessonDetailsSerializer(LessonSerializer):
    tags = TagSerializer(many=True)

    class Meta:
        model = LessonSerializer.Meta.model
        fields = LessonSerializer.Meta.fields + ['tags', 'content']


class AuthenticatedLessonDetailsSerializer(LessonDetailsSerializer):
    liked = serializers.SerializerMethodField()

    def get_liked(self, lesson):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return lesson.like_set.filter(user=request.user, active=True).exists()

    class Meta:
        model = LessonDetailsSerializer.Meta.model
        fields = LessonDetailsSerializer.Meta.fields + ['liked']


class UserSerializer(serializers.ModelSerializer):
    def create(self, validated_data):  # hash password be4 store in database
        data = validated_data.copy()
        user = User(**data)  # unpacking dict and pass them as arg into init model User
        user.set_password(user.password)
        user.save()

        return user

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'username', 'password', 'avatar']
        extra_kwargs = {  # prevent the password field returned when creating a new user
            'password': {
                'write_only': 'true'
            }
        }


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Comment
        fields = ['id', 'content', 'created_date', 'user']
