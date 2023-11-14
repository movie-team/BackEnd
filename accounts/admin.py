from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

class UserAdmin(BaseUserAdmin):
    # list_display: 관리자 페이지의 목록에서 표시할 필드
    list_display = ('email', 'first_name', 'last_name', 'is_active', 'is_staff')
    
    # search_fields: 관리자 페이지에서 검색할 필드
    search_fields = ('email', 'first_name', 'last_name')

    # ordering: 변경 목록의 기본 정렬
    ordering = ('email',)

    # fieldsets: 세부 정보 뷰의 구조 정의
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )

    # add_fieldsets: '추가' 페이지에 표시할 필드
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )

    # filter_horizontal: 가로 필터에 표시할 다대다 관계 필드
    filter_horizontal = ()
    
    # list_filter: 변경 목록을 필터링할 필드
    list_filter = ('is_active', 'is_staff')

admin.site.register(User, UserAdmin)
