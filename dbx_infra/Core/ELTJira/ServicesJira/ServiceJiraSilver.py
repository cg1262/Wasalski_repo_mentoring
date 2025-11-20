class ServiceSilver:
    def __init__(self, spark):
        self.spark = spark

    def users(self):
        """MERGE jira_users from bronze to silver with column name standardization."""
        self.spark.sql(
            """
            INSERT OVERWRITE TABLE engineering_metrics.silver.jira_users
            SELECT
                source.self AS self,
                source.accountId AS account_id,
                source.accountType AS account_type,
                source.avatarUrls AS avatar_urls,
                source.displayName AS display_name,
                source.active AS active,
                source.timeZone AS time_zone,
                source.locale AS locale,
                source.emailAddress AS email_address
            FROM engineering_metrics.bronze.jira_users AS source
            """
        )

    def boards(self):
        self.spark.sql(
            """
            WITH sprintBoard AS (
                SELECT
                    sprint_id,
                    board_id
                FROM
                    engineering_metrics.silver.jira_issues_projects
                GROUP BY
                    sprint_id,
                    board_id
            )
            INSERT OVERWRITE TABLE engineering_metrics.silver.jira_boards
            SELECT 
                b.id AS id,
                b.name AS name,
                b.type AS type,
                b.projectId AS project_id,
                b.projectKey AS project_key,
                sb.sprint_id AS sprint_id,
                CONCAT('https://phlexglobal.atlassian.net/jira/software/c/projects/', b.projectKey, '/boards/', b.id, '?sprints=', sb.sprint_id) AS current_sprint_url
            FROM engineering_metrics.bronze.jira_boards AS b
            LEFT JOIN sprintBoard AS sb ON sb.board_id = b.id
            """
        )

    def projects(self):
        self.spark.sql(
            """
            INSERT OVERWRITE TABLE engineering_metrics.silver.jira_projects
            SELECT
                CAST(source.id AS INT) AS id,
                source.key AS key,
                source.name AS name,
                CAST(source.isPrivate AS BOOLEAN) AS is_private,
                source.projectTypeKey AS project_type_key
            FROM engineering_metrics.bronze.jira_projects AS source
            """
        )

    def project_versions(self):
        self.spark.sql(
            """
            INSERT OVERWRITE TABLE engineering_metrics.silver.jira_project_versions
            SELECT
                CAST(source.id AS INT) AS id,
                source.name AS name,
                source.self AS self,
                source.overdue AS overdue,
                source.archived AS archived,
                source.released AS released,
                source.projectId AS project_id,
                source.startDate AS start_date,
                source.description AS description,
                source.releaseDate AS release_date,
                source.userStartDate AS user_start_date
            FROM engineering_metrics.bronze.jira_project_versions AS source
            """
        )
    def sprints(self):
        self.spark.sql(
            """
            INSERT OVERWRITE TABLE engineering_metrics.silver.jira_sprints
            SELECT
                source.id AS id,
                source.name AS name,
                source.state AS state,
                source.endDate AS end_date,
                source.startDate AS start_date,
                source.createdDate AS created_date,
                source.completeDate AS complete_date
            FROM engineering_metrics.bronze.jira_sprints AS source
            """
        )

    def issues_projects(self):
        """MERGE with transformation embedded in USING clause"""
        self.spark.sql(
            """
            INSERT OVERWRITE TABLE engineering_metrics.silver.jira_issues_projects
            SELECT
                source.id AS id,
                source.key AS key,
                source.created AS created,
                source.updated AS updated,
                source.project_id AS project_id,
                source.project_key AS project_key,
                source.due_date AS due_date,
                source.current_status AS current_status,
                source.assignee AS assignee,
                source.reporter AS reporter,
                source.resolution_date AS resolution_date,
                source.resolution_date_string AS resolution_date_string,
                source.summary AS summary,
                source.story_point AS story_point,
                source.owner_team AS owner_team,
                source.priority AS priority,
                source.issue_category AS issue_category,
                source.impact AS impact,
                source.root_cause_category AS root_cause_category,
                source.client_name AS client_name,
                source.root_cause AS root_cause,
                source.components AS components,
                source.parent_issue_type AS parent_issue_type,
                source.sprint_name AS sprint_name,
                source.sprint_id AS sprint_id,
                source.board_id AS board_id,
                source.bug_discovery AS bug_discovery,
                source.failure_rate AS failure_rate,
                source.change_failure AS change_failure,
                source.inherent_risk AS inherent_risk,
                source.inherent_risk_level AS inherent_risk_level,
                source.goals AS goals,
                source.issue_type AS issue_type,
                source.labels AS labels
            FROM (
                SELECT
                    id,
                    key,
                    TRY_PARSE_JSON(versionedRepresentations):created['1']::TIMESTAMP AS created,
                    TRY_PARSE_JSON(versionedRepresentations):updated['1']::TIMESTAMP AS updated,
                    TRY_PARSE_JSON(versionedRepresentations):project['1']['id'] AS project_id,
                    TRY_PARSE_JSON(versionedRepresentations):project['1']['key'] AS project_key,
                    TRY_PARSE_JSON(versionedRepresentations):duedate['1']::TIMESTAMP AS due_date,
                    TRY_PARSE_JSON(versionedRepresentations):status['1']['name'] AS current_status,
                    TRY_PARSE_JSON(versionedRepresentations):assignee['1']['displayName'] AS assignee,
                    TRY_PARSE_JSON(versionedRepresentations):reporter['1']['displayName'] AS reporter,
                    TRY_PARSE_JSON(versionedRepresentations):resolutiondate['1']::TIMESTAMP AS resolution_date,
                    TRY_PARSE_JSON(versionedRepresentations):resolutiondate['1'] AS resolution_date_string,
                    TRY_PARSE_JSON(versionedRepresentations):summary['1'] AS summary,
                    TRY_PARSE_JSON(versionedRepresentations):customfield_10006['1']::INT AS story_point,
                    TRY_PARSE_JSON(versionedRepresentations):customfield_11328['1']['value'] AS owner_team,
                    TRY_PARSE_JSON(versionedRepresentations):priority['1']['name'] AS priority,
                    TRY_PARSE_JSON(versionedRepresentations):customfield_11418['1']['value'] AS issue_category,
                    TRY_PARSE_JSON(versionedRepresentations):customfield_10017['1']['value'] AS impact,
                    TRY_PARSE_JSON(versionedRepresentations):customfield_11365['1']['value'] AS root_cause_category,
                    TRY_PARSE_JSON(versionedRepresentations):customfield_10206['1']['value'] AS client_name,
                    TRY_PARSE_JSON(fields):customfield_10028 AS root_cause,
                    TRY_PARSE_JSON(versionedRepresentations):components['1'][0]['name'] AS components,
                    TRY_PARSE_JSON(fields):parent.fields.issuetype.name AS parent_issue_type,
                    TRY_PARSE_JSON(versionedRepresentations):customfield_10004['1'][0]['name'] AS sprint_name,
                    TRY_PARSE_JSON(versionedRepresentations):customfield_10004['1'][0]['id'] AS sprint_id,
                    TRY_PARSE_JSON(versionedRepresentations):customfield_10004['1'][0]['boardId'] AS board_id,
                    TRY_PARSE_JSON(versionedRepresentations):customfield_11443['1']['value'] AS bug_discovery,
                    TRY_PARSE_JSON(versionedRepresentations):customfield_11898['1']['value'] AS failure_rate,
                    TRY_PARSE_JSON(versionedRepresentations):customfield_11763['1']['value'] AS change_failure,
                    TRY_PARSE_JSON(versionedRepresentations):customfield_11310['1'] AS inherent_risk,
                    TRY_PARSE_JSON(versionedRepresentations):customfield_11575['1']['value'] AS inherent_risk_level,
                    TRY_PARSE_JSON(versionedRepresentations):customfield_11765['1'][0]['id'] AS goals,
                    TRY_PARSE_JSON(versionedRepresentations):issuetype['1']['name'] AS issue_type,
                    REPLACE(REPLACE(REPLACE(TRY_PARSE_JSON(versionedRepresentations):labels['1']::STRING, '',''), '[', ''), ']','') AS labels
                FROM
                    engineering_metrics.bronze.jira_issues_projects
            ) AS source
            """
        )



    def risk_types(self):
        self.spark.sql(
            """
            INSERT OVERWRITE TABLE engineering_metrics.silver.jira_risk_types
            SELECT
                source.issue_key AS issue_key,
                source.risk_type AS risk_type
            FROM (
                SELECT
                    key AS issue_key,
                    TRY_PARSE_JSON(versionedRepresentations):customfield_11570['1'][0].value::STRING AS risk_type
                FROM engineering_metrics.bronze.jira_issues_projects
                WHERE TRY_PARSE_JSON(versionedRepresentations):customfield_11570['1'][0].value IS NOT NULL
            ) AS source
            """
        )

    def issues_changes(self):
        self.spark.sql(
            """
            INSERT OVERWRITE TABLE engineering_metrics.silver.jira_issues_changes
            SELECT
                source.issue_id AS issue_id,
                source.key AS key,
                source.created_date AS created_date,
                source.change_id AS change_id,
                source.from_state AS from_state,
                source.to_state AS to_state
            FROM (
                SELECT 
                    CAST(id AS INT) AS issue_id,
                    key,
                    CAST(SUBSTRING(TRY_PARSE_JSON(changelog):histories[0].created::STRING, 1, CHARINDEX('T', TRY_PARSE_JSON(changelog):histories[0].created::STRING) - 1) AS DATE) AS created_date,
                    TRY_PARSE_JSON(changelog):histories[0].id::STRING AS change_id,
                    TRY_PARSE_JSON(changelog):histories[0].items[0].fromString AS from_state,
                    TRY_PARSE_JSON(changelog):histories[0].items[0].toString AS to_state
                FROM
                    engineering_metrics.bronze.jira_issues_projects
                WHERE TRY_PARSE_JSON(changelog):histories[0].items[0].field::STRING = 'status'
            ) AS source
            """
        )

    def issue_changes_owner_team_tls(self):
        self.spark.sql(
            """
            INSERT OVERWRITE TABLE engineering_metrics.silver.jira_issue_changes_owner_team_tls
            SELECT
                source.issue_id AS issue_id,
                source.key AS key,
                source.created_date AS created_date,
                source.change_id AS change_id,
                source.from_state AS from_state,
                source.to_state AS to_state
            FROM (
                SELECT 
                    CAST(id AS INT) AS issue_id,
                    key,
                    CAST(SUBSTRING(TRY_PARSE_JSON(changelog):histories[0].created::STRING, 1, CHARINDEX('T', TRY_PARSE_JSON(changelog):histories[0].created::STRING) - 1) AS DATE) AS created_date,
                    TRY_PARSE_JSON(changelog):histories[0].id::STRING AS change_id,
                    TRY_PARSE_JSON(changelog):histories[0].items[0].fromString AS from_state,
                    TRY_PARSE_JSON(changelog):histories[0].items[0].toString AS to_state
                FROM
                    engineering_metrics.bronze.jira_issues_projects
                WHERE key like 'TLS%'
            ) AS source
            """
        )

    def sprint_issues(self):
        self.spark.sql(
            """
            INSERT OVERWRITE TABLE engineering_metrics.silver.jira_sprint_issues
            SELECT
                source.id AS id,
                source.key AS key,
                source.issue_id AS issue_id,
                source.sprint_id AS sprint_id,
                source.created AS created,
                source.updated AS updated
            FROM engineering_metrics.bronze.jira_sprint_issues AS source
            """
        )
    def risk_manager(self):
        self.spark.sql(
            """
            INSERT OVERWRITE TABLE engineering_metrics.silver.jira_risk_manager
            SELECT
                source.user_name AS user_name,
                source.issue_key AS issue_key,
                source.user_account_id AS user_account_id
            FROM (
                SELECT
                    TRY_PARSE_JSON(versionedRepresentations):customfield_11664['1'].displayName AS user_name,
                    key AS issue_key,
                    TRY_PARSE_JSON(versionedRepresentations):customfield_11664['1'].accountId AS user_account_id
                FROM engineering_metrics.bronze.jira_issues_projects
                WHERE TRY_PARSE_JSON(versionedRepresentations):customfield_11664['1'].displayName IS NOT NULL
            ) AS source
            """
        )
    def change_lead_time(self):
        self.spark.sql(
            """
            INSERT OVERWRITE TABLE engineering_metrics.silver.jira_change_lead_time
            SELECT
                source.issue_id AS issue_id,
                source.to_do_date AS to_do_date,
                source.done_date AS done_date,
                source.duration AS duration
            FROM (
                SELECT 
                    ic.issue_id,
                    MAX(CASE WHEN from_state = 'To Do' AND to_state <> 'To Do' THEN CAST(created_date AS DATE) END) AS to_do_date,
                    MAX(CASE WHEN from_state <> 'Done' AND to_state = 'Done' THEN CAST(created_date AS DATE) END) AS done_date,
                    CAST(DATEDIFF(
                        MAX(CASE WHEN from_state <> 'Done' AND to_state = 'Done' THEN created_date END),
                        MAX(CASE WHEN from_state = 'To Do' AND to_state <> 'To Do' THEN created_date END)
                    ) AS INT) + 1 AS duration
                FROM engineering_metrics.silver.jira_issues_changes AS ic
                JOIN engineering_metrics.silver.jira_issues_projects AS i ON ic.issue_id = i.id
                WHERE i.current_status = 'Done'
                AND (from_state = 'To Do' OR to_state = 'Done')
                GROUP BY ic.issue_id, i.current_status
                HAVING
                    MAX(CASE WHEN from_state = 'To Do' AND to_state <> 'To Do' THEN CAST(created_date AS DATE) END) IS NOT NULL 
                    AND MAX(CASE WHEN from_state <> 'Done' AND to_state = 'Done' THEN CAST(created_date AS DATE) END) IS NOT NULL
            ) AS source
            """
        )
