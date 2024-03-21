from django.contrib import admin
from courses.models import Category, Course, Lesson, Tag
from django.utils.html import mark_safe
from django import forms
from ckeditor_uploader.widgets import CKEditorUploadingWidget


class CourseForm(forms.ModelForm):  # add static be4 url when send it to server
    description = forms.CharField(widget=CKEditorUploadingWidget)

    class Meta:
        model = Course
        fields = '__all__'


class CourseAdmin(admin.ModelAdmin):  # Custom admin view
    list_display = ['id', 'name', 'created_date', 'updated_date', 'active']
    search_fields = ['name', 'description']
    list_filter = ['id', 'name', 'created_date']
    readonly_fields = ['my_image']
    form = CourseForm

    def my_image(self, course):
        if course.image:
            return mark_safe(f'<img src="{course.image.url}" width="200" />')

    class Media:
        css = {
            'all': ('/static/css/style.css',)
        }
        # js = ('/static/js/script.js',)


admin.site.register(Category)
admin.site.register(Lesson)
admin.site.register(Tag)
admin.site.register(Course, CourseAdmin)
