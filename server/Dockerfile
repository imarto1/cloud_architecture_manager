FROM docker:27-cli AS docker_cli


FROM python:3.12-slim AS builder

ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv "${VIRTUAL_ENV}"
ENV PATH="${VIRTUAL_ENV}/bin:${PATH}"

WORKDIR /build

COPY aws_parser ./aws_parser
COPY aws_parser_mocks ./aws_parser_mocks
COPY server/requirements.txt ./server/requirements.txt

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir \
        ./aws_parser \
        ./aws_parser_mocks \
        -r server/requirements.txt


FROM python:3.12-slim AS runtime

COPY --from=docker_cli /usr/local/bin/docker /usr/local/bin/docker
COPY --from=docker_cli /usr/local/libexec/docker/cli-plugins \
    /usr/local/libexec/docker/cli-plugins
COPY --from=builder /opt/venv /opt/venv

ENV PATH="/opt/venv/bin:${PATH}" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    SERVER_HOST=0.0.0.0 \
    SERVER_PORT=8000

WORKDIR /app
COPY server ./server

EXPOSE 8000

CMD ["python", "-m", "server.docker_entrypoint"]
