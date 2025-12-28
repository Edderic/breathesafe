# Use AWS Lambda Python base image
FROM public.ecr.aws/lambda/python:3.11

# Copy and install dependencies
COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip3 install --no-cache-dir -r ${LAMBDA_TASK_ROOT}/requirements.txt

# Copy function code
COPY lambda_function.py ${LAMBDA_TASK_ROOT}
COPY crf_model.pkl ${LAMBDA_TASK_ROOT}

# Command can be overwritten by providing a different command in the template directly.
CMD ["lambda_function.lambda_handler"]
