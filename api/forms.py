from django import forms
from django.contrib.auth.forms import (AuthenticationForm, UserCreationForm)
from django.contrib.auth import get_user_model

User = get_user_model()

class SearchForm(forms.Form):
    searchword = forms.CharField(label="検索ワード", max_length=10, )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["searchword"].widget.attrs["class"] = "block w-full h-12 pl-5 border rounded-full bg-gray-100 border-gray-600 shadow-md "
        self.fields["searchword"].widget.attrs["placeholder"] = "書籍名、論文名、著者名等を入力してください"


# Loginフォーム
class LoginForm(AuthenticationForm):
    username = forms.CharField(label="ユーザー名")
    password = forms.CharField(label="パスワード")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs["class"] = "block w-full border-0 px-2 py-1.5 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset sm:text-sm sm:leading-6"
        self.fields["username"].widget.attrs["placeholder"] = "ユーザー名を入力してください"
        self.fields["password"].widget.attrs["class"] = "block w-full border-0 px-2 py-1.5 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset sm:text-sm sm:leading-6"
        self.fields["password"].widget.attrs["placeholder"] = "パスワードを入力してください"

# Signupフォーム
class UserCreateForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'w-full pl-1 py-1 form-control'

    # 同じメールアドレスが使用されると仮登録段階でアカウントを消去する
    def clean_email(self):
        email = self.cleaned_data['email']
        User.objects.filter(email=email, is_active=False).delete()
        return email