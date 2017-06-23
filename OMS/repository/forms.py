# --*-- coding:utf8 --*--

from django import forms
from models import Repository, Version
from departments.models import Department


class RepositoryForm(forms.ModelForm):

    class Meta:
        model = Repository
        fields = '__all__'


class VersionForm(forms.ModelForm):
    # department = forms.ModelChoiceField(label=u'项目组', queryset=Department.objects.all())
    project = forms.CharField(max_length=20, label=u'项目', widget=forms.HiddenInput(), required=False)
    repository = forms.ModelChoiceField(label=u'仓库', queryset=Repository.objects.all())
    archive_path = forms.CharField(max_length=200, label=u'本地归档路径', initial=u'/srv/salt/code/project/')
    version = forms.CharField(max_length=20, label=u'版本', widget=forms.HiddenInput(), required=False)
    timestamp = forms.DateTimeField(label=u'时间', widget=forms.HiddenInput(), required=False)
    author = forms.CharField(max_length=20, label=u'提交用户', widget=forms.HiddenInput(), required=False)
    vernier = forms.CharField(label=u'游标', widget=forms.HiddenInput(), required=False)
    is_backup = forms.BooleanField(label=u'是否备份', widget=forms.HiddenInput(), required=False)
    content = forms.CharField(label=u'备注', widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Version
        fields = '__all__'


class LocalArchiveForm(forms.Form):
    departments = forms.ModelChoiceField(label=u'项目组', queryset=Department.objects.all())
    repository = forms.ModelChoiceField(label=u'仓库', queryset=Repository.objects.all())
    archive_path = forms.CharField(max_length=200, label=u'本地归档路径', initial=u'/srv/salt/code/project/')

    # def clean(self):
    #     cleaned_data = super(LocalArchiveForm, self).clean()
    #     return cleaned_data
