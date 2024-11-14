FROM amazonlinux:2023

RUN dnf install -y git tar gcc wget \
    zlib-devel bzip2-devel readline-devel \
    sqlite sqlite-devel openssl-devel \
    tk-devel libffi-devel xz-devel

RUN curl https://pyenv.run | bash && \
    echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc && \
    echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc && \
    echo 'eval "$(pyenv init -)"' >> ~/.bashrc && \
    source ~/.bashrc && \
    pyenv install 3.12.7 && \
    pyenv global 3.12.7

RUN wget https://bootstrap.pypa.io/get-pip.py && \
    python3 get-pip.py && \
    pip3 install -U pip

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt
COPY ./main.py /code/main.py
COPY ./app/ /code/app/

RUN pip3 install --no-cache-dir --upgrade -r /code/requirements.txt

ENV PYTHONPATH="$PYTHONPATH:/code/app"

CMD ["fastapi", "run", "main.py", "--port", "8080"]