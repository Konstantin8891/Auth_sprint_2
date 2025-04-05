# FROM python:3.13-bookworm
#
# WORKDIR /app
#
# COPY requirements.txt .
#
# RUN pip install -r requirements.txt --no-cache-dir
#
# COPY . .
#
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

FROM python:3.13-bookworm AS builderstage

RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
	PATH=/home/user/.local/bin:$PATH
COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir

FROM python:3.13-bookworm AS runtime
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
	PATH=/home/user/.local/bin:$PATH
ENV HOME=/home/user \
	PATH=/home/user/.local/bin:$PATH
	# Make sure scripts in .local are usable:
COPY --from=builderstage /home/user/.local /home/user/.local

WORKDIR $HOME/app
COPY --chown=user . $HOME/app
RUN chown -R user:user $HOME/app
RUN chmod -R 755 $HOME/app

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
