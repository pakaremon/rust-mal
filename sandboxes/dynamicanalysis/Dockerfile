# Use wolfi-base as the base image
FROM cgr.dev/chainguard/wolfi-base AS image

# All intermediate files during first-stage build are stored under /setup
# This directory is removed before second-stage build (i.e. copying runtime files to an empty image)
WORKDIR /setup

# Install base packages in groups to better handle dependencies
RUN apk update && \
    apk add --no-cache \
    python3 \
    python3-dev \
    py3-pip

# Install Node.js and npm
RUN apk add --no-cache \
    nodejs \
    npm

RUN apk add --no-cache ruby ruby-dev build-base \
 && gem install bundler
 
# Install Rust and Cargo
ENV PATH="/root/.cargo/bin:${PATH}"
# Install Rust and Cargo manually using rustup
RUN apk add --no-cache curl build-base && \
    curl https://sh.rustup.rs -sSf | sh -s -- -y --default-toolchain stable && \
    ln -s /root/.cargo/bin/* /usr/local/bin/

# Install PHP and its extensions
RUN apk add --no-cache \
    php \
    php-openssl \
    php-zip \
    php-gd \
    php-phar \
    php-iconv \
    php-mbstring

# Install Java and Maven
RUN apk add --no-cache \
    openjdk-21 \
    maven

# Create necessary directories
RUN mkdir -p /etc/apk/keyrings /etc/apk/sources.list.d

# Configure sudo for passwordless execution
RUN echo "ALL ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

# Create ssh directory for root
RUN mkdir -m 0700 /root/.ssh

# Python setup
WORKDIR /setup/python
COPY pypi-packages.txt ./
RUN pip install --require-hashes --requirement pypi-packages.txt

# Node.js setup
WORKDIR /setup/node
COPY bowerrc /app/.bowerrc

# Ruby setup
WORKDIR /setup/ruby
RUN gem install bundler

# Rust setup
WORKDIR /setup/rust
RUN cargo init

# PHP setup
WORKDIR /setup/php
RUN php -r "copy('https://getcomposer.org/installer', 'composer-setup.php');" && \
    php -r "if (hash_file('sha384', 'composer-setup.php') === file_get_contents('https://composer.github.io/installer.sig')) { echo 'Installer verified'; } else { echo 'Installer corrupt'; unlink('composer-setup.php'); } echo PHP_EOL;" && \
    php composer-setup.php --version=2.5.8 && \
    php -r "unlink('composer-setup.php');" && \
    mv composer.phar /usr/local/bin/

# Remove setup files
RUN rm -rf /setup

# Second stage build
FROM scratch
COPY --from=image / /
WORKDIR /app

# Set environment variables
ENV PATH="/usr/local/cargo/bin:${PATH}"
ENV RUSTUP_HOME="/usr/local/rustup"
ENV CARGO_HOME="/usr/local/cargo"
ENV NODE_PATH="/app/node_modules"
ENV JAVA_HOME="/usr/lib/jvm/java-21-openjdk"
ENV MAVEN_HOME="/opt/maven"
ENV PATH="${JAVA_HOME}/bin:${MAVEN_HOME}/bin:${PATH}"

# copy pom.xml to /app
COPY pom.xml /app/

# Test installations
RUN ruby --version || echo "Ruby failed"
RUN php --version || echo "PHP failed"
RUN python3 --version || echo "Python failed"
RUN pip --version || echo "Pip failed"
RUN node --version || echo "Node failed"
RUN npm --version || echo "NPM failed"
RUN rustc --version || echo "Rustc failed"
RUN cargo --version || echo "Cargo failed"
RUN java -version || echo "Java failed"
RUN mvn -version || echo "Maven failed"


# Add analysis scripts
WORKDIR /usr/local/bin/
COPY analyze-php.php .
COPY analyze-node.js .
COPY analyze-python.py .
COPY analyze-ruby.rb .
COPY analyze-rust.py .
COPY analyze-java.py .
COPY analyze-wolfi.py .
RUN chmod 755 analyze-php.php analyze-node.js analyze-python.py analyze-ruby.rb analyze-rust.py analyze-java.py analyze-wolfi.py

# Final workdir
WORKDIR /app
ENTRYPOINT [ "sleep" ]
CMD [ "30m" ]