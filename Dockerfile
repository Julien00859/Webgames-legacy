FROM python:3.6
ADD . /webgames
RUN pip install git+https://github.com/channelcat/sanic.git
RUN pip install $(cat /webgames/requirements.txt | grep -v sanic=)
WORKDIR /webgames
EXPOSE 50898
CMD ["python", "start.py"]
