# Benchmarking Function Hook Latency in Cloud-Native Environments

This repository contains the source code for the paper 📜 [Benchmarking Function Hook Latency in Cloud-Native Environments](https://arxiv.org/#)
which we published at the 14th Symposium on Software Performance (SSP) in 2023.

> **Note**
> This project is not officially supported by Dynatrace.

The repository is structured as follows:

- [`/benchmark`](./benchmark/) contains the Locust load generator, the system under test (SUT), and the Kubernetes manifests for deploying them
- [`/hook`](./hook/) contains the source code of the function hook (and a pre-built binary) that we inject into the SUT
- [`/results`](./results/) contains the data from our experiment, and a Jupyter notebook to analyze and visualize it

If you are only interested in the raw data from our experiments, look into the [`/results/data`](./results/data) directory.

## Recommendations from the paper

Besides following [**empirical standards for software benchmarking**](https://www2.sigsoft.org/EmpiricalStandards/docs/?standard=Benchmarking) (Ralph et al., 2021)
and [**methodological principles for performance evaluation in cloud computing**](https://doi.org/10.1109/TSE.2019.2927908) (Papadopoulos et al., 2019),
we recommend researchers and engineers who benchmark function hook latency in cloud-native environments to also consider the following recommendations:

1. Place the load generator and the system under test in separate containers, but within the same pod.
2. If that is not possible, at least ensure that both pods are deployed on the same physical node.
3. Weigh the benefits of introducing a service mesh against its additional network overhead.
4. Generally avoid benchmarking in multi-tenancy clusters.
5. Place the monitoring tool as close as possible to the layer where the hook is injected.
6. Describe if the benchmark measures the specific hooking overhead in isolation (micro benchmark) or represents a real-world application with a hook injected into it (macro benchmark).
7. Describe how the hooked function is typically used by applications.
8. Ensure that your servers do not hit any resource limits during the experiment.
9. Use a high number of repetitions to regain statistical power over the high variance that cloud-native environments introduce.
10. Conduct experiments in differently configured environments.

💬 If you have suggestions on how to improve these recommendations, please let us know by opening an issue or a pull request.

## Citation

If this is useful for your work, please cite us as follows:

```bibtex
@inproceedings{Kahlhofer2023:BenchmarkingFunctionHookLatency,
  title = {Benchmarking {{Function Hook Latency}} in {{Cloud-Native Environments}}},
  author = {Kahlhofer, Mario and Kern, Patrick and Henning, Sören and Rass, Stefan},
  booktitle = {14th {{Symposium}} on {{Software Performance}}},
  series = {{{SSP}} '23},
  date = {2023-11-07},
  location = {{Karlsruhe, Germany}}
  publisher = {{Gesellschaft für Informatik e.V.}},
}
```

## Demonstration

In the following, we demonstrate how to reproduce the experiments of our paper.
As a prerequisite, you will need to install the following tools:

- [Docker](https://docs.docker.com/get-docker/) for running containers locally
- [Kind](https://kind.sigs.k8s.io/) for running Kubernetes clusters locally
- [kubectl](https://kubernetes.io/docs/tasks/tools/) for interacting with Kubernetes clusters
- _(optional, for AWS)_ An [AWS](https://aws.amazon.com/) account for running experiments in [EKS](https://aws.amazon.com/eks/)
- _(optional, for AWS)_ The [AWS CLI](https://aws.amazon.com/cli/) for interacting with AWS

### Building the function hook

This repository already includes a **pre-built version of the function hook in [`/hook/out/readhook.so`](`/hook/out/readhook.so`)** making this step optional.
For building, we use a rather old `gcc:7.5.0` image so that we build the hook against an older version of the C standard library (GLIBC 2.28).
This way, we have greater backwards compatibility with applications that use older versions of the C standard library.

In Bash, to build the hook in a container and copy it to the host system, run:

```sh
cd hook
docker build -t readhook .
id=$(docker create readhook)
docker cp $id:/out/readhook.so ./out/readhook.so
docker rm -v $id
```

In PowerShell, to build the hook in a container and copy it to the host system, run:

```sh
cd hook
docker build -t readhook .
$Id = docker create readhook
docker cp "$($Id):/out/readhook.so" ./out/readhook.so
docker rm -v $Id
```

### 🐋 Experiment 1: Docker

We prepared a `docker-compose.yaml` file that sets up the following:

- Container for the SUT, on port `8080`
- Container for the SUT, with `LD_PRELOAD=/opt/hook/readhook.so` set, mounted from `/hook/out` in this repository, on port `8081`
- Container for the Locust load generator, with `/benchmark/benchmark_results` mounted into this repository, on port `8089`

First, let Compose build and start the containers:

```sh
cd benchmark
docker compose up -d
```

Then, browse to [http://localhost:8089](http://localhost:8089) and start two benchmarks:

- One with the host `http://host.docker.internal:8080` (no trailing slash) to test the SUT without the hook
- One with the host `http://host.docker.internal:8081` (no trailing slash) to test the SUT with the hook

Results will be placed into `/tmp/benchmark_results` in the Locust container, which is mounted locally to `./benchmark/benchmark_results`.

To clean up again, run:

```sh
docker compose down
```

### 🛳️ Experiment 2: Kind

First, create a Kind cluster with our `kind-cluster-config.yaml` that also mounts some host paths:

```sh
cd benchmark
kind create cluster --name benchmark --config ./k8s-manifests/kind-cluster-config.yaml
kubectl create namespace benchmark
```

Then, build and push the images to the Kind cluster with the help of Compose (this may take some time):

```sh
docker compose build
kind load docker-image -n benchmark system-under-test system-under-test
kind load docker-image -n benchmark test-bench test-bench
```

Next, apply a `Deployment` and `Service` resource in that cluster, wait for it, and port-forward the Locust UI:

```sh
kubectl apply -n benchmark -f ./k8s-manifests/kind-single-pod.yaml
kubectl rollout status deployment tb-single-pod -n benchmark --timeout=60s
kubectl port-forward -n benchmark service/locust 8089:8089
```

Then, browse to [http://localhost:8089](http://localhost:8089) and start two benchmarks:

- One with the host `http://localhost:8080` (no trailing slash) to test the SUT without the hook
- One with the host `http://localhost:8081` (no trailing slash) to test the SUT with the hook

Results will be placed into `/tmp/benchmark_results` in the Locust container, which is mounted locally to `./benchmark/benchmark_results`.

To clean up again, run:

```sh
kind delete cluster --name benchmark
```

### Prerequisites for experiments in AWS EKS

For experiment 3 and 4, we presume that your AWS EKS cluster is already set up and that you have `kubectl` configured to talk to it.
Typically, this can be done with the AWS CLI, like so:

```sh
aws eks update-kubeconfig --name ${CLUSTER_NAME} --region ${REGION}
```

We need to push our container images into AWS ECR. First, login into the container registry (ECR):

```sh
aws ecr get-login-password --region ${REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com
```

Next, create repositories for the images:

```sh
aws ecr create-repository --repository-name system-under-test
aws ecr create-repository --repository-name test-bench
aws ecr create-repository --repository-name readhook
```

Then, build the images locally (also the scratch `readhook` container), tag them, and push them to ECR:

```sh
cd benchmark
docker compose --profile with-readhook build
docker tag system-under-test ${AWS_ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/system-under-test
docker tag test-bench ${AWS_ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/test-bench
docker tag readhook ${AWS_ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/readhook
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/system-under-test
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/test-bench
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/readhook
```

Note that we have a special `readhook` container image which just contains the `/out/readhook.so` file so that we can mount it without volume claims.

### ⚓ Experiment 3: AWS EKS with SUT and load generator in a single pod

_Before continuing, make sure that you read the prerequisites for experiments in AWS EKS from before._

Let's start by creating a namespace for our benchmark:

```sh
kubectl create namespace benchmark
```

Then, we take the `aws-single-pod.template.yaml` manifest and need to change the `REPOSITORY_URL` variable and deploy it.
If you use Windows, change this value manually in the file. With Bash, you can use the following command:

```sh
cd benchmark
export AWS_ACCOUNT_ID=YOUR_AWS_ACCOUNT_ID
export REGION=YOUR_AWS_REGION
cat ./k8s-manifests/aws-single-pod.template.yaml \
  | sed -e 's@${REPOSITORY_URL}@'"${AWS_ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com"'@g' \
  | kubectl apply -n benchmark -f -
```

Next, wait for the deployment and then port-forward the Locust UI locally:

```sh
kubectl rollout status deployment tb-single-pod -n benchmark --timeout=60s
kubectl port-forward -n benchmark service/locust 8089:8089
```

Then, browse to [http://localhost:8089](http://localhost:8089) and start two benchmarks:

- One with the host `http://localhost:8080` (no trailing slash) to test the SUT without the hook
- One with the host `http://localhost:8081` (no trailing slash) to test the SUT with the hook

Results will be placed into `/tmp/benchmark_results` in the Locust container. We need to copy this manually to our local machine.

In Bash, run the following:

```sh
podname=$(kubectl get pods -n benchmark --selector=app.kubernetes.io/name=tb-single-pod --no-headers -o custom-columns=":metadata.name")
kubectl cp -c test-bench "benchmark/$($PodName):/tmp/benchmark_results" ./benchmark_results
```

In PowerShell, run the following:

```sh
$PodName = kubectl get pods -n benchmark --selector=app.kubernetes.io/name=tb-single-pod --no-headers -o custom-columns=":metadata.name"
kubectl cp -c test-bench "benchmark/$($PodName):/tmp/benchmark_results" ./benchmark_results
```

To clean up again, run:

```sh
kubectl delete all --all -n benchmark
```

### 🔱 Experiment 4: AWS EKS with SUT and load generator in separate pods, each pod on a different node

_Before continuing, make sure that you read the prerequisites for experiments in AWS EKS from before._

Let's start by creating a namespace for our benchmark:

```sh
kubectl create namespace benchmark
```

We need to note down the hostnames of at least two different nodes in our cluster:

```sh
kubectl get nodes --no-headers -o custom-columns=":metadata.name"
export NODE_HOSTNAME_FOR_LOCUST=MANUALLY_COPY_THE_FIRST_HOSTNAME_FROM_ABOVE
export NODE_HOSTNAME_FOR_SUT=MANUALLY_COPY_THE_SECOND_HOSTNAME_FROM_ABOVE
```

Then, we take the `aws-different-nodes.template.yaml` manifest and need to change the `REPOSITORY_URL`, `NODE_HOSTNAME_FOR_LOCUST`, and `NODE_HOSTNAME_FOR_SUT` variables and deploy it.
If you use Windows, change these values manually in the file. With Bash, you can use the following command:

```sh
cd benchmark
export AWS_ACCOUNT_ID=YOUR_AWS_ACCOUNT_ID
export REGION=YOUR_AWS_REGION
cat ./k8s-manifests/aws-different-nodes.template.yaml \
  | sed -e 's@${REPOSITORY_URL}@'"${AWS_ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com"'@g' \
  | sed -e 's@${NODE_HOSTNAME_FOR_LOCUST}@'"${NODE_HOSTNAME_FOR_LOCUST}"'@g' \
  | sed -e 's@${NODE_HOSTNAME_FOR_SUT}@'"${NODE_HOSTNAME_FOR_SUT}"'@g' \
  | kubectl apply -n benchmark -f -
```

Next, wait for the deployment and then port-forward the Locust UI locally:

```sh
kubectl rollout status deployment tb-locust-node -n benchmark --timeout=60s
kubectl port-forward -n benchmark service/locust 8089:8089
```

Then, browse to [http://localhost:8089](http://localhost:8089) and start two benchmarks:

- One with the host `http://sut.benchmark.svc.cluster.local:8080` (no trailing slash) to test the SUT without the hook
- One with the host `http://sut.benchmark.svc.cluster.local:8081` (no trailing slash) to test the SUT with the hook

Results will be placed into `/tmp/benchmark_results` in the Locust container. We need to copy this manually to our local machine.

In Bash, run the following:

```sh
podname=$(kubectl get pods -n benchmark --selector=app.kubernetes.io/name=tb-locust-node --no-headers -o custom-columns=":metadata.name")
kubectl cp -c test-bench "benchmark/$($PodName):/tmp/benchmark_results" ./benchmark_results
```

In PowerShell, run the following:

```sh
$PodName = kubectl get pods -n benchmark --selector=app.kubernetes.io/name=tb-locust-node --no-headers -o custom-columns=":metadata.name"
kubectl cp -c test-bench "benchmark/$($PodName):/tmp/benchmark_results" ./benchmark_results
```

To clean up again, run:

```sh
kubectl delete all --all -n benchmark
```
