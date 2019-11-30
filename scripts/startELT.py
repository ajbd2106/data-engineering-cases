import pyspark
import pyspark.sql.functions as F
from pyspark.sql.types import StringType, LongType, IntegerType
from pyspark.sql import SQLContext
from datetime import datetime
# Initialize Spark ans SparkSQL context using default confs

sc = pyspark.SparkContext.getOrCreate()
sql = SQLContext(sc)
# Read incoming files folder

df = (sql.read.json("../inbox"))

# Create timestamp and save file as parquet to processed folder

currentdate = datetime.now().strftime("%Y%m%d%H%M%s")
df.coalesce(1).write.parquet("work/data/inbox_elt/result_process"+currentdate)