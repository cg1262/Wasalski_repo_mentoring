class ServiceSilver:
    def __init__(self, spark):
        self.spark = spark

    def applications(self):
        self.spark.sql(
            """
            INSERT OVERWRITE TABLE engineering_metrics.silver.checkmarx_applications
            SELECT
                source.id AS application_id,
                source.name AS name,
                source.description AS description,
                source.type AS type,
                source.criticality AS criticality,
                source.rules AS rules,
                source.projectIds AS project_id,
                source.tags AS tags,
                TRY_CAST(source.createdAt AS timestamp) AS created_at,
                TRY_CAST(source.updatedAt AS timestamp) AS updated_at
            FROM engineering_metrics.bronze.checkmarx_applications AS source
            """
        )

    def scans(self):
        self.spark.sql(
            """
            INSERT OVERWRITE TABLE engineering_metrics.silver.checkmarx_scans
            SELECT
                source.id                                AS scan_id,
                source.status                             AS status,
                source.statusDetails                      AS status_details,
                source.branch                             AS branch,
                TRY_CAST(source.createdAt AS timestamp)   AS created_at,
                TRY_CAST(source.updatedAt AS timestamp)   AS updated_at,
                source.projectId                          AS project_id,
                source.projectName                        AS project_name,
                source.userAgent                          AS user_agent,
                source.initiator                          AS initiator,
                source.metadata                           AS metadata,
                source.engines                            AS engines,
                source.sourceType                         AS source_type,
                source.sourceOrigin                       AS source_origin
            FROM engineering_metrics.bronze.checkmarx_scans AS source;
            """
        )
