class ServiceSilver:
    def __init__(self, spark):
        self.spark = spark

    def incidents(self):
        self.spark.sql(
            """
            INSERT OVERWRITE TABLE engineering_metrics.silver.pagerduty_incidents
            SELECT
                source.incident_number AS incident_number,
                source.title AS title,
                source.description AS description,
                TRY_CAST(source.created_at AS timestamp) AS created_at,
                TRY_CAST(source.updated_at AS timestamp) AS updated_at,
                source.status AS status,
                source.service AS service,
                source.assignments AS assignments,
                source.assigned_via AS assigned_via,
                TRY_CAST(source.last_status_change_at AS timestamp) AS last_status_change_at,
                TRY_CAST(source.resolved_at AS timestamp) AS resolved_at,
                source.first_trigger_log_entry AS first_trigger_log_entry,
                source.alert_counts AS alert_counts,
                TRY_CAST(source.is_mergeable AS boolean) AS is_mergeable,
                source.incident_type AS incident_type,
                source.escalation_policy AS escalation_policy,
                source.teams AS teams,
                source.pending_actions AS pending_actions,
                source.acknowledgements AS acknowledgements,
                source.basic_alert_grouping AS basic_alert_grouping,
                source.alert_grouping AS alert_grouping,
                source.last_status_change_by AS last_status_change_by,
                source.priority AS priority,
                source.resolve_reason AS resolve_reason,
                source.incidents_responders AS incidents_responders,
                source.responder_requests AS responder_requests,
                source.subscriber_requests AS subscriber_requests,
                source.urgency AS urgency,
                source.id AS id,
                source.type AS type,
                source.summary AS summary,
                source.self AS self,
                source.html_url AS html_url,
                source.incident_key AS incident_key
            FROM engineering_metrics.bronze.pagerduty_incidents AS source
            """
        )
