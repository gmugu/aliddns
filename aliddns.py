import json
import logging
import os
from aliyunsdkcore.client import AcsClient

logger = logging.getLogger('mugu.'+__name__)

accessKeyId = os.environ.get('ACCESS_KEY_ID')  # 将accessKeyId改成自己的accessKeyId
accessSecret = os.environ.get('ACCESS_SECRET')  # 将accessSecret改成自己的accessSecret
domain = os.environ.get('DOMAIN')  # 你的主域名

client = AcsClient(accessKeyId, accessSecret, 'cn-hangzhou')

def ali_update(RecordId, RR, Type, Value):  # 修改域名解析记录
    from aliyunsdkalidns.request.v20150109.UpdateDomainRecordRequest import UpdateDomainRecordRequest
    request = UpdateDomainRecordRequest()
    request.set_accept_format('json')
    request.set_RecordId(RecordId)
    request.set_RR(RR)
    request.set_Type(Type)
    request.set_Value(Value)
    response = client.do_action_with_exception(request)
    logger.info(f'修改域名解析记录返回结果:{response}')


def ali_add(DomainName, RR, Type, Value):  # 添加新的域名解析记录
    from aliyunsdkalidns.request.v20150109.AddDomainRecordRequest import AddDomainRecordRequest
    request = AddDomainRecordRequest()
    request.set_accept_format('json')
    request.set_DomainName(DomainName)
    request.set_RR(RR)
    request.set_Type(Type)
    request.set_Value(Value)
    response = client.do_action_with_exception(request)
    logger.info(f'添加新的域名解析记录返回结果:{response}')


def ali_del_subdomain(DomainName, RR, Type):  # 删除整个子域名
    from aliyunsdkalidns.request.v20150109.DeleteSubDomainRecordsRequest import DeleteSubDomainRecordsRequest
    request = DeleteSubDomainRecordsRequest()
    request.set_accept_format('json')
    request.set_DomainName(DomainName)
    request.set_RR(RR)
    request.set_Type(Type)
    response = client.do_action_with_exception(request)
    logger.info(f'删除整个子域名返回结果:{response}')


def ali_get(DomainName, Sub_domain, Type):  # 获取域名解析记录列表
    from aliyunsdkalidns.request.v20150109.DescribeSubDomainRecordsRequest import DescribeSubDomainRecordsRequest
    request = DescribeSubDomainRecordsRequest()
    request.set_accept_format('json')
    request.set_DomainName(DomainName)
    request.set_SubDomain(Sub_domain + '.' + domain)
    request.set_Type(Type)
    response = client.do_action_with_exception(request)
    logger.info(f'获取域名解析记录列表返回结果:{response}')
    domain_list = json.loads(response)  # 将返回的JSON数据转化为Python能识别的
    return domain_list

def get_local_ipv6():
    import socket
    try:
        s = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        s.connect(('2400:da00:2::29', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return str(ip)


def ddns_ipv6(sub_domain_ipv6):
    logger.debug(f'ddns_ipv6 with sub_domain_ipv6 = {sub_domain_ipv6}')

    ipv6 = get_local_ipv6()
    logger.info("获取到本机IPv6地址：%s" % ipv6)

    domain_list = ali_get(domain, sub_domain_ipv6, 'AAAA')
    if domain_list['TotalCount'] == 0:
        logger.info('没有查到阿里子域名记录，开始新增...')
        ali_add(domain, sub_domain_ipv6, "AAAA", ipv6)
        logger.info("新建域名解析成功")
    elif domain_list['TotalCount'] == 1:
        if domain_list['DomainRecords']['Record'][0]['Value'].strip() != ipv6.strip():
            logger.info('查阿里dns，IPv6地址改变，开始更新...')
            ali_update(domain_list['DomainRecords']['Record']
                        [0]['RecordId'], sub_domain_ipv6, "AAAA", ipv6)
            logger.info("修改域名解析成功")
        else:
            logger.info("查阿里dns，IPv6地址没变")
    elif domain_list['TotalCount'] > 1:
        logger.info('查阿里dns，子域名记录超过一个，开始更新...')
        ali_del_subdomain(domain, sub_domain_ipv6, "AAAA")
        ali_add(domain, sub_domain_ipv6, "AAAA", ipv6)
        logger.info("修改域名解析成功")
    logger.info('当前域名解析地址为：%s' % ipv6)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
#                        filename=os.path.join(os.environ['HOME'],'log/aliddns.log'),
#                        filemode='a',
                        )

    logger = logging.getLogger(__name__)
    ddns_ipv6(os.environ.get('SUB_DOMAIN'))

