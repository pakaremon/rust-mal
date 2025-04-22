# Debian can't be used because the public keys for the powershell and kubectl repos
# aren't recognised. Installation fails with 'The following signatures couldn't be
# verified because the public key is not available'
# NO_PUBKEY EB3E94ADBE1229CF [powershell]
# NO_PUBKEY B53DC80D13EDEF05 [kubectl]

# buildpack-deps 22.04 [ubuntu]
FROM buildpack-deps@sha256:d76488a56e1e85930e053b794daa9f990636565bf0de54903d65d93c43c3cad5 AS image

# All intermediate files during first-stage build are stored under /setup
# This directory is removed before second-stage build (i.e. copying runtime files to an empty image)
WORKDIR /setup

# Suppress questions relating to package installs
ENV DEBIAN_FRONTEND=noninteractive
ENV DEBCONF_NOWARNINGS="yes"
ENV K8S_VERSION="v1.29"
ENV NODE_MAJOR=18

# setup repo for kubectl
RUN curl -fsSL "https://pkgs.k8s.io/core:/stable:/${K8S_VERSION}/deb/Release.key" | gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg && \
    echo "deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/${K8S_VERSION}/deb/ /" > /etc/apt/sources.list.d/kubernetes.list

# install repo for nodejs
RUN curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/trusted.gpg.d/nodesource.gpg && \
    echo "deb https://deb.nodesource.com/node_${NODE_MAJOR}.x nodistro main" > /etc/apt/sources.list.d/nodesource.list

# install keys for powershell
RUN curl -fsSL "https://packages.microsoft.com/config/ubuntu/22.04/packages-microsoft-prod.deb" -o /setup/packages-microsoft-prod.deb && \
	dpkg -i /setup/packages-microsoft-prod.deb

# Install runtime packages
RUN apt-get update && apt-get -y upgrade && apt-get install -y --no-install-recommends \
	apt-transport-https \
	auditd \
	awscli \
	build-essential \
	cmake \
	clang \
	dnsutils \
	golang \
	iproute2 \
	iputils-ping \
	kubectl \
	libpng-dev \
	libzip-dev \
	net-tools \
	netcat \
	powershell \
	protobuf-compiler \
	python2 \
	sshpass \
	sudo \
	tcpdump \
	telnet \
	tshark \
	software-properties-common \
	xxd \
	zip \
	openjdk-21-jdk 

# Install Maven
ENV MAVEN_VERSION=3.9.9
ENV MAVEN_HOME=/opt/maven
ENV PATH="${MAVEN_HOME}/bin:${PATH}"

RUN curl -fsSL https://downloads.apache.org/maven/maven-3/${MAVEN_VERSION}/binaries/apache-maven-${MAVEN_VERSION}-bin.tar.gz \
    | tar -xz -C /opt && \
    ln -s /opt/apache-maven-${MAVEN_VERSION} ${MAVEN_HOME}

# Configure sudo
RUN echo "ALL ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers
RUN mkdir -m 0700 /root/.ssh

# PHP setup
WORKDIR /setup/php
RUN apt-get update && apt-get install -y --no-install-recommends \
	php \
	php-zip \
	php-gd

# Composer install
RUN php -r "copy('https://getcomposer.org/installer', 'composer-setup.php');" && \
    php -r "if (hash_file('sha384', 'composer-setup.php') === file_get_contents('https://composer.github.io/installer.sig')) { echo 'Installer verified'; } else { echo 'Installer corrupt'; unlink('composer-setup.php'); } echo PHP_EOL;" && \
    php composer-setup.php --version=2.5.8 && \
    php -r "unlink('composer-setup.php');" && \
    mv composer.phar /usr/local/bin/

# NodeJS setup
WORKDIR /setup/node
RUN apt-get update && apt-get install -y --no-install-recommends \
	nodejs
COPY bowerrc /app/.bowerrc

# Python setup
WORKDIR /setup/python
RUN apt-get update && apt-get install -y --no-install-recommends \
	python3 \
	python3-dev \
	python3-pip
COPY pypi-packages.txt ./
RUN pip install --require-hashes --requirement pypi-packages.txt

# Ruby setup
WORKDIR /setup/ruby
RUN apt-get update && apt-get install -y --no-install-recommends \
	ruby \
	ruby-rubygems

# Rust setup
WORKDIR /setup/rust
RUN apt-get update && apt-get install -y --no-install-recommends \
	rust-all

WORKDIR /app
RUN cargo init
RUN rm -rf /setup

# Second stage build
FROM scratch
COPY --from=image / /
WORKDIR /app

# Rust
ENV PATH="/usr/local/cargo/bin:${PATH}"
ENV RUSTUP_HOME="/usr/local/rustup"
ENV CARGO_HOME="/usr/local/cargo"

# Node
ENV NODE_PATH="/app/node_modules"

# Java + Maven
ENV JAVA_HOME="/usr/lib/jvm/java-21-openjdk-amd64"
ENV MAVEN_HOME="/opt/maven"
ENV PATH="${JAVA_HOME}/bin:${MAVEN_HOME}/bin:${PATH}"
COPY pom.xml /app/pom.xml

# Test installations
RUN ruby --version && php --version && python3 --version && pip --version && node --version && npm --version && rustc --version && cargo --version && java -version && mvn -version

# Analysis scripts
WORKDIR /usr/local/bin/
COPY analyze-php.php .
COPY analyze-node.js .
COPY analyze-python.py .
COPY analyze-ruby.rb .
COPY analyze-rust.py .
COPY analyze-java.py .
RUN chmod 755 analyze-php.php analyze-node.js analyze-python.py analyze-ruby.rb analyze-rust.py analyze-java.py

# Final workdir
WORKDIR /app
ENTRYPOINT [ "sleep" ]
CMD [ "30m" ]
