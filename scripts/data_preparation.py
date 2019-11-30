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
# Read enrichment files folder

df_payment = (sql.read.csv("work/schemas/data-payment_lookup-csv.csv"))
df_vendor = (sql.read.csv("work/schemas/data-vendor_lookup-csv.csv", header = "true"))
# Data cleansing on bad enrichment file layout

df_payment = df_payment.filter(df_payment._c0 != "A").filter(df_payment._c0 != "payment_type") \
.selectExpr("_c0 as payment_type", "_c1 as payment_lookup")
# Data enrichment incoming files with payment and vendor enrichment data

df = df.join(df_payment, on=['payment_type'], how='inner').join(df_vendor, on=['vendor_id'], how='inner')
# Data enrichment to calculate duration of the trips

df = df.withColumn("duration", \
    (F.unix_timestamp('dropoff_datetime', format="yyyy-MM-dd'T'HH:mm:ss").cast("long") \
     - F.unix_timestamp('pickup_datetime', format="yyyy-MM-dd'T'HH:mm:ss").cast("long"))/60)
# Register temp table

df.registerTempTable("data")
# Data enrichment to get weekday based on pickup_datetime

df = sql.sql(
  "select *, date_format(pickup_datetime, 'EEEE') as weekday, concat(pickup_latitude,', ',pickup_longitude) as pickup_location, concat(dropoff_latitude,', ',dropoff_longitude) as dropoff_location from data"
)
# Create timestamp and save file as parquet to processed folder

currentdate = datetime.now().strftime("%Y%m%d%H%M%s")
df.coalesce(1).write.format("json").save("work/data/inbox/result_process"+currentdate+".json")