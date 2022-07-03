FROM public.ecr.aws/lambda/python:3.9 AS build-image

RUN  pip3 install --upgrade pip wheel

COPY lib/python/ /build-image/python/lib/

RUN  pip3 install /build-image/python/lib \
       --disable-pip-version-check \
       --no-cache-dir \
       --find-links /build-image/python \
       --target "${LAMBDA_TASK_ROOT}"

RUN ls -l /build-image/python/lib/src

FROM public.ecr.aws/lambda/python:3.9 as base-image

COPY --from=build-image ${LAMBDA_TASK_ROOT} ${LAMBDA_TASK_ROOT}

FROM base-image

ARG FUNCTION_DIR

# Copy function code
COPY ${FUNCTION_DIR}/ ${LAMBDA_TASK_ROOT}/

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "function.handler" ]
