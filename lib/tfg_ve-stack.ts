import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as s3 from 'aws-cdk-lib/aws-s3';
import {aws_kms as kms} from 'aws-cdk-lib';
import {aws_iam as iam} from 'aws-cdk-lib';
import {aws_glue as glue} from 'aws-cdk-lib';
import { PolicyStatement } from 'aws-cdk-lib/aws-iam';



export class TfgVeStack extends cdk.Stack {
    dataLakeUser: cdk.aws_iam.User;
    constructor(scope: Construct, id: string, props?: cdk.StackProps) {
        super(scope, id, props);


        const stackName = cdk.Names.uniqueId(this);
        const region = this.region;
        
        const kmsKey = this.createKmsKey();

        //create an IAM user data-lake
        this.dataLakeUser = this.createIamUser();

        const rawDataVeBucket = this.createS3Bucket(kmsKey, this.dataLakeUser, 'raw-data-ve-');
        const cleanDataVeBucket = this.createS3Bucket(kmsKey, this.dataLakeUser, 'clean-data-ve-');

        const glueRoleRawData = this.createGlueRole('ve-glue-role-s3-raw-data', kmsKey, rawDataVeBucket);

        this.createGlueCrawler('ve-db', 've-crawler',
         glueRoleRawData.roleArn, rawDataVeBucket.bucketName, 'snapshot/');

  }

    //declare method createKmsKey
    private createKmsKey(){
        return new kms.Key(this, TfgVeStack + 'key', {
            alias: 'alias/' + this.stackName + '-' + this.region,
            description: 'KMS Key for encrypting the objects in the s3 buckets',
            removalPolicy: cdk.RemovalPolicy.DESTROY,
            enableKeyRotation: true
        })
    }

    //declare method to createS3Bucket
    private createS3Bucket(kmsKey: cdk.aws_kms.Key, user: iam.User, bucketName: string){
        const s3Bucket = new s3.Bucket(this, bucketName + '--' + this.region,{
            bucketName: bucketName + this.region,
            blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
            encryption: s3.BucketEncryption.KMS,
            encryptionKey: kmsKey,
            removalPolicy: cdk.RemovalPolicy.DESTROY,
            accessControl: s3.BucketAccessControl.BUCKET_OWNER_FULL_CONTROL
        });

        const secureTransportPolicy = new iam.PolicyStatement({
            sid: 'DenyInsecureCommunications',
            effect: iam.Effect.DENY,
            actions: ['s3:*'],
            principals: [new iam.StarPrincipal()],
            resources: [s3Bucket.bucketArn, `${s3Bucket.bucketArn}/*`],
            conditions: {
                Bool: {
                    'aws:SecureTransport': 'false',
                }
            }
        });

        const tls12OrAbove = new iam.PolicyStatement({
            sid: 'DenyTlsBelow1_2',
            effect: iam.Effect.DENY,
            actions: ['s3:*'],
            principals: [new iam.StarPrincipal()],
            resources: [s3Bucket.bucketArn, `${s3Bucket.bucketArn}/*`],
            conditions: {
                NumericLessThan: {
                    's3:TlsVersion': '1.2',
                },
            }
        });

        s3Bucket.addToResourcePolicy(secureTransportPolicy);
        s3Bucket.addToResourcePolicy(tls12OrAbove);
        s3Bucket.grantReadWrite(this.dataLakeUser);

        return s3Bucket;
    }

    private createIamUser(){
        const user = new iam.User(this, 'DataLakeUser', {
            userName: 'data-lake-user',
        });

        const listBucketPolicy = new iam.PolicyStatement({
            effect: iam.Effect.ALLOW,
            actions: [
                's3:ListAllMyBuckets',
                's3:GetAccountPublicAccessBlock',
                's3:GetBucketPublicAccessBlock',
                's3:GetBucketPolicyStatus',
                's3:GetBucketAcl',
                's3:ListAccessPoints'
                ],
            resources: ['*'],
        });

        user.addToPolicy(listBucketPolicy)

        return user;
    }

    private createGlueRole(roleName: string, kmsKey:kms.Key, s3Bucket: s3.Bucket){
        const glueRole = new iam.Role(this, roleName, {
            roleName: roleName,
            assumedBy: new iam.ServicePrincipal('glue.amazonaws.com')
        });

        glueRole.addManagedPolicy(
            iam.ManagedPolicy.fromAwsManagedPolicyName("service-role/AWSGlueServiceRole")
        );

        const allowGlueRoleS3Access = new iam.PolicyStatement({
            sid: 'AllowUserAccess', 
            effect: iam.Effect.ALLOW, 
            principals: [
                new iam.ArnPrincipal(glueRole.roleArn),
            ],
            actions: [
                's3:GetObject',
                's3:PutObject',
                's3:GetObjectTagging',
                's3:GetObjectAcl',
                's3:ListBucket',
                's3:GetBucketLocation'
            ],
            resources: [
                s3Bucket.bucketArn + '/*',
                s3Bucket.bucketArn,
            ],
        });

        s3Bucket.addToResourcePolicy(allowGlueRoleS3Access);

        //grant glue role permission to decrypt data on s3
        kmsKey.grantDecrypt(glueRole);

        return glueRole;
    }

    private createGlueCrawler(dbName: string, crawlerName: string, glueRoleArn: string, bucketName: string, s3Path: string) {
        const dataLakeDB = new glue.CfnDatabase(this, dbName, {
            catalogId: this.account,
            databaseInput: {
                name: dbName
            }
        });

        const classifierName = 'CleanDataCsvClassifier'
        new glue.CfnClassifier(this, classifierName, {
            csvClassifier: {
                name: classifierName,
                containsHeader: 'PRESENT',
                delimiter: ';',
                quoteSymbol: '"'
            }
        });

        const dataLakeCrawler = new glue.CfnCrawler(this, crawlerName, {
            role: glueRoleArn,
            name: crawlerName,
            databaseName: dbName,
            classifiers: [classifierName],
            targets: {
                s3Targets: [
                    {
                        path: 's3://' + bucketName + '/' + s3Path
                    }
                ]
            },
            schemaChangePolicy: {
                updateBehavior: 'UPDATE_IN_DATABASE',
                deleteBehavior: 'DELETE_FROM_DATABASE'
            },
            configuration: '{"Version": 1.0, "Grouping": { "TableLevelConfiguration": 3 }}',
            schedule: {
                scheduleExpression: "cron(0 1 * * ? *)",
            }
        });

        dataLakeCrawler.addDependency(dataLakeDB);
    }
}

