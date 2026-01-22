FROM public.ecr.aws/lambda/python:3.12

# Copy requirements.txt
COPY inference/requirements.txt ${LAMBDA_TASK_ROOT}/requirements.txt

# Install the specified packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy function code
COPY inference/lambda_function.py ${LAMBDA_TASK_ROOT}/lambda_function.py
COPY feature_builder.py ${LAMBDA_TASK_ROOT}/feature_builder.py

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "lambda_function.handler" ]
