class ServiceSilver:
    def __init__(self, spark):
        self.spark = spark

    def actors(self):
        self.spark.sql(
            """
            INSERT OVERWRITE TABLE engineering_metrics.silver.apify_actors
            SELECT
                source.id AS actor_id,
                TRY_CAST(source.createdAt AS timestamp) AS created_at,
                TRY_CAST(source.modifiedAt AS timestamp) AS modified_at,
                source.name AS actor_name,
                source.username AS username,
                source.title AS actor_title,
                source.stats AS stats
            FROM engineering_metrics.bronze.apify_actors AS source
            """
        )

    def actor_runs(self):
        self.spark.sql(
            """
            INSERT OVERWRITE TABLE engineering_metrics.silver.apify_actor_runs
            SELECT
                source.id AS run_id,
                source.actId AS actor_id,
                source.actorTaskId AS actor_task_id,
                source.status AS status,
                TRY_CAST(source.startedAt AS timestamp) AS started_at,
                TRY_CAST(source.finishedAt AS timestamp) AS finished_at,
                source.buildId AS build_id,
                source.buildNumber AS build_number,
                TRY_CAST(source.buildNumberInt AS int) AS build_number_int,
                source.meta AS meta,
                source.defaultKeyValueStoreId AS default_key_value_store_id,
                source.defaultDatasetId AS default_dataset_id,
                source.defaultRequestQueueId AS default_request_queue_id,
                source.usageTotalUsd AS usage_total_usd,
                source.userId AS user_id
            FROM engineering_metrics.bronze.apify_actor_runs AS source
            """
        )

    def actor_runs_details(self):
        self.spark.sql(
            """
            INSERT OVERWRITE TABLE engineering_metrics.silver.apify_actor_runs_details
            SELECT
                source.id AS actor_run_id,
                source.actId AS actor_id,
                source.userId AS user_id,
                source.actorTaskId AS actor_task_id,
                TRY_CAST(source.startedAt AS timestamp) AS started_at,
                TRY_CAST(source.finishedAt AS timestamp) AS finished_at,
                source.status AS status,
                source.statusMessage AS status_message,
                TRY_CAST(source.isStatusMessageTerminal AS boolean) AS is_status_message_terminal,
                source.stats AS stats,
                source.options AS options,
                source.createdByOrganizationMemberUserId AS member_user_id_created_by_org,
                source.buildId AS build_id,
                source.buildNumber AS build_number_int,
                TRY_CAST(source.exitCode AS int) AS exit_code,
                source.defaultKeyValueStoreId AS default_key_value_store_id,
                source.defaultDatasetId AS dafault_dataset_id,
                source.defaultRequestQueueId AS default_request_queue_id,
                source.platformUsageBillingModel AS paltform_usage_billing_model,
                source.generalAccess AS general_access,
                source.containerUrl AS container_url,
                source.usage AS usage,
                source.usageTotalUsd AS usage_total_in_usd,
                source.usageUsd AS usage_details,
                source.consoleUrl AS console_url,
                source.time_to_load_in_sec AS time_to_load_in_sec,
                source.time_to_load_in_min AS time_to_load_in_min,
                source.pages_scraped AS pages_scraped,
                source.pages_scraped_per_sec AS pages_scraped_per_sec,
                source.duration_in_sec AS duration
            FROM engineering_metrics.bronze.apify_actor_runs_details AS source
            """
        )
