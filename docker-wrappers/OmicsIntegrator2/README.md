# Omics Integrator 2 Docker image

A Docker image for [Omics Integrator 2](https://github.com/fraenkel-lab/OmicsIntegrator2) that is available on [DockerHub](https://hub.docker.com/repository/docker/reedcompbio/omics-integrator-2).

## Activating conda inside a Docker container

By default, an installed conda environment will not be activated inside the Docker container.
Docker does not invoke Bash as a login shell.
[This blog post](https://pythonspeed.com/articles/activate-conda-dockerfile/) provides a workaround demonstrated here in `Dockerfile` and `env.yml`.
It defines a custom ENTRYPOINT that uses `conda run` to run the command inside the conda environment.

To create the Docker image run:
```
docker build -t reedcompbio/omics-integrator-2 -f Dockerfile .
```
from this directory.

To confirm that commands are run inside the conda environment run:
```
winpty docker run reedcompbio/omics-integrator-2 conda list
winpty docker run reedcompbio/omics-integrator-2 OmicsIntegrator -h
```
The `winpty` prefix is only needed on Windows.

## Testing
Test code is located in `test/OmicsIntegrator2`.
The `input` subdirectory contains test files `oi2-edges.txt` and `oi2-prizes.txt`.
The Docker wrapper can be tested with `pytest`.

## TODO
- Attribute https://github.com/fraenkel-lab/OmicsIntegrator2
- Modify environment to use fraenkel-lab or [PyPI](https://pypi.org/project/OmicsIntegrator/) version instead of fork
- Document usage
- Consider `continuumio/miniconda3:4.9.2-alpine` base image