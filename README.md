# Cloud5296 Project Group18

The project has followed the installation guideline from yeshwanthlm to initiate a k8s cluster with AWS EC2 instances. After setting up the cluster, a sample machine learning script has been deployed as a load test to the cluster. On the high level, the script will loop training a simple neural network model and delete it. Then, Horizontal Pod Autoscaling (HPA) is used to autoscale and provide load balancing services to the cluster.

Hence, it empowers the project to load test the cluster and verify if the system aligns with the project goals. The project goals include deploying a ML model on a EC2 cluster, with autoscaling and load balancing. k8s is the perfect tools for the project.

The following guideline outlines the steps needed to set up a Kubernetes cluster using kubeadm. Then setup load balancing and autoscaling services on the cluster.

## Pre-requisites:
* Ubuntu OS (Xenial or later)
* sudo privileges
* AWS Account
* EC2 instances (>= 2GB ram per instance, 2 CPUs for master node/ control plane, 32GB storage for everything)

### Master & Slave Node: 
Run the following commands on both the master and worker nodes to prepare them for kubeadm.

```bash
 curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"

 curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl.sha256"

 echo "$(cat kubectl.sha256)  kubectl" | sha256sum --check

 sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

 chmod +x kubectl
 mkdir -p ~/.local/bin
 mv ./kubectl ~/.local/bin/kubectl
 # and then append (or prepend) ~/.local/bin to $PATH

 kubectl version --client

# disable swap
sudo swapoff -a

# Create the .conf file to load the modules at bootup
cat <<EOF | sudo tee /etc/modules-load.d/k8s.conf
overlay
br_netfilter
EOF

sudo modprobe overlay
sudo modprobe br_netfilter

# sysctl params required by setup, params persist across reboots
cat <<EOF | sudo tee /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-iptables  = 1
net.bridge.bridge-nf-call-ip6tables = 1
net.ipv4.ip_forward                 = 1
EOF

# Apply sysctl params without reboot
sudo sysctl --system

## Install CRIO Runtime
sudo apt-get update -y
sudo apt-get install -y software-properties-common curl apt-transport-https ca-certificates gpg

sudo curl -fsSL https://pkgs.k8s.io/addons:/cri-o:/prerelease:/main/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/cri-o-apt-keyring.gpg
echo "deb [signed-by=/etc/apt/keyrings/cri-o-apt-keyring.gpg] https://pkgs.k8s.io/addons:/cri-o:/prerelease:/main/deb/ /" | sudo tee /etc/apt/sources.list.d/cri-o.list

sudo apt-get update -y
sudo apt-get install -y cri-o

sudo systemctl daemon-reload
sudo systemctl enable crio --now
sudo systemctl start crio.service

echo "CRI runtime installed successfully"

# Add Kubernetes APT repository and install required packages
curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.29/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.29/deb/ /' | sudo tee /etc/apt/sources.list.d/kubernetes.list

sudo apt-get update -y
sudo apt-get install -y kubelet="1.29.0-*" kubectl="1.29.0-*" kubeadm="1.29.0-*"
sudo apt-get update -y
sudo apt-get install -y jq

sudo systemctl enable --now kubelet
sudo systemctl start kubelet

```
### Master Node (Only):
a) Initialize the Kubernetes master node.

```bash
 sudo kubeadm config images pull

 sudo kubeadm init

 mkdir -p "$HOME"/.kube
 sudo cp -i /etc/kubernetes/admin.conf "$HOME"/.kube/config
 sudo chown "$(id -u)":"$(id -g)" "$HOME"/.kube/config

 # Network Plugin = calico
 kubectl apply -f https://raw.githubusercontent.com/projectcalico/calico/v3.26.0/manifests/calico.yaml
```
After succesfully running, your Kubernetes control plane will be initialized successfully.

b) Generate a token for worker nodes to join:

```bash
 kubeadm token create --print-join-command
```

c) Expose port 6443 in the Security group for the Worker to connect to Master Node

### Slave Node (Only):

a) Run the following commands on the worker node.

```bash
sudo kubeadm reset pre-flight checks
```

b) Paste the join command you got from the master node and append --v=5 at the end. Make sure either you are working as sudo user or usesudo before the command

Verify if it is working as expected!

```bash
kubectl get nodes
```

## Full Steps on Configuring the Cluster and Deploying ML Tasks on it
a) Snap is a package manager available on Ubuntu. There are many ways to install docker and snap is only one of them.

```bash
snap install docker
```

b) Then pull the tensorflow image

```bash
docker pull tensorflow/tensorflow:latest
```

c) Verify if the image has been pulled
```bash
docker images
docker run --rm -it tensorflow/tensorflow:latest python -c "import tensorflow as tf; print(tf.__version__)"
```

d) Create configmap for the ML script so that the tensorflow container could use it
```bash
kubectl create configmap tensorflow-script --from-file=train_and_delete.py
```
Verify if the configmap has been created
```bash
kubectl get configmap tensorflow-script -o yaml
```

e) Deploy the Machine learning training script
```bash
kubectl apply -f tensorflow-deployment.yaml
```
Commands for verifying the deployment
```bash
kubectl get pods
kubectl describe pod -l app=tensorflow-training
kubectl logs -l app=tensorflow-training --tail=50
```

e) Expose the deployment as a service
```bash
kubectl apply -f tensorflow-service.yaml
```
Commands for verifying the service
```bash
kubectl get svc
kubectl describe svc tensorflow-service
```

f) Setup HPA for autoscaling and load balancing
```bash
kubectl autoscale deployment tensorflow-training --cpu-percent=50 --min=1 --max=10
```
Commands for verifying the HPA
```bash
kubectl get hpa
kubectl describe hpa tensorflow-training
```
Fof HPA to function properly, we need to install the metrics server, which could monitor CPU utilization of the instaces
```bash
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```
Check [here](### If metrics server is not working) if the metics server is not working as expected.

g) Monitor if the cluster autoscales and load balances according to workload
```bash
kubectl get hpa tensorflow-training
kubectl describe hpa tensorflow-training
kubectl top pods
```
We could manually scale the deployment as well for immediate validation, where x is the number of replicas
```bash
kubectl scale deployment tensorflow-training --replicas=x
```

### If metrics server is not working
Verify if it is available
```bash
kubectl get --raw "/apis/metrics.k8s.io/v1beta1/nodes"
kubectl top nodes
kubectl top pods
kubectl get apiservices | grep metrics
kubectl describe apiservice v1beta1.metrics.k8s.io
```
Restarting it
```bash
kubectl rollout restart deployment metrics-server -n kube-system
```
If the metrics server is still not available, configure its deployment, including:
1. Add --kubelet-insecure-tls argument to containers args - used to skip verifying Kubelet CA certificates.
2.Change the container port from 10250 to port 4443
3. Add hostNetwork: true

```bash
kubectl patch deployment metrics-server -n kube-system --type='json' -p='[
{
"op": "add",
"path": "/spec/template/spec/hostNetwork",
"value": true
},
{
"op": "replace",
"path": "/spec/template/spec/containers/0/args",
"value": [
"--cert-dir=/tmp",
"--secure-port=4443",
"--kubelet-preferred-address-types=InternalIP,ExternalIP,Hostname",
"--kubelet-use-node-status-port",
"--metric-resolution=15s",
"--kubelet-insecure-tls"
]
},
{
"op": "replace",
"path": "/spec/template/spec/containers/0/ports/0/containerPort",
"value": 4443
}
]'
```

Check this [blog](https://medium.com/@cloudspinx/fix-error-metrics-api-not-available-in-kubernetes-aa10766e1c2f) for more details.



