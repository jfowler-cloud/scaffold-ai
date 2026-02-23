import { useEffect, useState } from "react";

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
}

/**
 * Parse structured fields out of the formatted prompt text sent by Project Planner AI.
 * The prompt follows a known format with labelled lines like:
 *   Project: My App
 *   Architecture: Full Serverless
 *   Tech Stack: frontend: React, backend: Lambda
 *   Users: 1K-10K | Uptime: 99.9% | Data: <1GB
 */
function parsePrompt(prompt: string): PlannerImport {
  const lines = prompt.split("\n").map(l => l.trim());

  const get = (prefix: string) => {
    const line = lines.find(l => l.toLowerCase().startsWith(prefix.toLowerCase()));
    return line ? line.slice(prefix.length).trim() : "";
  };

  // Project name
  const projectName = get("Project:") || get("App:") || "Imported Project";

  // Architecture
  const architecture = get("Architecture:") || get("Recommended Architecture:");

  // Tech stack — parse "key: value, key: value" pairs
  const techStackRaw = get("Tech Stack:") || get("Stack:");
  const techStack: Record<string, string> = {};
  if (techStackRaw) {
    techStackRaw.split(",").forEach(pair => {
      const [k, ...rest] = pair.split(":");
      if (k && rest.length) techStack[k.trim()] = rest.join(":").trim();
    });
  }

  // Requirements line: "Users: 1K-10K | Uptime: 99.9% | Data: <1GB"
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

export function usePlannerImport() {
  const [plannerData, setPlannerData] = useState<PlannerImport | null>(null);
  const [isFromPlanner, setIsFromPlanner] = useState(false);

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const fromPlanner = urlParams.get("from") === "planner";

    if (fromPlanner) {
      setIsFromPlanner(true);

      const prompt = urlParams.get("prompt");
      if (prompt) {
        console.log("✅ Received prompt from Project Planner AI");
        setPlannerData(parsePrompt(prompt));
      }
    }
  }, []);

  return { plannerData, isFromPlanner };
}
