FROM public.ecr.aws/lambda/python:3.12

# Copy requirements and install deps
COPY python/mask_recommender/pytorch/requirements.txt ${LAMBDA_TASK_ROOT}/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy package code into Lambda task root
COPY python/mask_recommender/pytorch ${LAMBDA_TASK_ROOT}/python/mask_recommender/pytorch

# Environment defaults (can be overridden at deploy time)
ENV ENVIRONMENT=staging
ENV S3_BUCKET_REGION=us-east-2

# Set handler
CMD [ "python/mask_recommender/pytorch/lambda_function.handler" ]
