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
                TRY_CAST(source.line AS int) AS line,
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
                TRY_CAST(source.creationDate AS timestamp) AS creation_date,
                TRY_CAST(source.updateDate AS timestamp) AS update_date,
                source.type AS type,
                source.organization AS organization,
                source.externalRuleEngine AS external_rule_engine,
                source.cleanCodeAttribute AS clean_code_attribute,
                source.cleanCodeAttributeCategory AS clean_code_attribute_category,
                source.impacts AS impacts,
                source.issueStatus AS issue_status,
                source.projectName AS project_name,
                source.resolution AS resolution,
                TRY_CAST(source.closeDate AS timestamp) AS close_date,
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
                duplicated_lines_density,
                current_timestamp() AS timestamp
                FROM PIVOTED_TABLE;
                           """
                          )
    # def measures_component(self):
    #         self.spark.sql("""
    #         MERGE INTO engineering_metrics.silver.sonarcloud_measures_component AS target
    #         USING (

    #         WITH exploded AS (
    #             SELECT
    #             t.id,
    #             t.key,
    #             t.name,
    #             m.metric,
    #             m.value
    #             FROM engineering_metrics.bronze.sonarcloud_measures_component t
    #             LATERAL VIEW EXPLODE(
    #             from_json(t.measures, 'array<struct<metric:string,value:string>>')
    #             ) m AS m
    #         ),

    #         pivoted AS (
    #             SELECT *
    #             FROM exploded
    #             PIVOT (
    #             first(value) FOR metric IN (
    #                 'files',
    #                 'ncloc',
    #                 'maintainability_issues',
    #                 'reliability_issues',
    #                 'security_hotspots',
    #                 'security_issues',
    #                 'line_coverage',
    #                 'duplicated_lines',
    #                 'duplicated_lines_density'
    #             )
    #             )
    #         )

    #         SELECT
    #             id,
    #             key,
    #             name,

    #             TRY_CAST(`files` AS INT) AS files,
    #             TRY_CAST(`ncloc` AS INT) AS codelines,

    #             -- Maintainability
    #             TRY_CAST(get_json_object(`maintainability_issues`, '$.total') AS INT) AS maintainability_total,
    #             TRY_CAST(get_json_object(`maintainability_issues`, '$.HIGH') AS INT) AS maintainability_high,
    #             TRY_CAST(get_json_object(`maintainability_issues`, '$.MEDIUM') AS INT) AS maintainability_medium,
    #             TRY_CAST(get_json_object(`maintainability_issues`, '$.LOW') AS INT) AS maintainability_low,

    #             -- Reliability
    #             TRY_CAST(get_json_object(`reliability_issues`, '$.total') AS INT) AS reliability_total,
    #             TRY_CAST(get_json_object(`reliability_issues`, '$.HIGH') AS INT) AS reliability_high,
    #             TRY_CAST(get_json_object(`reliability_issues`, '$.MEDIUM') AS INT) AS reliability_medium,
    #             TRY_CAST(get_json_object(`reliability_issues`, '$.LOW') AS INT) AS reliability_low,

    #             -- Security
    #             TRY_CAST(get_json_object(`security_issues`, '$.total') AS INT) AS security_total,
    #             TRY_CAST(get_json_object(`security_issues`, '$.HIGH') AS INT) AS security_high,
    #             TRY_CAST(get_json_object(`security_issues`, '$.MEDIUM') AS INT) AS security_medium,
    #             TRY_CAST(get_json_object(`security_issues`, '$.LOW') AS INT) AS security_low,

    #             TRY_CAST(`security_hotspots` AS INT) AS securityhotspots,
    #             TRY_CAST(`line_coverage` AS FLOAT) AS linecoverage,
    #             TRY_CAST(`duplicated_lines` AS INT) AS duplicated_lines,
    #             TRY_CAST(`duplicated_lines_density` AS FLOAT) AS duplicated_lines_density,

    #             current_timestamp() AS timestamp,

    #             -- Upsert key to identify records
    #             CONCAT(id, '_', key) AS upsert_key

    #         FROM pivoted

    #         ) AS source
    #         ON target.upsert_key = source.upsert_key

    #         WHEN MATCHED THEN UPDATE SET
    #         target.id = source.id,
    #         target.key = source.key,
    #         target.name = source.name,
    #         target.files = source.files,
    #         target.codelines = source.codelines,
    #         target.maintainability_total = source.maintainability_total,
    #         target.maintainability_high = source.maintainability_high,
    #         target.maintainability_medium = source.maintainability_medium,
    #         target.maintainability_low = source.maintainability_low,
    #         target.reliability_total = source.reliability_total,
    #         target.reliability_high = source.reliability_high,
    #         target.reliability_medium = source.reliability_medium,
    #         target.reliability_low = source.reliability_low,
    #         target.security_total = source.security_total,
    #         target.security_high = source.security_high,
    #         target.security_medium = source.security_medium,
    #         target.security_low = source.security_low,
    #         target.securityhotspots = source.securityhotspots,
    #         target.linecoverage = source.linecoverage,
    #         target.duplicated_lines = source.duplicated_lines,
    #         target.duplicated_lines_density = source.duplicated_lines_density

    #         WHEN NOT MATCHED THEN INSERT (
    #         id, key, name,
    #         files, codelines,
    #         maintainability_total, maintainability_high, maintainability_medium, maintainability_low,
    #         reliability_total, reliability_high, reliability_medium, reliability_low,
    #         security_total, security_high, security_medium, security_low,
    #         securityhotspots, linecoverage, duplicated_lines, duplicated_lines_density,
    #         upsert_key
    #         )
    #         VALUES (
    #         source.id,
    #         source.key,
    #         source.name,
    #         source.files,
    #         source.codelines,
    #         source.maintainability_total,
    #         source.maintainability_high,
    #         source.maintainability_medium,
    #         source.maintainability_low,
    #         source.reliability_total,
    #         source.reliability_high,
    #         source.reliability_medium,
    #         source.reliability_low,
    #         source.security_total,
    #         source.security_high,
    #         source.security_medium,
    #         source.security_low,
    #         source.securityhotspots,
    #         source.linecoverage,
    #         source.duplicated_lines,
    #         source.duplicated_lines_density,
    #         source.upsert_key
    #         )
    #         """)

