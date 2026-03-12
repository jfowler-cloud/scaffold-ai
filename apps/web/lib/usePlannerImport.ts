import { useEffect, useState } from "react";
import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import { DynamoDBDocumentClient, GetCommand } from "@aws-sdk/lib-dynamodb";
import { fetchAuthSession } from "aws-amplify/auth";

export interface ReviewFinding {
  category: string;
  findings: string[];
  recommendations: string[];
  risk_level: string;
}

export interface PlannerImport {
  projectName: string;
  description: string;
  architecture: string;
  techStack: Record<string, string>;
  requirements: {
    users: string;
    uptime: string;
    dataSize: string;
  };
  reviewFindings?: ReviewFinding[];
  reviewSummary?: string;
}

const HANDOFF_TABLE = "project-planner-handoff";

/**
 * Parse structured fields out of the formatted prompt text sent by Project Planner AI.
 */
function parsePrompt(prompt: string): PlannerImport {
  const lines = prompt.split("\n").map(l => l.trim());

  const get = (prefix: string) => {
    const line = lines.find(l => l.toLowerCase().startsWith(prefix.toLowerCase()));
    return line ? line.slice(prefix.length).trim() : "";
  };

  const projectName = get("Project:") || get("App:") || "Imported Project";
  const architecture = get("Architecture:") || get("Recommended Architecture:");

  const techStackRaw = get("Tech Stack:") || get("Stack:");
  const techStack: Record<string, string> = {};
  if (techStackRaw) {
    techStackRaw.split(",").forEach(pair => {
      const [k, ...rest] = pair.split(":");
      if (k && rest.length) techStack[k.trim()] = rest.join(":").trim();
    });
  }

  const reqLine = lines.find(l => l.toLowerCase().includes("users:") && l.includes("|")) || "";
  const reqParts = Object.fromEntries(
    reqLine.split("|").map(p => {
      const [k, ...v] = p.split(":");
      return [k.trim().toLowerCase(), v.join(":").trim()];
    })
  );

  return {
    projectName,
    description: prompt,
    architecture,
    techStack,
    requirements: {
      users: reqParts["users"] || "",
      uptime: reqParts["uptime"] || "",
      dataSize: reqParts["data"] || reqParts["data size"] || "",
    },
  };
}

async function fetchPlanFromDynamoDB(sessionId: string): Promise<PlannerImport | null> {
  const session = await fetchAuthSession();
  if (!session.credentials) return null;

  const region = import.meta.env.VITE_AWS_REGION || "us-east-1";
  const ddb = DynamoDBDocumentClient.from(
    new DynamoDBClient({ region, credentials: session.credentials })
  );

  const resp = await ddb.send(new GetCommand({
    TableName: HANDOFF_TABLE,
    Key: { sessionId },
  }));

  const item = resp.Item;
  if (!item) return null;

  return {
    projectName: item.project_name ?? "Imported Project",
    description: item.description ?? "",
    architecture: item.architecture ?? "",
    techStack: item.tech_stack ?? {},
    requirements: item.requirements ?? { users: "", uptime: "", dataSize: "" },
    reviewFindings: item.review_findings,
    reviewSummary: item.review_summary,
  };
}

export function usePlannerImport() {
  const [plannerData, setPlannerData] = useState<PlannerImport | null>(null);
  const [isFromPlanner, setIsFromPlanner] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const fromPlanner = urlParams.get("from") === "planner";

    if (fromPlanner) {
      setIsFromPlanner(true);

      const sessionId = urlParams.get("session");
      if (sessionId) {
        setIsLoading(true);

        fetchPlanFromDynamoDB(sessionId)
          .then(data => {
            if (data) {
              console.log("Received plan from Project Planner AI via DynamoDB");
              setPlannerData(data);
            } else {
              throw new Error("Plan not found in DynamoDB");
            }
          })
          .catch(error => {
            console.warn("DynamoDB handoff unavailable, falling back to prompt parsing:", error.message);
            const prompt = urlParams.get("prompt");
            if (prompt) {
              setPlannerData(parsePrompt(prompt));
            }
          })
          .finally(() => {
            setIsLoading(false);
          });
      } else {
        // Fallback to old prompt-based method
        const prompt = urlParams.get("prompt");
        if (prompt) {
          setPlannerData(parsePrompt(prompt));
        }
      }
    }
  }, []);

  return { plannerData, isFromPlanner, isLoading };
}
