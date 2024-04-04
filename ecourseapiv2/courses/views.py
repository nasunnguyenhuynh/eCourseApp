from rest_framework import viewsets, generics, status, parsers, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from courses.models import Category, Course, Lesson, User, Comment, Like
from courses import serializers, paginators, perms


class CategoryViewset(viewsets.ViewSet, generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = serializers.CategorySerializer


class CourseViewset(viewsets.ViewSet, generics.ListAPIView):
    queryset = Course.objects.filter(active=True)
    serializer_class = serializers.CourseSerializer
    pagination_class = paginators.CoursePaginator

    def get_queryset(self):  # /courses/?page=?&category_id=&q=
        queryset = self.queryset

        # Fix use arg q
        if self.action == 'list':  # check if the list of courses is being retrieved (not a specific course)
            q = self.request.query_params.get('q')
            if q:  # This parameter can be used to search for courses by name
                queryset = queryset.filter(name__icontains=q)  # <field>__icontains is special syntax

            cate_id = self.request.query_params.get('category_id')
            if cate_id:  # This parameter can be used to search for courses by category_id
                queryset = queryset.filter(category_id=cate_id)  # category_id is a field in course model

        return queryset

    @action(methods=['get'], url_path='lessons', detail=True)  # /courses/{course_id}/lessons/?q=
    # 'detail=true' meaning the action works on single object not entire collection
    def get_lessons(self, request, pk):  # pk: primary key of course
        lessons = self.get_object().lesson_set.filter(active=True)  # Get all lessons of the course

        q = self.request.query_params.get('q')
        if q:
            lessons = lessons.filter(subject__icontains=q)

        return Response(serializers.LessonSerializer(lessons, many=True).data,
                        status=status.HTTP_200_OK)


class LessonViewset(viewsets.ViewSet, generics.RetrieveAPIView):
    queryset = Lesson.objects.prefetch_related('tags').filter(
        active=True)  # prefetch_related tag -> to Enhance retrieve db
    serializer_class = serializers.LessonDetailsSerializer

    def get_serializer_class(self):
        if self.request.user.is_authenticated:
            return serializers.AuthenticatedLessonDetailsSerializer
        return self.serializer_class

    def get_permissions(self):
        if self.action in ['add_comments']:
            return [permissions.IsAuthenticated(), ]
        return [permissions.AllowAny(), ]

    @action(methods=['get'], url_path='comments', detail=True)  # /lessons/{lesson_id}/
    def get_comments(self, request, pk):
        """
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        """

        comments = self.get_object().comment_set.select_related('user').order_by("-id")
        paginator = paginators.CommentPaginator()
        page = paginator.paginate_queryset(comments, request)
        if page is not None:
            serializer = serializers.CommentSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        return Response(serializers.CommentSerializer(comments, many=True).data,
                        status=status.HTTP_200_OK)

    @action(methods=['post'], url_path='comments', detail=True)  # /lessons/{lesson_id}/comments/
    def add_comments(self, request, pk):  # Comment.objects.create()
        c = self.get_object().comment_set.create(content=request.data.get('content'),
                                                 user=request.user)
        return Response(serializers.CommentSerializer(c).data, status=status.HTTP_201_CREATED)

    @action(methods=['post'], url_path='like', detail=True)  # lessons/{id}/like
    def like(self, request, pk):
        li, created = Like.objects.get_or_create(lesson=self.get_object(),  # used for  unique together
                                                 user=request.user)
        if not created:
            li.active = not li.active
            li.save()

        return Response(serializers.LessonDetailsSerializer(self.get_object()).data, status=status.HTTP_201_CREATED)


class UserViewset(viewsets.ViewSet, generics.CreateAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = serializers.UserSerializer
    parser_classes = [parsers.MultiPartParser, ]  # to receive file

    def get_permissions(self):
        if self.action in ['get_current_user']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    @action(methods=['get', 'patch'], url_path='current-user', detail=False)  # /users/current-user/
    def get_current_user(self, request):
        user = request.user
        if request.method.__eq__('PATCH'):
            for k, v in request.data.items():
                setattr(user, k, v)
            user.save()

        return Response(serializers.UserSerializer(request.user).data)


class CommentViewset(viewsets.ViewSet, generics.DestroyAPIView, generics.UpdateAPIView):  # /comments/{id}/
    queryset = Comment.objects.all()
    serializer_class = serializers.CommentSerializer
    permission_classes = [perms.CommentOwner]
