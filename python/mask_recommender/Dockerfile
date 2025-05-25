FROM public.ecr.aws/lambda/python:3.12

# Copy requirements.txt
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Install the specified packages
RUN pip install -r requirements.txt

COPY .breathesafe
RUN source ${LAMBDA_TASK_ROOT}/.breathesafe

# Copy function code
COPY fit_testing.py ${LAMBDA_TASK_ROOT}
COPY recommender.py ${LAMBDA_TASK_ROOT}

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "lambda_function.handler" ]
