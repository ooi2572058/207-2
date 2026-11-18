from django.views.generic import TemplateView


class IndexGuestView(TemplateView):
    """index 0: 未ログイン（ゲスト）画面"""
    template_name = 'index/index_guest.html'


class IndexUserView(TemplateView):
    """index 1: 一般ユーザー画面"""
    template_name = 'index/index_user.html'


class IndexCorporateView(TemplateView):
    """index 2: 法人画面"""
    template_name = 'index/index_corporate.html'


class IndexAdminView(TemplateView):
    """index 3: アドミン（管理者）画面"""
    template_name = 'index/index_admin.html'