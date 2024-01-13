import os
import pandas as pd
import boto3

profile_name = 'default'
region_name = 'eu-central-1'

session = boto3.Session(profile_name=profile_name, region_name=region_name)

def encode_csv_to_unicode(file_path):
    
    # Leer el archivo CSV en un DataFrame de pandas
    df = pd.read_csv(file_path, encoding='latin-1')

    # Agregar nueva columna al archivo CSV
    df['Year'] = year 
    df['month'] = str(month).zfill(2)

    # Guardar el DataFrame codificado en un nuevo archivo CSV
    encoded_file_path = 'encoded_file.csv'
    df.to_csv(encoded_file_path, index=False)
    
    return encoded_file_path

def upload_file_to_s3(bucket_name, file_path, s3_key, kms_key_arn):
    s3 = boto3.client('s3')
    
    # Subir el archivo al bucket de AWS S3
    s3.upload_file(file_path, bucket_name, s3_key, ExtraArgs={'SSEKMSKeyId': kms_key_arn, 'ServerSideEncryption': 'aws:kms'})
    
    print(f"File uploaded to S3 bucket: s3://{bucket_name}/{s3_key}")

bucket_name = 'raw-data-ve-eu-central-1'
s3_key_prefix = 'data/'
kms_key_arn = 'arn:aws:kms:eu-central-1:766973746059:key/4ae649c9-0b3f-4080-8344-2b0c7696e44a'

# Recorrer la estructura de directorios
for year in range(2016, 2024):
    for month in range(1, 13):
        # Generar la ruta del archivo basada en la estructura de directorios
        file_path = f"/Users/I559673/Documents/Informatica/tfg_ve/data/{year}/{str(month).zfill(2)}/InformePredefinido_Parque{year}{str(month).zfill(2)}.csv"
        
        # Comprobar si el archivo existe
        if os.path.exists(file_path):
            # Codificar el archivo CSV a Unicode
            encoded_file_path = encode_csv_to_unicode(file_path)
            
            # Generar la clave de S3 basada en la estructura de directorios
            s3_key = f"{s3_key_prefix}{year}/{str(month).zfill(2)}/informe_VE_{year}_{str(month).zfill(2)}.csv"
            
            # Subir el archivo codificado a AWS S3
            upload_file_to_s3(bucket_name, encoded_file_path, s3_key, kms_key_arn)
        else:
            print(f"File does not exist: {file_path}")
