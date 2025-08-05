FROM mambaorg/micromamba:1.5.8

# Set environment variables for micromamba
ENV MAMBA_DOCKERFILE_ACTIVATE=1

# Create environment and install packages
RUN micromamba install -y -n base -c conda-forge python=3.11 pymc jax jaxlib numpyro arviz pandas requests matplotlib scikit-learn

WORKDIR /workspace
COPY . /workspace

CMD ["python", "python/mask_recommender/training/train.py"]
