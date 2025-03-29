# EC2Watchdog: Automated EC2 Instance Management

> **Automatically stop and start idle EC2 instances to optimize AWS costs** 💰🔄

## 🚀 Overview
**EC2Watchdog** is an AWS Lambda-based automation tool designed to **reduce unnecessary AWS compute costs** by:

1. **Identifying idle EC2 instances** (based on CPU, network, and disk activity)  
2. **Stopping test/demo instances** during non-business hours (8 PM – 9 AM IST)  
3. **Restarting instances automatically** when needed  
4. **Preventing accidental shutdowns** of critical instances using AWS Security Hub  
5. **Sending real-time notifications** to Slack or Microsoft Teams  

This ensures **cost savings** while **maintaining operational flexibility**!  

---

## 🛠 Features
### ✅ Automated Cost Optimization
- Stops idle **test/demo** instances at night (8 PM – 9 AM IST)  
- Resumes them automatically in the morning  
- Avoids stopping critical workloads  

### 🔍 Smart Idle Detection
- Checks **CPU, Network, and Disk I/O** usage  
- Uses **CloudWatch Metrics** to determine inactivity  

### 🛡 Security & Reliability
- **Prevents accidental shutdowns** of important instances  
- Uses **AWS Security Hub** to ensure compliance  

### 🔔 Real-Time Notifications
- **Slack / Microsoft Teams alerts** when instances are stopped  
- Engineers can **override auto-shutdown** via Slack  

### ⚡ Infrastructure as Code (Terraform)
- Fully provisioned using **Terraform**  
- IAM roles, Lambda permissions, and logging are automated  

---

## 🏗 Architecture
![Architecture Diagram](/ec2Watchdog_Architecture_diagram.png)
### **Key AWS Services Used**
- **AWS Lambda** → Runs the automation  
- **Amazon CloudWatch** → Monitors EC2 activity  
- **EC2 Tags** → Identifies test/demo instances  
- **AWS Security Hub** → Prevents shutdown of critical instances  
- **Amazon SNS / Slack API** → Sends alerts  

---

## 🔧 Setup & Installation
### 📌 1. Prerequisites
Before deploying **EC2Watchdog**, ensure you have:  
✅ **AWS Account** with necessary permissions  
✅ **AWS CLI** installed and configured (`aws configure`)  
✅ **Terraform** installed (`brew install terraform` or `choco install terraform`)  
✅ **Python 3.x** installed for Lambda scripts  

---

### 📌 2. Deploy with Terraform
Run the following commands to deploy the infrastructure:  
```bash
# Clone the repository
git clone https://github.com/yourusername/EC2Watchdog.git
cd EC2Watchdog

# Initialize Terraform
terraform init

# Plan the deployment
terraform plan

# Apply changes
terraform apply -auto-approve
```
This will **create the Lambda function, IAM roles, and SNS notifications** automatically!  

---

### 📌 3. Configure Slack Notifications
To enable Slack alerts:  
1. Create a **Slack Incoming Webhook URL**  
2. Add the webhook URL in `config.json`:  
```json
{
  "slack_webhook_url": "https://hooks.slack.com/services/your/webhook/url"
}
```
3. Deploy the updated config using:  
```bash
terraform apply -auto-approve
```

---

## 🏃 Usage
### 🔹 Check Scheduled Instances
Run manually to see which instances will be stopped:  
```bash
python scripts/check_instances.py
```

### 🔹 Force Stop an Instance
```bash
python scripts/stop_instance.py --instance-id i-1234567890abcdef
```

### 🔹 Override Auto-Stop via Slack
Reply `"Keep Running"` in the Slack notification thread to **override the shutdown**.

---

## 📊 Logging & Monitoring
- **All actions are logged in CloudWatch Logs**  
- **Failures trigger alerts in AWS SNS & Slack**  
- Use `aws logs tail /aws/lambda/EC2Watchdog --follow` to see logs in real-time  

---

## 🛠 Contributing
Want to improve **EC2Watchdog**? 🚀  
- Open an **Issue** for feature requests  
- Fork the repo & submit a **Pull Request**  
- Follow the **Project Kanban Board** for active tasks  

---

## 📜 License
This project is licensed under the **MIT License**.  

📢 **Maintained by [Nitin Gouda]** | [GitHub](https://github.com/shaggyyy2002)