"""Team No. 25
Team Project by Prakruti(Node 1),Aditi(Node 2),Shristi(Node 3) and Prachi(Node 4)
Node 1 ingestion: JSONL -> validated Iceberg pages and links on HDFS.
"""
import sys
from pyspark.sql import SparkSession, Window
from pyspark.sql import functions as F

if len(sys.argv) != 3 or sys.argv[1] not in ("0", "1"):
    raise SystemExit("Usage: node1_ingest.py <0|1> <hdfs-input-path>")

phase = int(sys.argv[1])
input_path = sys.argv[2]
spark = SparkSession.builder.appName("Node1-Ingestion").getOrCreate()
spark.sparkContext.setLogLevel("WARN")

DB = "iceberg_catalog.search"
PAGES = DB + ".pages"
LINKS = DB + ".valid_links"
CHANGES = DB + ".changed_docs"
RUNS = DB + ".ingested_phases"

# Same catalog and CREATE TABLE pattern as the Iceberg hands-on.
spark.sql(f"CREATE NAMESPACE IF NOT EXISTS {DB}")
spark.sql(f"""CREATE TABLE IF NOT EXISTS {PAGES} (
    doc_id STRING, url STRING, title STRING, text STRING,
    links ARRAY<STRING>, version INT
) USING iceberg""")
spark.sql(f"""CREATE TABLE IF NOT EXISTS {LINKS} (
    source_id STRING, target_id STRING
) USING iceberg""")
spark.sql(f"""CREATE TABLE IF NOT EXISTS {CHANGES} (
    phase INT, doc_id STRING, op STRING
) USING iceberg""")
spark.sql(f"""CREATE TABLE IF NOT EXISTS {RUNS} (
    phase INT, snapshot_id STRING
) USING iceberg""")

# Successful phases are marked only after ALL writes complete.
if spark.sql(f"SELECT * FROM {RUNS} WHERE phase = {phase}").count():
    print(f"Phase {phase} was already ingested. Nothing changed.")
    spark.stop()
    sys.exit(0)
if phase == 1 and not spark.sql(f"SELECT * FROM {RUNS} WHERE phase = 0").count():
    raise RuntimeError("Finish Phase 0 before Phase 1.")

# PERMISSIVE retains malformed JSON in the _corrupt_record column.
raw = (spark.read.option("mode", "PERMISSIVE")
       .option("columnNameOfCorruptRecord", "_corrupt_record")
       .json(input_path))
if "_corrupt_record" not in raw.columns:
    raw = raw.withColumn("_corrupt_record", F.lit(None).cast("string"))
if "links" not in raw.columns:
    raw = raw.withColumn("links", F.expr("CAST(array() AS ARRAY<STRING>)"))
if phase == 0:
    raw = raw.withColumn("op", F.lit("UPSERT"))
else:
    raw = raw.withColumn("op", F.upper(F.col("op")))

# The supplied files have no version field: phase is the version.
raw = raw.withColumn("version", F.lit(phase)).cache()
total = raw.count()

# doc_id is needed for all operations; the other fields are needed for UPSERT only. links is optional (a page can have no links)
identifier_ok = F.col("doc_id").isNotNull() & (F.trim("doc_id") != "")
fields_ok = F.lit(True)
for name in ("url", "title", "text"):
    fields_ok = fields_ok & F.col(name).isNotNull() & (F.trim(name) != "")
valid = raw.filter(
    F.col("_corrupt_record").isNull() & identifier_ok & (
        (F.col("op") == "DELETE") |
        ((F.col("op") == "UPSERT") & fields_ok)
    )
)
valid = valid.withColumn("links", F.coalesce("links", F.expr("array()")))
valid_count = valid.count()

# Highest version wins per doc_id. For same-version duplicates, the hash makes the tie-break deterministic
tie = F.sha2(F.to_json(F.struct("op", "url", "title", "text", "links")), 256)
window = Window.partitionBy("doc_id").orderBy(F.desc("version"), tie.desc())
incoming = (valid.withColumn("rn", F.row_number().over(window))
            .filter("rn = 1")
            .select("doc_id", "op", "url", "title", "text", "links", "version"))
incoming.createOrReplaceTempView("incoming")
unique_count = incoming.count()

print(f"Phase {phase}: input={total}, rejected={total-valid_count}, "
      f"duplicates={valid_count-unique_count}, unique={unique_count}")

# Detect which incoming documents actually differ from Iceberg's current version. Record their IDs for the indexing team
changed = spark.sql(f"""
    SELECT {phase} AS phase, s.doc_id, s.op
    FROM incoming s LEFT JOIN {PAGES} p ON s.doc_id = p.doc_id
    WHERE (s.op = 'DELETE' AND p.doc_id IS NOT NULL AND s.version >= p.version)
       OR (s.op = 'UPSERT' AND (p.doc_id IS NULL OR s.version > p.version))
""")
changed.createOrReplaceTempView("new_changes")
changed_count = changed.count()

# MERGE is idempotent: it only inserts new documents, updates newer versions, or deletes existing documentsS
spark.sql(f"""
    MERGE INTO {CHANGES} t USING new_changes s
    ON t.phase = s.phase AND t.doc_id = s.doc_id
    WHEN NOT MATCHED THEN INSERT (phase, doc_id, op)
    VALUES (s.phase, s.doc_id, s.op)
""")

spark.sql(f"""
    MERGE INTO {PAGES} t USING incoming s ON t.doc_id = s.doc_id
    WHEN MATCHED AND s.op = 'DELETE' AND s.version >= t.version THEN DELETE
    WHEN MATCHED AND s.op = 'UPSERT' AND s.version > t.version THEN UPDATE SET
        t.url = s.url, t.title = s.title, t.text = s.text,
        t.links = s.links, t.version = s.version
    WHEN NOT MATCHED AND s.op = 'UPSERT' THEN
        INSERT (doc_id, url, title, text, links, version)
        VALUES (s.doc_id, s.url, s.title, s.text, s.links, s.version)
""")

# Rebuild the valid edge list from the current Iceberg page set. The inner join removes links to deleted / nonexistent document
source_edges = spark.table(PAGES).select(
    F.col("doc_id").alias("source_id"),
    F.explode("links").alias("target_id")
)
existing_ids = spark.table(PAGES).select(F.col("doc_id").alias("target_id"))
clean_edges = (source_edges.join(existing_ids, "target_id", "inner")
               .select("source_id", "target_id").distinct())
old_edges = spark.table(LINKS)
added = clean_edges.exceptAll(old_edges).count()
removed = old_edges.exceptAll(clean_edges).count()
if added or removed:
    clean_edges.createOrReplaceTempView("clean_edges")
    spark.sql(f"""INSERT OVERWRITE {LINKS}
                  SELECT source_id, target_id FROM clean_edges""")

# A snapshot is created by Iceberg when the page table changes
row = spark.sql(f"""SELECT snapshot_id FROM {PAGES}.snapshots
                    ORDER BY committed_at DESC LIMIT 1""").first()
snapshot_id = str(row[0]) if row else "none"
spark.sql(f"INSERT INTO {RUNS} VALUES ({phase}, '{snapshot_id}')")

print(f"Changed docs: {changed_count}")
print(f"Pages in Iceberg: {spark.table(PAGES).count()}")
print(f"Valid links in Iceberg: {spark.table(LINKS).count()}")
print(f"Current pages snapshot: {snapshot_id}")
spark.stop()
