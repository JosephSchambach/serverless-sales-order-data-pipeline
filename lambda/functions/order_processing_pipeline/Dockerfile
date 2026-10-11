FROM public.ecr.aws/lambda/python:3.14

COPY requirements.txt ${LAMBDA_TASK_ROOT}
COPY helpers.py ${LAMBDA_TASK_ROOT}
COPY process_orders.py ${LAMBDA_TASK_ROOT}

RUN pip install -r requirements.txt

COPY app.py ${LAMBDA_TASK_ROOT}

CMD [ "app.handler" ]