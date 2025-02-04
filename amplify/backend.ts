import { defineBackend } from '@aws-amplify/backend';
import { auth } from './auth/resource';
import { data } from './data/resource';
import { PolicyStatement } from 'aws-cdk-lib/aws-iam';
import * as cdk from 'aws-cdk-lib';

/**
 * @see https://docs.amplify.aws/react/build-a-backend/ to add storage, functions, and more
 */
const backend = defineBackend({
  auth,
  data,
});

const KnowledgeBaseDataSource =
  backend.data.resources.graphqlApi.addHttpDataSource(
    "KnowledgeBaseDataSource",
    `https://bedrock-agent-runtime.ap-northeast-1.amazonaws.com`,
    {
      authorizationConfig: {
        signingRegion: "ap-northeast-1",
        signingServiceName: "bedrock",
      },
    },
  );

KnowledgeBaseDataSource.grantPrincipal.addToPrincipalPolicy(
  new PolicyStatement({
    resources: [
      `arn:aws:bedrock:ap-northeast-1:133000800802:knowledge-base/B2TTXCTYTP`
    ],
    actions: ["bedrock:Retrieve"],
  }),
);