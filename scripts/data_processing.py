import os
import pandas as pd
import boto3

profile_name = 'tfg-ve'
region_name = 'eu-central-1'

session = boto3.Session(profile_name=profile_name, region_name=region_name)

def encode_csv_to_unicode(file_path):
 
    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv(file_path, encoding='latin-1', delimiter='\t')
      # Add a new column with the file path

    # Add new column to the csv
    df['Year'] = year, month 
    df['month'] = month

    # Save the encoded DataFrame to a new CSV file
    encoded_file_path = 'encoded_file.csv'
    df.to_csv(encoded_file_path, sep='\t', index=False)
    
    return encoded_file_path

def upload_file_to_s3(bucket_name, file_path, s3_key, kms_key_arn):
    s3 = boto3.client('s3')
    print(s3_key)
    
    # Upload the file to AWS S3 bucket
    s3.upload_file(file_path, bucket_name, s3_key, ExtraArgs={'SSEKMSKeyId': kms_key_arn, 'ServerSideEncryption': 'aws:kms'})
    
    print(f"File uploaded to S3 bucket: s3://{bucket_name}/{s3_key}")

bucket_name = 'raw-data-ve-eu-central-1'
s3_key_prefix = 'data/'
kms_key_arn = 'arn:aws:kms:eu-central-1:766973746059:key/4ae649c9-0b3f-4080-8344-2b0c7696e44a'

# Loop through the directory structure
for year in range(2016, 2024):
    for month in range(1, 13):
        # Generate the file path based on the directory structure
        file_path = f"/Users/I559673/Documents/Informatica/tfg_ve/data/{year}/{month}/InformePredefinido_Parque{year}{month}.csv"
        
        # Check if the file exists
        if os.path.exists(file_path):
            # Step 1: Encode the CSV file to Unicode
            encoded_file_path = encode_csv_to_unicode(file_path)
            
            # Generate the S3 key based on the directory structure
            s3_key = f"{s3_key_prefix}{year}/{month:}/informe_VE_{year}_{month}.csv"
            
            # Step 2: Upload the encoded file to AWS S3
            upload_file_to_s3(bucket_name, encoded_file_path, s3_key, kms_key_arn)
        else:
            print(f"File does not exist: {file_path}")
