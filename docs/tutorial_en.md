# Tutorial

[中文](./tutorial.md) | English

## Step 1: Fork this Repository

Copy the source code of this repository to your personal account repository

### 1. Click Fork on the homepage:

![Fork Entrance](./images/fork-btn.png 'Fork Entrance')

### 2. Fork to create a personal repository:

![Fork Details](./images/fork-detail.png 'Fork Details')

1. Name your personal repository, you can name it whatever you like (the final live source result link depends on this name), here we use default TV as an example.
2. After confirming the information is correct, click to confirm and create.

## Step 2: Modify the Template

When you click to confirm and create in step one, you will be automatically redirected to your personal repository. At this point, your personal repository is created, and you can customize your personal live source channel menu!

### 1. Click on the demo.txt template file:

![demo.txt Entrance](./images/demo-btn.png 'demo.txt Entrance')

### 2. Create a personal template user_demo.txt:

![Create user_demo.txt](./images/edit-user-demo.png 'Create user_demo.txt')

1. Create file
2. Name the template file user_demo.txt
3. The template file needs to be written in the format of (channel category, #genre#), (channel name, channel interface), note that it is an English comma. The maximum number of channels is 200, any excess will not be updated.
4. Click Commit changes... to save.

## Step 3: Modify the Configuration

Similar to editing the template, modify the running configuration

### 1. Click on the config.py configuration file:

![config.py Entrance](./images/config-btn.png 'config.py Entrance')

### 2. Copy the default configuration file content:

![Copy config.py](./images/copy-config.png 'Copy default template')

### 3. Create a personal configuration file user_config.py:

![Create user_config.py](./images/edit-user-config.png 'Create user_config.py')

1. Create file
2. Name the configuration file user_config.py
3. Paste the default template, modify source_file = "user_demo.txt"; final_file = "user_result.txt"
4. Click Commit changes... to save.

Adjust the configuration as needed. Below is the default configuration explanation:
[Config parameter](./docs/config_en.md)

## Step 4: Run Updates

### Method 1: Command Line Update

```python
1. Install Python
Please download and install Python from the official site. During installation, choose to add Python to the system's environment variables Path.

2. Run Update
Open a CMD terminal in the project directory and run the following commands in sequence:
pip3 install pipenv
pipenv install
pipenv run build
```

### Method 2: GUI Software Update

1. Download the update tool software, open the software, click update to complete the update.

2. Alternatively, run the following command in the project directory to open the GUI software:

```python
pipenv run ui
```

![Update tool software](./images/ui.png 'Update tool software')

### Method 3: Docker Update

- requests: Lightweight, low performance requirements, fast update speed, stability uncertain (recommend this version only for subscription sources)
- driver: Higher performance requirements, slower update speed, high stability, high success rate (use this version for online search, multicast sources)

```bash
1. Pull the image:
For requests version:
docker pull guovern/tv-requests:latest

For driver version:
docker pull guovern/tv-driver:latest

2. Run the container:
docker run -d -p 8000:8000 guovern/tv-requests or driver

Volume Mount Parameter (Optional):
-v host path/TV:/tv-requests or tv-driver

This allows synchronization of files between the host machine and the container. Modifying templates, configurations, and retrieving updated result files can be directly operated in the host machine's folder.
Note: Before running the container with this command, be sure to first clone this project to the host machine.

3. Check the update results: Visit (domain:8000)
```

#### Note: Link to the result file after updates of methods one to three: http://local ip:8000 or http://localhost:8000

### Method 4: Workflow Update

Please see step six

### 3. Update the File to the Repository(optional)

If you do not have your own domain address, after the interface update is completed, upload user_result.txt to your personal repository to use it.
![Username and Repository Name](./images/rep-info.png 'Username and Repository Name')
https://mirror.ghproxy.com/raw.githubusercontent.com/your github username/repository name (corresponding to the TV created when forking)/master/user_result.txt

## Step 5: Update the Source Code

Since this project will continue to iterate and improve, if you want to get the latest updates, you can do the following:

### 1. Star

Click on the star button at the homepage of my repository to favorite this project (Your star is the motivation for me to keep updating).
![Star](./images/star.png 'Star')

### 2. Watch

Follow this project to be notified by email about the latest updates and release logs through releases.
![Watch-activity](./images/watch-activity.png 'Watch All Activity')

### 3. Sync fork

Return to the homepage of your repository. If there are updates to the project, click on "Sync fork" and then "Update branch" to confirm and update to the latest code.
![Sync-fork](./images/sync-fork.png 'Sync fork')

## Please use the following content with caution. If you have a large number of channels that need to be updated, please use local updates instead of automatic updates. Improper configuration may lead to your account or workflow being banned!

## Step 6: Enable workflow auto-update

If your template and configuration modifications are correct, you can configure Actions to achieve automatic updates

### 1. Enter Actions:

![Actions Entrance](./images/actions-btn.png 'Actions Entrance')

### 2. Enable Actions workflow:

![Enable Actions workflow](./images/actions-enable.png 'Enable Actions workflow')
Since the Actions workflow of the forked repository is disabled by default, you need to manually enable it by clicking the button in the red box to confirm.

![Actions workflow enabled successfully](./images/actions-home.png 'Actions workflow enabled successfully')
After successful activation, you can see that there are no workflows running at the moment. Don't worry, let's start running your first update workflow below.

### 3. Run the update workflow:

#### (1) Enable update schedule:

![Enable Workflows update](./images/workflows-btn.png 'Enable Workflows update')

1. Click on update schedule under the Workflows category.
2. Since the workflow of the forked repository is disabled by default, click the Enable workflow button to confirm the activation.

#### (2) Run the Workflow based on branches:

![Run Workflow](./images/workflows-run.png 'Run Workflow')
Now you can run the update workflow.

1. Click Run workflow.
2. Here you can switch to the branch you want to run. Since the fork defaults to the master branch, if the template and configuration you modified are also in the master branch, just choose master here, and click Run workflow to confirm the run.

#### (3) Workflow in progress:

![Workflow in progress](./images/workflow-running.png 'Workflow in progress')
Wait a moment, and you will see that your first update workflow is running!
(Note: The running time depends on the number of channels and pages in your template and other configurations, and also largely depends on the current network conditions. Please be patient. The default template and configuration usually take about 25 minutes.)

#### (4) Cancel the running Workflow:

![Cancel running Workflow](./images/workflow-cancel.png 'Cancel running Workflow')
If you feel that this update is not quite right and you need to modify the template or configuration before running again, you can click Cancel run to cancel this run.

#### (5) Workflow executed successfully:

![Workflow executed successfully](./images/workflow-success.png 'Workflow executed successfully')
If everything is normal, after a short wait, you will see that the workflow has been executed successfully (green check mark). At this point, you can visit the proxy file link to see if the latest results have been synchronized:
![Username and Repository Name](./images/rep-info.png 'Username and Repository Name')
https://mirror.ghproxy.com/raw.githubusercontent.com/your github username/repository name (corresponding to the TV created when forking)/master/user_result.txt

If you can access this link and it returns the updated interface content, then your live source interface link has been successfully created! Simply copy and paste this link into software like TVBox in the configuration field to use~

- Note: Except for the first execution of the workflow, which requires you to manually trigger it, subsequent executions (default: daily at 6:00 am Beijing time) will be automatically triggered. If you have modified the template or configuration files and want to execute the update immediately, you can manually trigger (2) Run workflow.

## Step 7: Modify Workflow Update Frequency

![.github/workflows/main.yml](./images/schedule-cron.png '.github/workflows/main.yml')
If you want to modify the update frequency (default: daily at 6:00 am Beijing time), you can modify the on:schedule:- cron field.

### 1. It is strongly discouraged to make modifications, as there is no difference in the content of the interface in a short period of time. Both too frequent updates and high-consumption running workflows may be judged as resource abuse, leading to the risk of the repository and account being banned.

### 2. Please pay attention to the runtime of your workflow. If you find that the execution time is too long, you need to appropriately reduce the number of channels in the template, modify the number of pages and interfaces in the configuration, in order to meet the compliant operation requirements.
