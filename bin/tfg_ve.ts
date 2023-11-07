#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import * as fs from 'fs';
import { TfgVeStack } from '../lib/tfg_ve-stack';

const app = new cdk.App();

//get context params from the CDK application
const env = 'tfg-ve-env';

//get context from config 
const context = JSON.parse(fs.readFileSync('./conf/env.json', 'utf-8'));

//retrieve the account and region to your CDK stack
const account = context[env].account;
const region = context[env].region;

new TfgVeStack(app, 'tfg-ve-stack', {
  //envName: env,
  env: { 
    account: account,
    region: region
  }
});
