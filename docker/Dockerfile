ARG PYTHON_VERSION=3.12
# IMPORTANT: This image was built manually from Dockerfile.base_image
FROM orderry/python:$PYTHON_VERSION-ubuntu-deadsnakes AS base

ARG PYTHON_VERSION
ENV APPROOT=/opt/app
ENV VIRTUAL_ENV=/opt/.venv
ENV PATH=$VIRTUAL_ENV/bin:$PATH
ENV PYTHONPATH=$VIRTUAL_ENV/lib/python$PYTHON_VERSION/site-packages:

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never

WORKDIR $APPROOT

# Install dependencies
COPY Pipfile.lock .
RUN --mount=type=cache,mode=0777,id=dot_cache,target=/root/.cache \
    --mount=from=ghcr.io/astral-sh/uv,source=/uv,target=/bin/uv \
    apt-get update && apt-get -y upgrade \
    && uv venv --seed $VIRTUAL_ENV \
    && pipenv requirements --exclude-markers | xargs uv pip install \
    && apt-get -y autoremove; apt-get autoclean; rm -rf /var/lib/apt/lists/*

FROM base AS tests

RUN --mount=type=cache,mode=0777,id=dot_cache,target=/root/.cache \
    --mount=from=ghcr.io/astral-sh/uv,source=/uv,target=/bin/uv \
    pipenv requirements --dev --exclude-markers | xargs uv pip install

FROM base AS prod

COPY . .

ARG GIT_VERSION
ARG DJANGO_SETTINGS_MODULE=remonline.settings.build_settings
# Create version metadata and Generate translations and compile .pycg
RUN python3 make_meta.py $GIT_VERSION \
    && python -m compileall -q . ||:

CMD ["make", "run"]
