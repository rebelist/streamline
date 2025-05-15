# Streamline

### Engineering and Management Metrics Platform for JSMD

The **Streamline** project is about building a metrics platform that brings together data from Jira, GitLab, AWS,
Datadog,
and
other tools
used across Jochen Schweizer mydays (JSMD). The goal is to give teams and managers clear, data-driven insights into how
work gets done, how fast code moves, how teams collaborate, how stable and costly systems are, and how changes in
process actually
affect outcomes.

It’s not just about engineering metrics like delivery speed or reliability, it’s also about giving managers visibility
into team health, workload patterns, and the results of decisions over time. Instead of relying on gut feeling or
scattered reports, the platform helps everyone, developers, leads, and managers, make better calls based on real data.
In the end, it’s a tool to support smarter decisions, continuous improvement, and a more transparent way of working.

### How to run Streamline

1. Run `make init`
2. Add `JIRA_HOST` and `JIRA_TOKEN` to the **.env** file.
3. Edit the Jira section of the **settings.ini** file, with your preferences.
    - team: The name of the team.
    - project: The Jira project identifier
    - board_id: A numerical identifier for a specific board within the Jira instance.
    - sprint_start_at: The index of the first sprint to return (0 based).
    - issue_statuses: Type of Jira issues to consider.
4. Run `make build`
5. Run `make start`

### How to configure Grafana & Disaply the Charts

1. Login to Grafana using _admin/admin_.
2. Click _Skip_.
3. Click on **Connections** -> _Add new connection_.
4. Search for _"Infinity"_.
5. Click **Install** -> Click in the Infinity Icon.
6. Click on _Add New Datasource_
7. Write the name _"streamline-datasource"_
8. Go to **URL, Headers & Params** and in **Base Url** write _http://host.docker.internal:8000_
9. Click _Save & Test_
10. Click **Dashboards** -> **New** -> _Import_
11. Choose to upload the file _docker/grafana/dashboards/workflow_performance.json_
12. Select **streamline-datasource** datasource.
13. You can now visualize the cycle time, for the team selected.

### How to shudown Streamline

Run `make shutdown`