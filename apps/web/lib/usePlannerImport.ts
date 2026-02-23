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

export function usePlannerImport() {
  const [plannerData, setPlannerData] = useState<PlannerImport | null>(null);
  const [isFromPlanner, setIsFromPlanner] = useState(false);

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const fromPlanner = urlParams.get("from") === "planner";
    
    if (fromPlanner) {
      setIsFromPlanner(true);
      
      // Get prompt from URL parameter
      const prompt = urlParams.get("prompt");
      
      if (prompt) {
        console.log("✅ Received prompt from Project Planner AI");
        
        // The prompt is already decoded by URLSearchParams
        // Create plannerData from the prompt
        setPlannerData({
          projectName: "Imported Project",
          description: prompt,
          architecture: "",
          techStack: {},
          requirements: { users: "", uptime: "", dataSize: "" }
        });
      }
    }
  }, []);

  return { plannerData, isFromPlanner };
}
