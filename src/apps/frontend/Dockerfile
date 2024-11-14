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

WORKDIR /frontend

COPY ./requirements.txt /frontend/requirements.txt
COPY ./images/ /frontend/images/
COPY ./app/ /frontend/app/

RUN pip3 install --no-cache-dir --upgrade -r requirements.txt

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "app/Home.py", "--server.port=8501", "--server.address=0.0.0.0"]