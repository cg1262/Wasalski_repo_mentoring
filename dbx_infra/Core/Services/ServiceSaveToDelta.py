from delta.tables import *
from pyspark.sql import SparkSession


def upserting_data(target_table_name: str, source_dataframe, target_column: str, source_column: str):
        
    spark = SparkSession.builder.getOrCreate()

        # upsert part
    target = DeltaTable.forName(
            spark,
            f"engineering_metrics.bronze.{target_table_name}"
        )

    source = source_dataframe

        #  https://docs.delta.io/latest/delta-update.html#upsert-into-a-table-using-merge
        #  https://stackoverflow.com/questions/64883915/delta-lake-merge-doesnt-update-schema-automatic-schema-evolution-enabled
                    # .withSchemaEvolution()\
    target.alias("target").merge(source.alias("source"),f"target.{target_column} = source.{source_column}")\
                .whenMatchedUpdate(set={col: f"source.{col}" for col in source.columns})\
                    .whenNotMatchedInsert(values={col: f"source.{col}" for col in source.columns})\
                        .execute()