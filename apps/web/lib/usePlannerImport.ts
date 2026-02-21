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
    // Check if coming from Project Planner AI
    const urlParams = new URLSearchParams(window.location.search);
    const fromPlanner = urlParams.get("from") === "planner";

    if (fromPlanner) {
      setIsFromPlanner(true);

      // Try to get data from localStorage
      const storedData = localStorage.getItem("plannerExport");
      if (storedData) {
        try {
          const data = JSON.parse(storedData);
          setPlannerData(data);

          // Clear the data after reading (one-time use)
          localStorage.removeItem("plannerExport");

          // Show notification
          console.log("✅ Imported project plan from Project Planner AI");
        } catch (error) {
          console.error("Failed to parse planner data:", error);
        }
      }
    }
  }, []);

  return { plannerData, isFromPlanner };
}
