class ServiceSilver:
    def __init__(self, spark):
        self.spark = spark

    def projects(self):
        """
        """
        self.spark.sql(
            """
            insert overwrite TABLE engineering_metrics.silver.mend_projects
            select
            UUID as project_id,
            NAME as project_name,
            PATH,
            applicationname as product_name,
            applicationuuid as product_id
            from engineering_metrics.bronze.mend_projects;
            """
            )
    def products(self):
        """
        """
        self.spark.sql(
            """
            insert overwrite TABLE engineering_metrics.silver.mend_products
            select
            uuid as product_id,
            name as product_name
            FROM engineering_metrics.bronze.mend_applications;
            """
            )
        # TRY_PARSE_JSON(versionedRepresentations):created['1']::TIMESTAMP AS created,
    def alert_types(self):
        """
        """
        self.spark.sql(
            """
        insert overwrite TABLE engineering_metrics.silver.mend_alert_types
        SELECT
        TRY_PARSE_JSON(policies):violations::string AS policies_violations,
        TRY_PARSE_JSON(securityperlibrary):librariesWithCritical::string AS libraries_critical,
        TRY_PARSE_JSON(securityperlibrary):librariesWithHigh::string AS libraries_high,
        TRY_PARSE_JSON(securityperlibrary):librariesWithMedium::string AS libraries_medium,
        TRY_PARSE_JSON(securityperlibrary):librariesWithLow::string AS libraries_low,
        TRY_PARSE_JSON(securityperlibrary):total::string AS violated_libraries,
        TRY_PARSE_JSON(securitypervulnerability):critical::string AS vulnerabilities_critical,
        TRY_PARSE_JSON(securitypervulnerability):high::string AS vulnerabilities_high,
        TRY_PARSE_JSON(securitypervulnerability):medium::string AS vulnerabilities_medium,
        TRY_PARSE_JSON(securitypervulnerability):low::string AS vulnerabilities_low,
        TRY_PARSE_JSON(securitypervulnerability):total::string AS violated_vulnerabilities
        FROM engineering_metrics.bronze.MEND_ALERT_TYPES;
            """
            )
        
    def alerts_severity(self):
        """
        """
        self.spark.sql(
            """
            insert overwrite table engineering_metrics.silver.mend_alerts_severity
            select
                total string,
                critical string,
                high string,
                medium string,
                low string
            from engineering_metrics.bronze.mend_alerts_severity;
            """
            )
        
    def security_alerts_per_library(self):
        """
        """
        self.spark.sql(
            """
            insert overwrite table engineering_metrics.silver.mend_security_alerts_per_library
            SELECT
            uuid as library_id,
            name as library_name,
            libraryType as library_type,
            status,
            severity,
            total,
            criticalNum as critical_num,
            highNum as high_num,
            mediumNum as medium_num,
            lowNum as low_num,
            try_parse_json(project):uuid::string AS project_id,
            try_parse_json(product):uuid::string AS product_id,
            lastScan as last_scan,
            detectedAt as detected_at,
            publishedAt as published_at,
            lastCveUpdatedAt as last_cve_updated_at,
            modifiedAt as modifiedat
            FROM engineering_metrics.bronze.mend_alerts_per_library;
           """
        )
        
    def project_due_diligence(self):
        """
        """
        self.spark.sql(
            """
            insert overwrite table engineering_metrics.silver.mend_project_due_diligence
            SELECT 
            uuid,
            name,
            try_parse_json(license):name::string AS license_name,
            try_parse_json(license):uuid::string AS license_uuid,
            try_parse_json(project):name::string AS project_name,
            try_parse_json(project):uuid::string AS project_uuid,
            try_parse_json(component):name::string AS component_name,
            try_parse_json(component):uuid::string AS component_uuid,
            try_parse_json(component):artifactId::string AS artifact_id,
            try_parse_json(riskscore):riskScore::string AS risk_score
            from engineering_metrics.bronze.mend_project_due_diligence
            """
           )
        
    def vulnerabilities_project(self):
        """
        """
        self.spark.sql(
            """
            insert overwrite table engineering_metrics.silver.mend_vulnerabilities_project
            SELECT
            uuid,
            productname as product_name,
            projectname as project_name,
            vulnerableLibraries as vulnerable_libraries
            FROM engineering_metrics.bronze.mend_vulnerabilities_project
             """
             )
        
    def labels(self):
        """
        """
        self.spark.sql(
            """
            insert overwrite table engineering_metrics.silver.mend_labels
            SELECT
            uuid as label_id,
            value,
            system,
            projects as project_count,
            createdat as created_at,
            createdby as created_by,
            applications as product_count 
            FROM engineering_metrics.bronze.MEND_LABELS
            """
            )
        
    def security_alerts_per_project(self):
        """
        """
        self.spark.sql(
            """
            insert overwrite table engineering_metrics.silver.mend_security_alerts_per_project
            SELECT
            uuid,
            name,
            type,
            exploitable,
            try_parse_json(topfix):id::string AS fix_id,
            try_parse_json(topfix):date::timestamp AS fix_date,
            try_parse_json(topfix):fixResolution::string AS fix_resolution,
            try_parse_json(topfix):type::string AS fix_type,
            try_parse_json(project):name::string AS project_name,
            try_parse_json(project):uuid::string AS project_id,
            try_parse_json(component):artifactId::string AS artifact_id,
            try_parse_json(application):name::string AS product_name,
            try_parse_json(application):uuid::string AS product_id,
            try_parse_json(detected_at)::timestamp AS detected_at,
            try_parse_json(modified_at)::timestamp AS modified_at,
            try_parse_json(status)::string AS finding_status,
            try_parse_json(vulnerability):score::float AS score,
            try_parse_json(vulnerability):severity::string AS severity,
            DATEDIFF(DAY, detected_at::timestamp, CURRENT_TIMESTAMP()) AS detected_age_days,
            DATEDIFF(DAY, try_parse_json(topfix):date::timestamp, CURRENT_TIMESTAMP()) AS fix_age_days
            FROM engineering_metrics.bronze.mend_alerts_per_project
            """
            )
        
    def libraries(self):
        """
        """
        self.spark.sql(
            """
            insert overwrite table engineering_metrics.silver.mend_libraries
            SELECT
            project_uuid as project_id,
            uuid as library_id,
            name as library_name,
            purl as p_url,
            type,
            groupid as group_id,
            version,
            extension,
            artifactid as artifact_id,
            classifier,
            librarytype as library_type,
            directdependency as direct_dependency
            FROM engineering_metrics.bronze.mend_libraries
            """
            )
        
    def license_policy_violations(self):
        """
        """
        self.spark.sql(
            """
        insert overwrite table engineering_metrics.silver.mend_license_policy_violations
        SELECT
        uuid as policy_id,
        name as policy_name,
        type,
        try_parse_json(project):uuid::string AS project_id,
        try_parse_json(status)::string AS status,
        CAST(try_parse_json(detected_At)::string AS timestamp) AS detected_at,
        CAST(try_parse_json(modified_At)::string AS timestamp) AS modified_at,
        try_parse_json(component):uuid::string AS library_id,
        try_parse_json(component):name::string AS library_name
        FROM engineering_metrics.bronze.mend_license_policy_violations
                    """
            )