FROM python:3.9-alpine
LABEL MAINTAINER MuGu <94156510@qq.com>

RUN set -evu; \
    apk add --no-cache gcc musl-dev libffi-dev; \
    pip3 install aliyun-python-sdk-core-v3 -i https://mirrors.aliyun.com/pypi/simple; \
    pip3 install aliyun-python-sdk-domain -i https://mirrors.aliyun.com/pypi/simple; \
    pip3 install aliyun-python-sdk-alidns -i https://mirrors.aliyun.com/pypi/simple; \
    pip3 install requests -i https://mirrors.aliyun.com/pypi/simple; \
    apk del gcc musl-dev libffi-dev; \
    echo "*/30 * * * * python /home/aliddns.py" > /var/spool/cron/crontabs/root;

COPY aliddns.py /home/

CMD python /home/aliddns.py && busybox crond -f -L /dev/stdout

