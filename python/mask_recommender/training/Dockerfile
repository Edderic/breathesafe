FROM public.ecr.aws/lambda/python:3.12

# Copy requirements.txt
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Install the specified packages
# Install the specified packages; prefer binary wheels to reduce build time
RUN pip install --no-cache-dir -r requirements.txt

# Copy function code
COPY lambda_function.py ${LAMBDA_TASK_ROOT}
COPY train.py ${LAMBDA_TASK_ROOT}
COPY run_tests.py ${LAMBDA_TASK_ROOT}
COPY fix_jax_environment.py ${LAMBDA_TASK_ROOT}

# Set the CMD to your handler
CMD [ "lambda_function.handler" ]