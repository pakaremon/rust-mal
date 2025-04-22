## Installation

### Prerequisites

- Docker
- Linux
- Podman

### Usage: Wolfi-APK Analysis

To analyze Wolfi-APK packages, use the following command:

```bash
scripts/run_analysis.sh -ecosystem wolfi -package test -local /path/to/test -sandbox-image 'customised_sandbox_for_dynamic_analysis' -mode dynamic
```

### Development

#### Building Docker Images with Podman

1. **Install Podman**: Ensure Podman is installed on your Linux system. Install it using:

    ```bash
    sudo apt-get update
    sudo apt-get -y install podman
    ```

    For other distributions, refer to the [Podman installation guide](https://podman.io/getting-started/installation).

2. **Modify Dockerfile**: Update the Dockerfile located at [`/sandboxes/dynamicanalysis/Dockerfile`](./sandboxes/dynamicanalysis/Dockerfile) as needed.

3. **Sync Sandbox Image**: Rebuild the image using Docker and sync it to Podman:

    ```bash
    make sync/sandbox/dynamic_analysis
    ```

4. **Rebuild Outer Image**: Recompile the outer container image for analysis:

    ```bash
    make build/image/analysis
    ```

5. **Run Analysis**: Use locally built sandbox images by adding the `-nopull` option:

    ```bash
    ./scripts/run_analysis.sh -ecosystem wolfi -package fijiwashere -version fijiwashere.0.0.0 -local /path/fijiwashere12323-0.0.0-r0.apk -sandbox-image 'wolfi-apk/dynamic-analysis' -analysis-command 'analyze_wolfi_apk.py' -mode dynamic -nopull
    ```

    - `-ecosystem`: Optional, defaults to `wolfi`.
    - `-local`: Use local Wolfi APK files.
    - `-sandbox-image`: Override the default analysis image.
    - `-analysis-command`: Override the default analysis script (`analyze_wolfi_apk.py`).
    - `-mode dynamic`: Execute only the dynamic analysis phase.
    - `-nopull`: Use the local image.

### Resolving Line Ending Issues

If you encounter line ending issues, convert files to Unix format using `dos2unix`:

```bash
sudo apt-get install dos2unix
dos2unix /path/to/your/file
```

### Configuration

- Docker
- Web
- Python

### Install OSS-Find-Squat

1. Install [`Oss-gadget v0.1.422`](https://github.com/microsoft/OSSGadget/releases/download/v0.1.422/OSSGadget_linux_0.1.422.tar.gz).
2. [`Extract and build docker`](https://github.com/microsoft/OSSGadget/wiki/Docker-Image)
3. Build a Docker image for microservice usage.


### Static analysis
- Bandit4mal
- VirusTotal
- OSS-detect-backdoor




<<<<<<< HEAD
=======
```bash
dos2unix /path/to/your/file
```

To convert all files in a specific folder
```bash
find path/sample_folder -type f -exec dos2unix {} \;
```
>>>>>>> 4f65f7d23b0ff93293539044235eb96e964cd9eb
