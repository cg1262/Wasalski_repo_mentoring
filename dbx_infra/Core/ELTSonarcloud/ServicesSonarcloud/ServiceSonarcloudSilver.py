class ServiceSilver:
    def __init__(self, spark):
        self.spark = spark

    def issues(self):
        self.spark.sql(
            """
            INSERT OVERWRITE TABLE engineering_metrics.silver.sonarcloud_issues
            SELECT
                source.key AS issue_key,
                source.rule AS rule,
                source.severity AS severity,
                source.component AS component,
                source.line AS line,
                source.hash AS hash,
                source.textRange AS text_range,
                source.flows AS flows,
                source.status AS status,
                source.message AS message,
                source.effort AS effort,
                source.debt AS debt,
                source.assignee AS assignee,
                source.author AS author,
                source.tags AS tags,
                source.creationDate AS creation_date,
                source.updateDate AS update_date,
                source.type AS type,
                source.organization AS organization,
                source.externalRuleEngine AS external_rule_engine,
                source.cleanCodeAttribute AS clean_code_attribute,
                source.cleanCodeAttributeCategory AS clean_code_attribute_category,
                source.impacts AS impacts,
                source.issueStatus AS issue_status,
                source.projectName AS project_name,
                source.resolution AS resolution,
                Tsource.closeDate AS close_date,
                source.upsert_key AS upsert_key,
                get_json_object(source.impacts, '$[0].severity') AS impact_severity,
                get_json_object(source.impacts, '$[0].softwareQuality') AS software_quality
            FROM engineering_metrics.bronze.sonarcloud_issues AS source
            """
        )

    def metrics(self):
        self.spark.sql(
            """
            INSERT OVERWRITE TABLE engineering_metrics.silver.sonarcloud_metrics
            SELECT
                source.id AS id,
                source.key AS key,
                source.type AS type,
                source.name AS name,
                source.description AS description,
                source.domain AS domain,
                TRY_CAST(source.direction AS long) AS direction,
                TRY_CAST(source.qualitative AS boolean) AS qualitative,
                TRY_CAST(source.hidden AS boolean) AS hidden,
                TRY_CAST(source.decimalScale AS float) AS decimal_scale
            FROM engineering_metrics.bronze.sonarcloud_metrics AS source
            """
        )

    def projects(self):
        self.spark.sql(
            """
            INSERT OVERWRITE TABLE engineering_metrics.silver.sonarcloud_projects
            SELECT
                source.key AS key,
                source.name AS name,
                TRY_CAST(source.lastAnalysisDate AS timestamp) AS last_analysis_date,
                source.revision AS revision
            FROM engineering_metrics.bronze.sonarcloud_projects AS source
            """
        )

    def components(self):
        self.spark.sql(
            """
            INSERT OVERWRITE TABLE engineering_metrics.silver.sonarcloud_components
            SELECT
                source.organization AS organization,
                source.key AS key,
                source.name AS name,
                source.qualifier AS qualifier,
                source.project AS project
            FROM engineering_metrics.bronze.sonarcloud_components AS source
            """
        )
    def measures_component(self):
            self.spark.sql("""
                INSERT OVERWRITE engineering_metrics.silver.sonarcloud_measures_component
                WITH FLATTENED AS (
                SELECT
                    t.ID AS id,
                    t.KEY AS key,
                    t.NAME AS name,
                    explode(from_json(t.MEASURES, 'array<struct<metric:string,value:string>>')) AS measure
                FROM engineering_metrics.bronze.sonarcloud_measures_component t
                ),
                PIVOTED_TABLE AS (
                SELECT
                    id,
                    key,
                    name,
                    MAX(CASE WHEN measure.metric = 'files' THEN measure.value END) AS files,
                    MAX(CASE WHEN measure.metric = 'ncloc' THEN measure.value END) AS ncloc,
                    MAX(CASE WHEN measure.metric = 'maintainability_issues' THEN measure.value END) AS maintainability_issues,
                    MAX(CASE WHEN measure.metric = 'reliability_issues' THEN measure.value END) AS reliability_issues,
                    MAX(CASE WHEN measure.metric = 'security_hotspots' THEN measure.value END) AS security_hotspots,
                    MAX(CASE WHEN measure.metric = 'security_issues' THEN measure.value END) AS security_issues,
                    MAX(CASE WHEN measure.metric = 'line_coverage' THEN measure.value END) AS line_coverage,
                    MAX(CASE WHEN measure.metric = 'duplicated_lines' THEN measure.value END) AS duplicated_lines,
                    MAX(CASE WHEN measure.metric = 'duplicated_lines_density' THEN measure.value END) AS duplicated_lines_density
                FROM FLATTENED
                GROUP BY id, key, name
                )
                SELECT
                id,
                key,
                name,
                files,
                ncloc AS codeLines,
                get_json_object(maintainability_issues, '$.total') AS maintainability_total,
                get_json_object(maintainability_issues, '$.HIGH') AS maintainability_high,
                get_json_object(maintainability_issues, '$.MEDIUM') AS maintainability_medium,
                get_json_object(maintainability_issues, '$.LOW') AS maintainability_low,
                get_json_object(reliability_issues, '$.total') AS reliability_total,
                get_json_object(reliability_issues, '$.HIGH') AS reliability_high,
                get_json_object(reliability_issues, '$.MEDIUM') AS reliability_medium,
                get_json_object(reliability_issues, '$.LOW') AS reliability_low,
                get_json_object(security_issues, '$.total') AS security_total,
                get_json_object(security_issues, '$.HIGH') AS security_high,
                get_json_object(security_issues, '$.MEDIUM') AS security_medium,
                get_json_object(security_issues, '$.LOW') AS security_low,
                security_hotspots AS securityHotspots,
                line_coverage AS lineCoverage,
                duplicated_lines,
                duplicated_lines_density
                FROM PIVOTED_TABLE;
                           """
                          )