class ServiceSilver:
    def __init__(self, spark):
        self.spark = spark
        
    def commits(self):
        self.spark.sql(
            """
                INSERT OVERWRITE TABLE engineering_metrics.silver.azure_devops_commits
                SELECT
                    repository_id,
                    branch_name,
                    commitId AS commit_id,
                    get_json_object(author, '$.email') AS author_email,
                    get_json_object(author, '$.date') AS datetime,
                    comment
                FROM engineering_metrics.bronze.azure_devops_commits;

            """
        )

    def projects(self):
        self.spark.sql(
            """
            INSERT OVERWRITE TABLE engineering_metrics.silver.azure_devops_projects
            SELECT
                id,
                name,
                url,
                state,
                revision,
                visibility,
                lastUpdateTime AS last_update_time,
                description
            FROM engineering_metrics.bronze.azure_devops_projects;
            """
        )

    def pipeline_runs(self):
        self.spark.sql(
            """
            insert overwrite table engineering_metrics.silver.azure_devops_pipeline_runs
            select
            env as environment,
            pipeline,
            state,
            url,
            id string,
            get_json_object(pipeline, '$.id') AS pipeline_id,
            result as result,
            createdDate as created_date,
            finishedDate as finished_date,
            datediff(MINUTE,createdDate,finishedDate) as run_time_minutes,
            issue_key as issue_key,
            extracted_name_for_issue_key as extracted_name_for_issue_key,
            rank as rank_from_finished_date_asc,
            first_is_succeeded as first_success
            from engineering_metrics.bronze.azure_devops_pipeline_runs
            """
        )
    def approvals(self):
        self.spark.sql(
            """
            INSERT OVERWRITE TABLE engineering_metrics.silver.azure_devops_approvals
            select
                ID,
                STATUS,
                get_json_object(PIPELINE, '$.id') AS pipeline_id,
                get_json_object(PIPELINE, '$.name') AS pipeline_name,
                get_json_object(PIPELINE, '$.owner.id') AS pipeline_owner_id,
                CAST(CREATEDON AS TIMESTAMP) AS created_on,
                MINREQUIREDAPPROVERS AS min_required_approvers
                from engineering_metrics.bronze.azure_devops_approvals
    """
    )


    def repos(self):
        self.spark.sql(
            """
            INSERT overwrite table engineering_metrics.silver.azure_devops_repos
        SELECT
            ID as repo_id,
            URL,
            NAME,
            SIZE,
            isDisabled as is_disabled, 
            defaultBranch as default_branch,
            isInMaintenance as is_in_maintenance,
            PROJECT 
        FROM engineering_metrics.bronze.azure_devops_repos
            """
    )


    def branches(self):
        self.spark.sql(
            """
            INSERT overwrite table engineering_metrics.silver.azure_devops_branches
              SELECT
                project_name,
                repository_id,
                branch_name
            from engineering_metrics.bronze.azure_devops_branches
            """
        )


    def pipeline_runs_agg(self):
        self.spark.sql(
            """
            INSERT OVERWRITE TABLE engineering_metrics.silver.azure_devops_pipeline_runs_agg
            WITH

            -- 1) First successful rank
            min_rank AS (
                SELECT 
                    issue_key,
                    pipeline_id,
                    MIN(rank_from_finished_date_asc) AS rank_min
                FROM engineering_metrics.silver.azure_devops_pipeline_runs 
                WHERE result = 'succeeded'
                GROUP BY issue_key, pipeline_id
            ),

            -- 2) Total runtime until first success
            azure_devops_pipeline_runs_sum_first_succeeded AS (
                SELECT
                    apr.issue_key,
                    apr.pipeline_id,
                    SUM(run_time_minutes) AS total_run_time_minutes
                FROM engineering_metrics.silver.azure_devops_pipeline_runs apr
                INNER JOIN min_rank mr 
                    ON apr.issue_key = mr.issue_key
                    AND apr.pipeline_id = mr.pipeline_id
                WHERE apr.rank_from_finished_date_asc <= mr.rank_min
                GROUP BY apr.issue_key, apr.pipeline_id
            ),

            -- 3) First successful run runtime
            first_success_run_time AS (
                SELECT 
                    main.issue_key,
                    main.pipeline_id,
                    main.run_time_minutes AS first_succeeded_run_time
                FROM engineering_metrics.silver.azure_devops_pipeline_runs main
                WHERE main.result = 'succeeded'
                AND main.rank_from_finished_date_asc = (
                        SELECT MIN(sub.rank_from_finished_date_asc)
                        FROM engineering_metrics.silver.azure_devops_pipeline_runs sub
                        WHERE sub.issue_key = main.issue_key
                        AND sub.pipeline_id = main.pipeline_id
                        AND sub.result = 'succeeded'
                )
            ),

            -- 4) Stats of successful runs
            first_success AS (
                SELECT 
                    issue_key,
                    pipeline_id,
                    MIN(rank_from_finished_date_asc) AS successful_attempt,
                    AVG(run_time_minutes) AS avg_run_time
                FROM engineering_metrics.silver.azure_devops_pipeline_runs
                WHERE result = 'succeeded'
                GROUP BY issue_key, pipeline_id
            )

            -- 5) Final SELECT — absolutely everything is STRING
            SELECT
                apr.issue_key,
                CONCAT(runs.pipeline_id, '') AS pipeline_id,
                CONCAT(fs.successful_attempt, '') AS successful_attempt,
                CONCAT(fs.avg_run_time, '') AS avg_run_time_for_succeeded_min,
                CONCAT(fsrt.first_succeeded_run_time, '') AS first_succeeded_build_time_min,
                CONCAT(sfs.total_run_time_minutes, '') AS minutes_with_first_success

            FROM (SELECT DISTINCT issue_key FROM engineering_metrics.bronze.azure_devops_pipeline_runs) apr
            LEFT JOIN (
                SELECT DISTINCT issue_key, pipeline_id
                FROM engineering_metrics.silver.azure_devops_pipeline_runs
            ) runs
                ON apr.issue_key = runs.issue_key
            LEFT JOIN first_success fs
                ON apr.issue_key = fs.issue_key AND runs.pipeline_id = fs.pipeline_id
            LEFT JOIN first_success_run_time fsrt
                ON apr.issue_key = fsrt.issue_key AND runs.pipeline_id = fsrt.pipeline_id
            LEFT JOIN azure_devops_pipeline_runs_sum_first_succeeded sfs
                ON apr.issue_key = sfs.issue_key AND runs.pipeline_id = sfs.pipeline_id
            """
        )



    def pipeline_runs_agg_minutes_env(self):
        self.spark.sql(
            """
            INSERT OVERWRITE TABLE engineering_metrics.silver.azure_devops_pipeline_runs_agg_minutes_env
            SELECT
                environment,
                SUM(CAST(run_time_minutes AS INT)) AS summed_run_time_minutes
            FROM engineering_metrics.silver.azure_devops_pipeline_runs
            GROUP BY 1
            ORDER BY 1
            """
        )



    def pipeline_runs_agg_minutes_issue_key(self):
        self.spark.sql(
            """
            insert overwrite table engineering_metrics.silver.azure_devops_pipeline_runs_agg_minutes_issue_key
            select
            issue_key,
            SUM(CAST(run_time_minutes AS INT)) AS summed_run_time_minutes
            from engineering_metrics.silver.azure_devops_pipeline_runs
            group by 1
            order by 1
            """
        )

    def builds(self):
        """
        Bronze → Silver copy for azure_devops_builds.
        Explicit aliasing so developers know the source fields.
        """
        self.spark.sql(
            """
            insert overwrite table engineering_metrics.silver.azure_devops_builds
            select
                cast(_links as string) as _links,
                cast(properties as string) as properties,
                cast(tags as string) as tags,
                cast(validationresults as string) as validation_results,
                cast(plans as string) as plans,
                cast(triggerinfo as string) as trigger_info,
                cast(id as string) as id,
                cast(buildnumber as string) as build_number,
                cast(status as string) as status,
                cast(result as string) as result,
                cast(queuetime as string) as queue_time,
                cast(starttime as string) as start_time,
                cast(finishtime as string) as finish_time,
                cast(url as string) as url,
                cast(definition as string) as definition,
                cast(project as string) as project,
                cast(uri as string) as uri,
                cast(sourcebranch as string) as source_branch,
                cast(sourceversion as string) as source_version,
                cast(queue as string) as queue,
                cast(priority as string) as priority,
                cast(reason as string) as reason,
                cast(requestedfor as string) as requested_for,
                cast(requestedby as string) as requested_by,
                cast(lastchangeddate as string) as last_changed_date,
                cast(lastchangedby as string) as last_changed_by,
                cast(parameters as string) as parameters,
                cast(orchestrationplan as string) as orchestration_plan,
                cast(logs as string) as logs,
                cast(repository as string) as repository,
                cast(retainedbyrelease as string) as retained_by_release,
                cast(triggeredbybuild as string) as triggered_by_build,
                cast(appendcommitmessagetorunname as string) as append_commit_message_to_run_name,
                cast(project_name as string) as project_name,
                cast(repo_id as string) as repo_id,
                cast(templateparameters as string) as template_parameters,
                cast(buildnumberrevision as string) as build_number_revision
            from engineering_metrics.bronze.azure_devops_builds
            """
        )
    def pull_requests(self):
        """
        Bronze → Silver ETL for azure_devops_pull_requests.
        Every renamed field includes an alias showing its bronze origin.
        """
        self.spark.sql(
            """
            INSERT OVERWRITE TABLE engineering_metrics.silver.azure_devops_pull_requests
            SELECT
                CAST(repository AS STRING) AS repository,
                CAST(pullrequestid AS STRING) AS pull_request_id,
                CAST(codereviewid AS STRING) AS code_review_id,
                CAST(status AS STRING) AS status,
                CAST(createdby AS STRING) AS created_by,
                CAST(creationdate AS STRING) AS creation_date,
                CAST(closeddate AS STRING) AS closed_date,
                CAST(title AS STRING) AS title,
                CAST(description AS STRING) AS description,
                CAST(sourcerefname AS STRING) AS source_ref_name,
                CAST(targetrefname AS STRING) AS target_ref_name,
                CAST(mergestatus AS STRING) AS merge_status,
                CAST(isdraft AS STRING) AS is_draft,
                CAST(mergeid AS STRING) AS merge_id,
                CAST(lastmergesourcecommit AS STRING) AS last_merge_source_commit,
                CAST(lastmergetargetcommit AS STRING) AS last_merge_target_commit,
                CAST(lastmergecommit AS STRING) AS last_merge_commit,
                CAST(reviewers AS STRING) AS reviewers,
                CAST(url AS STRING) AS url,
                CAST(completionoptions AS STRING) AS completion_options,
                CAST(supportsiterations AS STRING) AS supports_iterations,
                CAST(completionqueuetime AS STRING) AS completion_queue_time,
                CAST(project_name AS STRING) AS project_name,
                CAST(repo_id AS STRING) AS repo_id,
                CAST(autocompletesetby AS STRING) AS auto_complete_set_by
            FROM engineering_metrics.bronze.azure_devops_pull_requests
            """
        )

    def aged_pull_requests(self):
        """
        Silver → Silver aggregation for aged pull requests.
        Buckets PRs by age in days.
        """
        self.spark.sql(
            """
            INSERT OVERWRITE TABLE engineering_metrics.silver.azure_devops_aged_pull_requests
            SELECT
                SUM(
                    CASE WHEN DATEDIFF(
                        DAY,
                        TO_TIMESTAMP(REGEXP_REPLACE(creation_date, '(\\\\d{2})(\\\\d{2})$', '\\\\1:\\\\2')),
                        CURRENT_TIMESTAMP()
                    ) < 1 THEN 1 ELSE 0 END
                ) AS one_day_tickets,

                SUM(
                    CASE WHEN DATEDIFF(
                        DAY,
                        TO_TIMESTAMP(REGEXP_REPLACE(creation_date, '(\\\\d{2})(\\\\d{2})$', '\\\\1:\\\\2')),
                        CURRENT_TIMESTAMP()
                    ) BETWEEN 1 AND 3 THEN 1 ELSE 0 END
                ) AS three_day_tickets,

                SUM(
                    CASE WHEN DATEDIFF(
                        DAY,
                        TO_TIMESTAMP(REGEXP_REPLACE(creation_date, '(\\\\d{2})(\\\\d{2})$', '\\\\1:\\\\2')),
                        CURRENT_TIMESTAMP()
                    ) BETWEEN 4 AND 7 THEN 1 ELSE 0 END
                ) AS seven_day_tickets,

                SUM(
                    CASE WHEN DATEDIFF(
                        DAY,
                        TO_TIMESTAMP(REGEXP_REPLACE(creation_date, '(\\\\d{2})(\\\\d{2})$', '\\\\1:\\\\2')),
                        CURRENT_TIMESTAMP()
                    ) > 7 THEN 1 ELSE 0 END
                ) AS older_tickets

            FROM engineering_metrics.silver.azure_devops_pull_requests
            WHERE status = 'active'
            """
        )

