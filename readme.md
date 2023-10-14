# Local

## Docker 
```sh
# build images
docker-compose build

# run images
docker run -d --name sut-without-ldpreload -p 8080:8080 benchmark-system-under-test
docker run -d --name sut-with-ldpreload -p 8081:8081 -e SERVER_PORT='8081' -e LD_PRELOAD='//opt/ldpreload.so' benchmark-system-under-test

docker run -d --name test-bench -p 8089:8089  benchmark-test-bench

# Conducting a test run:
# - connect to localhost:8089 inside your browser
# - Let user number and spawn rate by one and select the host accordingly:
#   * "http://host.docker.internal:8080" for running the test on the container without the LD_PRELOAD variable set
#   * "http://host.docker.internal:8081" for running the test on the container with the LD_PRELOAD variable set

# Results can be found inside the benchmark-test-bench container in the /opt/locust/cvs_exports folder.
```

## Local Docker-Compose
```sh
docker-compose build
docker-compose up
```

## Kind
```sh
# create cluster and namespace and mount ./benchmark/jupyter-notebooks/data mounted for
# automatically extracting .csv data later at the benchmarks
kind create cluster --name ldpreload --config ./k8s-manifests/kind/cluster-config.yaml
kubectl create namespace ldpreload

# build and push images to registry
docker-compose build
kind load docker-image -n ldpreload benchmark-system-under-test benchmark-test-bench

# deploy test bench and system under test within a single pod
kubectl apply -n ldpreload -f ./k8s-manifests/base/same-pod/deployment.yaml

# port forward locust for executing the test
kubectl port-forward -n ldpreload service/benchmark 8089:8089 

# Conducting a test run:
# - connect to localhost:8089 inside your browser
# - Let user number and spawn rate by one and select the host accordingly:
#   * "http://localhost:8080/" for running the test on the container without the LD_PRELOAD variable set
#   * "http://localhost:8081/" for running the test on the container with the LD_PRELOAD variable set

# Results can be found inside the benchmark-test-bench container in the /opt/locust/cvs_exports folder.

``` 

## Multiple Node Deployment 
Deploying in two different nodes is not possible locally, without using two different clusters.


# AWS

## Prerequisite:
* Existing Cluster
  * For deploying to multiple nodes the cluster also have to contain multiple nodes
* For AWS: pushed images to the Register (take a look at [Build](#build))



## AWS Build
```sh
# Update kubeconfig if not already done
aws eks update-kubeconfig --name ${CLUSTER_NAME} --region ${REGION}

# Login into the container registry (ECR) 
aws ecr get-login-password --region ${REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com

# Create repositories for the image
aws ecr create-repository --repository-name benchmark-system-under-test
aws ecr create-repository --repository-name benchmark-test-bench

# Build the images locally 
docker-compose build

# Push them to ECR 
docker tag benchmark-system-under-test ${AWS_ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/benchmark-system-under-test:test
docker tag benchmark-test-bench ${AWS_ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/benchmark-test-bench
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/benchmark-system-under-test
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/benchmark-test-bench

```

## Single Pod Deployment 
```sh
# Generate namespace 
kubectl create namespace ldpreload

# Create deployment a deployment file for you AWS cluster (deployment file = ${DEPLOYMENT_PATH}-specific.yaml).
# The `sed` command is used to replacing the "${REPOSITORY_URL}" string inside ${DEPLOYMENT_PATH}.
# This is to made to not have to patch service account for pull rights. 
export DEPLOYMENT_PATH=./k8s-manifests/base/same-pod/deployment-aws.yaml
sed -e 's@${REPOSITORY_URL}@'"${AWS_ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com"'@g' < $DEPLOYMENT_PATH \
    > ${DEPLOYMENT_PATH}-specific.yaml

# Deploy  
kubectl apply -n ldpreload -f ${DEPLOYMENT_PATH}-specific.yaml

# Port forward test bench
kubectl port-forward -n ldpreload service/benchmark 8089:8089 

# Conducting a test run:
# - connect to localhost:8089 inside your browser
# - Let user number and spawn rate by one and select the host accordingly:
#   * "http://localhost:8080/" for running the test on the container without the LD_PRELOAD variable set
#   * "http://localhost:8081/" for running the test on the container with the LD_PRELOAD variable set

# Copy the test results to the jupyter-notbooks data folder.
kubectl get pods -o name -n ldpreload
kubectl cp -c benchmark-test-bench ldpreload/${POD_NAME}:/opt/locust/cvs_exports ./benchmarkjupyter-notebooks/data
```

## Multiple Node Deployment 
```sh
# Get and select nodes
kubectl get nodes
export NODE_HOSTNAME_1=<your-first-cluster-host-name>
export NODE_HOSTNAME_2=<your-second-cluster-host-name>

# Generate sut namespace 
kubectl create namespace ldpreload

# Create deployment a deployment file for you AWS cluster (deployment file = ${DEPLOYMENT_PATH}-specific.yaml).
# The `sed` command is used to replacing the "${REPOSITORY_URL}" string inside ${DEPLOYMENT_PATH}.
# This is to made to not have to patch service account for pull rights. 
export DEPLOYMENT_PATH_SUT=./k8s-manifests/base/different-pods/deployment-aws-sut.yaml
export DEPLOYMENT_PATH_TB=./k8s-manifests/base/different-pods/deployment-aws-tb.yaml

sed -e 's@${REPOSITORY_URL}@'"${AWS_ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com"'@g' < $DEPLOYMENT_PATH_SUT \
    > ${DEPLOYMENT_PATH_SUT}-specific.yaml
sed -e 's@${HOSTNAME}@'"${NODE_HOSTNAME_1}"'@g' < ${DEPLOYMENT_PATH_SUT}-specific.yaml \
    > ${DEPLOYMENT_PATH_SUT}-specific2.yaml

sed -e 's@${REPOSITORY_URL}@'"${AWS_ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com"'@g' < $DEPLOYMENT_PATH_TB \
    > ${DEPLOYMENT_PATH_TB}-specific.yaml
sed -e 's@${HOSTNAME}@'"${NODE_HOSTNAME_2}"'@g' < $DEPLOYMENT_PATH_TB-specific.yaml  \
    > ${DEPLOYMENT_PATH_TB}-specific2.yaml

# Deploy  
kubectl apply -n ldpreload -f ${DEPLOYMENT_PATH_SUT}-specific2.yaml
kubectl apply -n ldpreload -f ${DEPLOYMENT_PATH_TB}-specific2.yaml

# Port forward test bench
kubectl port-forward service/benchmark-test-bench-nodes 8089:8089 

# Conducting a test run:
# - connect to localhost:8089 inside your browser
# - Let user number and spawn rate by one and select the host accordingly:
#   * "http://benchmark-sut-nodes:8080" for running the test on the container without the LD_PRELOAD variable set
#   * "http://benchmark-sut-nodes:8081" for running the test on the container with the LD_PRELOAD variable set

# Results can be found inside the benchmark-test-bench container in the /opt/locust/cvs_exports folder.

```