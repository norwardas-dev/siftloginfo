# syntax=docker/dockerfile:1

FROM python:3.12-slim AS build
WORKDIR /src
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
RUN pip wheel --no-deps --wheel-dir /wheels .

FROM python:3.12-slim
RUN useradd --create-home --shell /usr/sbin/nologin logsift
COPY --from=build /wheels /wheels
RUN pip install --no-cache-dir /wheels/*.whl && rm -rf /wheels
USER logsift
WORKDIR /logs
ENTRYPOINT ["logsift"]
CMD ["--help"]
