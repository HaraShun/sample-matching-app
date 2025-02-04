import { generateClient } from "aws-amplify/api";
import { createAIHooks } from "@aws-amplify/ui-react-ai";
import type { Schema } from "../amplify/amplify/data/resource";

export const client = generateClient<Schema>({ authMode: "userPool" });
export const { useAIConversation } = createAIHooks(client);