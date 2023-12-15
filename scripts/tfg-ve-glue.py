import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue import DynamicFrame


def sparkSqlQuery(glueContext, query, mapping, transformation_ctx) -> DynamicFrame:
    for alias, frame in mapping.items():
        frame.toDF().createOrReplaceTempView(alias)
    result = spark.sql(query)
    return DynamicFrame.fromDF(result, glueContext, transformation_ctx)


args = getResolvedOptions(sys.argv, ["JOB_NAME"])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

# Script generated for node Amazon S3
AmazonS3_node1700937060089 = glueContext.create_dynamic_frame.from_options(
    format_options={
        "quoteChar": '"',
        "withHeader": True,
        "separator": ";",
        "optimizePerformance": False,
    },
    connection_type="s3",
    format="csv",
    connection_options={
        "paths": ["s3://raw-data-ve-eu-central-1/data/"],
        "recurse": True,
    },
    transformation_ctx="AmazonS3_node1700937060089",
)

# Script generated for node Change Schema
ChangeSchema_node1700937094143 = ApplyMapping.apply(
    frame=AmazonS3_node1700937060089,
    mappings=[
        (
            "comunidad autï¿½noma/provincia residencia",
            "string",
            "comunidad_autonoma/provincia",
            "string",
        ),
        ("tipo de vehï¿½culo", "string", "vehiculo", "string"),
        ("carburante", "string", "carburante", "string"),
        ("total,year,month", "string", "total/ano/mes", "string"),
    ],
    transformation_ctx="ChangeSchema_node1700937094143",
)

# Script generated for node SQL Query
SqlQuery466 = """
SELECT 
    split(`comunidad_autonoma/provincia`, '/')[0] AS comunidad_autonoma,
    split(`comunidad_autonoma/provincia`, '/')[1] AS provincia,
    vehiculo,
    carburante,
    split(`total/ano/mes`, ',')[0] AS total,
    split(`total/ano/mes`, ',')[1] AS ano,
    split(`total/ano/mes`, ',')[2] AS mes
FROM veData
WHERE carburante != 'TOTAL' and vehiculo is not null;
"""
SQLQuery_node1700937621405 = sparkSqlQuery(
    glueContext,
    query=SqlQuery466,
    mapping={"veData": ChangeSchema_node1700937094143},
    transformation_ctx="SQLQuery_node1700937621405",
)

# Script generated for node SQL Query
SqlQuery467 = """
SELECT 
    CASE 
        WHEN comunidad_autonoma = 'Andalucï¿½a' THEN 'Andalucía'
        WHEN comunidad_autonoma = 'Aragï¿½n' THEN 'Aragón'
        WHEN comunidad_autonoma = 'Castilla y Leï¿½n' THEN 'Castilla y León'
        WHEN comunidad_autonoma = 'Cataluï¿½a' THEN 'Catalunya'
        WHEN comunidad_autonoma = 'Murcia (Regiï¿½n de)' THEN 'Murcia'
        WHEN comunidad_autonoma = 'Paï¿½s Vasco' THEN 'País Vasco'
        WHEN comunidad_autonoma = 'Asturias (Principado de)' THEN 'Asturias'
        WHEN comunidad_autonoma = 'Madrid (Comunidad de)' THEN 'Madrid'
        WHEN comunidad_autonoma = 'Madrid (Comunidad de)' THEN 'Madrid'
        WHEN comunidad_autonoma = 'Navarra (Comunidad Foral de)' THEN 'Navarra'
        WHEN comunidad_autonoma = 'Rioja (La)' THEN 'Rioja'
        ELSE comunidad_autonoma
    END AS comunidad_autonoma,
    CASE 
        WHEN provincia = 'Almerï¿½a' THEN 'Almería'
        WHEN provincia = 'Cï¿½diz' THEN 'Cádiz'
        WHEN provincia = 'Cï¿½rdoba' THEN 'Córdoba'
        WHEN provincia = 'Jaï¿½n' THEN 'Jaén'
        WHEN provincia = 'Mï¿½laga' THEN 'Málaga'
        WHEN provincia = 'ï¿½vila' THEN 'Ávila'
        WHEN provincia = 'Leï¿½n' THEN 'León'
        WHEN provincia = 'Castellï¿½n' THEN 'Castellón'
        WHEN provincia = 'Cï¿½ceres' THEN 'Cáceres'
        WHEN provincia = 'Coruï¿½a (A)' THEN 'La Coruña'
        WHEN provincia = 'Rioja (La)' THEN 'Rioja'
        ELSE provincia
    END AS provincia,
    vehiculo,
    CASE 
        WHEN carburante = 'Elï¿½ctrico' THEN 'eléctrico'
        ELSE carburante
    END AS carburante,
    total, 
    ano, 
    mes
FROM veData;
"""
SQLQuery_node1700938286079 = sparkSqlQuery(
    glueContext,
    query=SqlQuery467,
    mapping={"veData": SQLQuery_node1700937621405},
    transformation_ctx="SQLQuery_node1700938286079",
)

# Script generated for node Change Schema
ChangeSchema_node1700938413030 = ApplyMapping.apply(
    frame=SQLQuery_node1700938286079,
    mappings=[
        ("comunidad_autonoma", "string", "comunidad_autonoma", "string"),
        ("provincia", "string", "provincia", "string"),
        ("vehiculo", "string", "vehiculo", "string"),
        ("carburante", "string", "carburante", "string"),
        ("total", "string", "total", "string"),
        ("ano", "string", "año", "string"),
        ("mes", "string", "mes", "string"),
    ],
    transformation_ctx="ChangeSchema_node1700938413030",
)

# Script generated for node Clean data  - ve
Cleandatave_node1701336191329 = glueContext.write_dynamic_frame.from_options(
    frame=ChangeSchema_node1700938413030,
    connection_type="s3",
    format="csv",
    connection_options={"path": "s3://clean-data-ve-eu-central-1", "partitionKeys": []},
    transformation_ctx="Cleandatave_node1701336191329",
)

job.commit()

