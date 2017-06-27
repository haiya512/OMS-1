# --*-- coding: utf-8 --*--

import decimal
import re
from IPy import IP
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.shortcuts import render, redirect, HttpResponse
from assets.models import Network, Hardware, Assets
from models import SaltKey
from saltstack.scripts.execute_command import running_command
from saltstack.scripts.copy_anything import do_copy
from saltstack.scripts.salt_api import *
from OMS.settings import MASTER_HOST, SHELL_ROOT

# Create your views here.


@login_required
@permission_required('Salt.view_release', raise_exception=True)
def salt_key_manager(request, template_name='saltstack/salt_introduction.html'):
    data = {
            'expr_form': 'list',
            'client': 'wheel',
            'fun': 'key.list_all',
        }

    salt = SaltApi()
    salt.get_token()
    header = salt.get_header()
    context = key_manager(header, **data)
    minions_num = len(context['data']['return']['minions'])
    minions_rejected_num = len(context['data']['return']['minions_rejected'])
    minions_denied_num = len(context['data']['return']['minions_denied'])
    minions_pre_num = len(context['data']['return']['minions_pre'])
    minions = context['data']['return']['minions']
    # print minions
    minions_pre = context['data']['return']['minions_pre']
    username = request.session['username']
    key_list1 = '%s %s' % (minions_num, minions_denied_num)
    key_list2 = '%s %s' % (minions_pre_num, minions_rejected_num)
    var7 = 'active'
    highlight1 = 'active'

    minions_object = SaltKey.objects.filter(status=1)

    return render(request, template_name, locals())


@login_required
@permission_required('saltstack.view_release', raise_exception=True)
def salt_key_accept(request, minion):
    # 接受key
    data = {
        'expr_form': 'list',
        'client': 'wheel',
        'fun': 'key.accept',
        'match': minion
    }

    salt = SaltApi()
    salt.get_token()
    header = salt.get_header()
    content = key_manager(header, **data)

    if content['data']['success']:
        data1 = {
            'expr_form': 'list',
            'client': 'wheel',
            'fun': 'key.finger',
            'match': minion
        }

        return_comment = key_manager(header, **data1)
        finger = return_comment['data']['return']['minions'][minion]
        # 将key信息存入数据库
        if SaltKey.objects.filter(minion=minion):
            if minion == MASTER_HOST:
                SaltKey.objects.filter(minion=minion).update(type=u'1', status=1)
            else:
                SaltKey.objects.filter(minion=minion).update(type=u'2', status=1)
        else:
            if minion == MASTER_HOST:
                keys = SaltKey(minion=minion, type=u'1', finger=finger, timestamp=return_comment['data']['_stamp'],
                               status=1, is_getinfo=0)
            else:
                keys = SaltKey(minion=minion, type=u'2', finger=finger, timestamp=return_comment['data']['_stamp'],
                               status=1, is_getinfo=0)
            keys.save()

    return redirect('salt_key_manager')


@login_required
@permission_required('Salt.view_release', raise_exception=True)
def salt_key_delete(request, minion):
    data = {
        'expr_form': 'list',
        'client': 'wheel',
        'fun': 'key.delete',
        'match': minion
    }
    salt = SaltApi()
    salt.get_token()
    header = salt.get_header()
    content = key_manager(header, **data)
    print content

    if content['data']['success']:
        SaltKey.objects.filter(minion=minion).update(status=2)

    return redirect('salt_key_manager')


@login_required
@permission_required('Salt.view_release', raise_exception=True)
def push_agent_scripts(request, minion):
    agent_dir = '/data/deploy/OMS/saltstack/agents'
    src_dir = '/srv/salt/agent_scripts'
    salt_url = 'salt://agent_scripts'
    des_dir = '/data'
    if not os.path.exists(src_dir):
        do_copy(agent_dir, src_dir)
    else:
        pass

    data = {
        'expr_form': 'list',
        'client': 'local',
        'fun': 'cp.get_dir',
        'tgt': minion,
        'arg': [salt_url, des_dir],
    }
    print data
    salt = SaltApi()
    salt.get_token()
    header = salt.get_header()
    context = process(header, **data)
    print context
    SaltKey.objects.filter(minion=minion).update(is_push_scripts=1)

    return redirect('salt_key_manager')


@login_required
def get_servers_info(request, minion):
    salt = SaltApi()
    salt.get_token()
    header = salt.get_header()
    context = get_grains_items(header, minion)
    print context
    ip_address = {}
    disks = {}
    # 取得ip地址信息存入ip_address字典中
    for key in context[minion]['ip4_interfaces']:
        if key == 'lo' or key == 'usb0':
            pass
        else:
            ip_address['private'] = None
            ip_address['public'] = None
            ip = context[minion]['ip4_interfaces'][key][0]
            if ip:
                address = IP(ip)
                if address.iptype() == 'PRIVATE':
                    ip_address['private'] = ip
                else:
                    ip_address['public'] = ip

    print ip_address
    # 检查数据库中是否存在，如果不存在则存入
    try:
        if ip_address['private']:
            if Network.objects.get(private_address=ip_address['private']):
                print "The record in table nothing to do!"
        else:
            if Network.objects.get(public_address=ip_address['public']):
                print "The record in table nothing to do!"
    except Network.DoesNotExist:
        nets = Network(public_address=ip_address['public'], private_address=ip_address['private'], bandwidth=0, 
                       unit=1, bind=0, net_type=1, provide=u'------')
        nets.save()

    # 检查cpu配置，如果没有则存入
    try:
        Hardware.objects.get(name='cpu', value=context[minion]['num_cpus'])
    except Hardware.DoesNotExist:
        hardware = Hardware(name='cpu', value=context[minion]['num_cpus'], unit=2)
        hardware.save()

    mem = int(round(decimal.Decimal(float(context[minion]['mem_total']) / 1024), 0))
    if mem < 1:
        mem = round(decimal.Decimal(float(context[minion]['mem_total']) / 1024), 1)
    print mem

    # 检查内存配置，如果没有存入
    try:
        Hardware.objects.get(name='memory', value=mem)
    except Hardware.DoesNotExist:
        hardware = Hardware(name='memory', value=mem, unit=1)
        hardware.save()

    # 检查磁盘，如果不存在存入
    for key in context[minion]:
        pattern = re.compile(r'[s-v]d[a-z]_size$')
        m = pattern.match(key)
        if m:
            disks['%s' % m.group()] = int(context[minion]['%s' % m.group()].split()[0])
        for item in disks:
            try:
                Hardware.objects.get(name=item, value=disks[item])
            except Hardware.DoesNotExist:
                hardware = Hardware(name=item, value=disks[item], unit=1)
                hardware.save()

    system = context[minion]['osfinger']

    # 检查资产,没有存入，并检查关联
    try:
        Assets.objects.get(host_name=minion)
        return HttpResponse("Asset already exist!")
    except Assets.DoesNotExist:
        if ip_address['private']:
            networks = Network.objects.get(private_address=ip_address['private'])
        else:
            networks = Network.objects.get(public_address=ip_address['public'])
        cpu_cores = Hardware.objects.get(name='cpu', value=context[minion]['num_cpus'])
        memories = Hardware.objects.get(name='memory', value=mem)

        assets = Assets(host_name=minion, alias_name=minion, host_type=2, os=system, is_online=True,
                        is_minion=1, is_unused=False, superuser=u'root', superuser_pass=u'------')
        assets.networks_id = networks.id
        assets.save()
        assets.hardware.add(cpu_cores.id, memories.id)
        for item in disks:
            disk = Hardware.objects.get(name=item, value=disks[item])
            disk_id = disk.id
            assets.hardware.add(disk_id)
        Network.objects.filter(id=networks.id).update(bind=1)

        keys = SaltKey.objects.filter(minion=minion)
        keys.update(is_getinfo=1)

        return HttpResponse('OK')


@login_required
def sync_grains(request, minion):
    script = os.path.join(SHELL_ROOT, 'sync_model.sh')
    command = "sh %s" % script
    print command
    if running_command(command):
        return HttpResponse('OK')
