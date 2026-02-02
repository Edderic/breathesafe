FROM public.ecr.aws/lambda/python:3.12

# Copy requirements.txt
COPY requirements.txt ${LAMBDA_TASK_ROOT}/requirements.txt

# Install dependencies for inference + training.
RUN pip install --no-cache-dir -r requirements.txt

# Copy function code + shared modules.
COPY . ${LAMBDA_TASK_ROOT}

# Set the CMD to your handler
CMD [ "lambda_function.handler" ]
