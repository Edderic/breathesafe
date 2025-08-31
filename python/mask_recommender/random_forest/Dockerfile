FROM public.ecr.aws/lambda/python:3.12

# Copy requirements and install deps
# Build context is python/mask_recommender
COPY random_forest/requirements.txt ${LAMBDA_TASK_ROOT}/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy only the random_forest package into Lambda task root
COPY random_forest ${LAMBDA_TASK_ROOT}/python/mask_recommender/random_forest

# Set handler
CMD [ "python/mask_recommender/random_forest/lambda_function.handler" ]
