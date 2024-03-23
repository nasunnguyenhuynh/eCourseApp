from rest_framework import viewsets, generics, status, parsers
from rest_framework.decorators import action
from rest_framework.response import Response
from courses.models import Category, Course, Lesson, User
from courses import serializers, paginators


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
    queryset = Lesson.objects.prefetch_related('tags').filter(active=True)  # prefetch_related tag -> to Enhance retrieve db
    serializer_class = serializers.LessonDetailsSerializer

    @action(methods=['get'], url_path='comments', detail=True)
    def get_comments(self, request, pk):
        comments = self.get_object().comment_set.select_related('user').all()

        return Response(serializers.CommentSerializer(comments, many=True).data,
                        status=status.HTTP_200_OK)


class UserViewset(viewsets.ViewSet, generics.CreateAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = serializers.UserSerializer
    parser_classes = [parsers.MultiPartParser, ]  # to receive file
