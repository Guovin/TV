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

| Configuration Item     | Default Value                                                                                                               | Description                                                                                                        |
| ---------------------- | --------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| source_file            | "demo.txt"                                                                                                                  | Template file name                                                                                                 |
| final_file             | "result.txt"                                                                                                                | Generated file name                                                                                                |
| favorite_list          | ["广东珠江","CCTV-1","CCTV-5","CCTV-5+","CCTV-13","广东体育","广东卫视","大湾区卫视","浙江卫视","湖南卫视","翡翠台"]        | List of favorite channel names (used only to distinguish from regular channels, custom page retrieval quantity)    |
| open_online_search     | False                                                                                                                       | Enable online search source feature                                                                                |
| favorite_page_num      | 5                                                                                                                           | Page retrieval quantity for favorite channels                                                                      |
| default_page_num       | 3                                                                                                                           | Page retrieval quantity for regular channels                                                                       |
| urls_limit             | 10                                                                                                                          | Number of interfaces per channel                                                                                   |
| open_sort              | True                                                                                                                        | Enable the sorting function (response speed, date, resolution), or turn it off if it takes a long time to execute  |
| response_time_weight   | 0.5                                                                                                                         | Response time weight value (the sum of all weight values should be 1)                                              |
| resolution_weight      | 0.5                                                                                                                         | Resolution weight value (the sum of all weight values should be 1)                                                 |
| recent_days            | 30                                                                                                                          | Retrieve interfaces updated within a recent time range (in days), reducing appropriately can avoid matching issues |
| ipv_type               | "ipv4"                                                                                                                      | The type of interface in the generated result, optional values: "ipv4", "ipv6", "all"                              |
| domain_blacklist       | ["epg.pw"]                                                                                                                  | Interface domain blacklist, used to filter out interfaces with low-quality, ad-inclusive domains                   |
| url_keywords_blacklist | []                                                                                                                          | Interface keyword blacklist, used to filter out interfaces containing specific characters                          |
| open_subscribe         | True                                                                                                                        | Enable subscription source feature                                                                                 |
| subscribe_urls         | ["https://m3u.ibert.me/txt/fmml_dv6.txt",<br>"https://m3u.ibert.me/txt/o_cn.txt",<br>"https://m3u.ibert.me/txt/j_iptv.txt"] | Subscription source list                                                                                           |
| open_multicast         | True                                                                                                                        | Enable multicast source function                                                                                   |
| region_list            | ["all"]                                                                                                                     | Multicast source region list, [more regions](./fofa_map.py, "all" means all regions)                               |

## Step 4: Run Updates Locally (Recommended, Stable, Supports a large number of channel updates)

### 1. Install Python

Please download and install Python from the official website, and choose to add Python to the system environment variable Path during installation.

### 2. Run the Update

Open the terminal CMD under the project directory and run the following commands in order:

```python
pip3 install pipenv
pipenv install
pipenv run build
```

### 3. Update the File to the Repository

After the interface update is completed, upload the user_result.txt to your personal repository to complete the update.
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

## Step 6: Enable Auto-update (Only suitable for a small number of channel updates)

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

- Note: Except for the first execution of the workflow, which requires you to manually trigger it, subsequent executions (default: daily at 8:00 am Beijing time) will be automatically triggered. If you have modified the template or configuration files and want to execute the update immediately, you can manually trigger (2) Run workflow.

## Step 7: Modify Workflow Update Frequency

![.github/workflows/main.yml](./images/schedule-cron.png '.github/workflows/main.yml')
If you want to modify the update frequency (default: daily at 8:00 am Beijing time), you can modify the on:schedule:- cron field.

### 1. It is strongly discouraged to make modifications, as there is no difference in the content of the interface in a short period of time. Both too frequent updates and high-consumption running workflows may be judged as resource abuse, leading to the risk of the repository and account being banned.

### 2. Please pay attention to the runtime of your workflow. If you find that the execution time is too long, you need to appropriately reduce the number of channels in the template, modify the number of pages and interfaces in the configuration, in order to meet the compliant operation requirements.
