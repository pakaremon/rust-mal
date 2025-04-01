## Installation

### Prerequisites

- Docker
- Linux
- Podman


### Usage: for wolfi-apk analysis



```bash
scripts/run_analysis.sh -ecosystem wolfi -package test -local /path/to/test -sandbox-image 'customised_sandbox_for_dynamic_analysis' -mode dynamic
```
## Development

### Building Docker Images with Podman

To build Docker images using Podman, follow these steps:

1. **Install Podman**: Ensure Podman is installed on your Linux system. You can install Podman using the following commands:

    ```bash
    sudo apt-get update
    sudo apt-get -y install podman
    ```

    For other Linux distributions, refer to the [official Podman installation guide](https://podman.io/getting-started/installation).

2. **Modify Dockerfile to rebuild image** in [`/sandboxes/dynamicanalysis/Dockerfile`](./sandboxes/dynamicanalysis/Dockerfile)

3. **Sync Sandbox Image**: Run the following command to rebuild the image using Docker and then build the sandbox image from Docker to Podman:

    ```bash
    $ make sync/sandbox/dynamic_analysis
    ```


    This command will rebuild the image using Docker and then build the sandbox image from Docker to Podman.
![{724718B7-84C7-4D15-A9C8-204A808972E4}](https://github.com/user-attachments/assets/150ba477-4d84-4b25-9860-759bdf6d4210)

4. **Rebuild Outer Image for Analysis**

To rebuild the outer image for analysis, execute the following command:

```bash
make build/image/analysis
```

This command will recompile the outer container image used for analysis.

5. **Run Analysis**: To use locally built sandbox images for analysis, pass the `-nopull` option to `scripts/run_analysis.sh`:

    ```bash
    ./scripts/run_analysis.sh -ecosystem wolfi -package fijiwashere -version fijiwashere.0.0.0  -local /path/fijiwashere12323-0.0.0-r0.apk -sandbox-image 'wolfi-apk/dynamic-analysis'   -analysis-command 'analyze_wolfi_apk.py' -mode dynamic -nopull  
    ```
    - `-ecosystem`: This option is optional. Default is `wolfi`.
    - `-local`: Use local Wolfi APK files.
    - `-sandbox-image`: Override the default analysis image.
    - `-analysis-command`: Override the default analysis script. The default command is `analyze_wolfi_apk.py`.
    - `-mode dynamic`: Execute only the dynamic analysis phase.
    - `-nopull`: Ensure package-analysis uses the local image.

### Resolving Line Ending Issues when build docker image.

If you encounter issues with line endings, you can use `dos2unix` to convert files to Unix format. To install `dos2unix`, use the following command:

```bash
sudo apt-get install dos2unix
```

To convert a file, use the following command:

```bash
dos2unix /path/to/your/file
```