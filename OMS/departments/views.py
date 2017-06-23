from django.shortcuts import render, redirect, get_object_or_404, HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from models import Department 
from forms import DepartmentForm


# Create your views here.

@login_required
@permission_required('Department.view_department', raise_exception=True)
def department_list(request, template_name='departments/department_list.html'):
    username = request.session['username']
    deps = Department.objects.all()
    var3 = 'active'
    return render(request, template_name, locals())


@login_required
@permission_required('Department.add_department', raise_exception=True)
def department_add(request, template_name='departments/department_add.html'):
    form = DepartmentForm(request.POST or None)
    username = request.session['username']
    print username
    if form.is_valid():
        print form
        form.save()
        return redirect('department_list')

    return render(request, template_name, {'form': form,
                                           'username': username,
                                           'var3': 'active',
                                           })


@login_required
@permission_required('Department.change_department', raise_exception=True)
def department_edit(request, pk, template_name='departments/department_add.html'):
    username = request.session['username']
    deps = get_object_or_404(Department, pk=pk)
    form = DepartmentForm(request.POST or None, instance=deps)
    if form.is_valid():
        form.save()
        return redirect('department_list')

    return render(request, template_name, {'form': form,
                                           'username': username,
                                           'var3': 'active',
                                           'deps': deps,
                                           })


@login_required
@permission_required('Department.delete_department', raise_exception=True)
def department_del(request):
    pk = request.GET['id']
    deps = get_object_or_404(Department, pk=int(pk))
    deps.delete()
    return HttpResponse('delete success')


@login_required
@permission_required('Department.view_department', raise_exception=True)
def department_detail(request, pk, template_name='departments/department_detail.html'):
    try:
        deps = Department.objects.get(pk=pk)
    except Department.DoesNotExist:
        raise Http404
    return render(request, template_name, {'deps': deps,
                                           'var3': 'active',
                                           'username': request.session['username'],
                                           })
