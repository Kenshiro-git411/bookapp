from django import forms

class SearchForm(forms.Form):
    searchword = forms.CharField(label="検索ワード", max_length=10, )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["searchword"].widget.attrs["class"] = "block w-full h-12 pl-5 border rounded-full bg-gray-100 border-gray-600 shadow-md "
        self.fields["searchword"].widget.attrs["placeholder"] = "書籍名、論文名、著者名等を入力してください"
