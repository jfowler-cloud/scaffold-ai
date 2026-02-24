"use client";

import Button from "@cloudscape-design/components/button";

interface PlannerRefineButtonProps {
  architecture: any;
  securityScore?: number;
}

export function PlannerRefineButton({ architecture, securityScore }: PlannerRefineButtonProps) {
  const handleRefine = () => {
    // Prepare data to send back to planner
    const refinementData = {
      architecture_json: architecture,
      security_score: securityScore,
      feedback: securityScore && securityScore < 70 
        ? "Security score is below threshold. Consider reviewing security requirements."
        : "Architecture looks good. Consider refining based on cost or scalability needs.",
    };
    
    // For now, just copy to clipboard and open planner
    const feedbackText = `Architecture Feedback from Scaffold AI:

Security Score: ${securityScore || "Not evaluated"}
${refinementData.feedback}

Architecture: ${JSON.stringify(architecture, null, 2)}`;
    
    navigator.clipboard.writeText(feedbackText).then(() => {
      const plannerUrl = process.env.NEXT_PUBLIC_PLANNER_URL || "http://localhost:3000";
      window.open(plannerUrl, "_blank");
      alert("Architecture feedback copied to clipboard! Paste it in Project Planner AI to refine your plan.");
    }).catch(() => {
      alert("Failed to copy feedback to clipboard");
    });
  };

  return (
    <Button
      variant="normal"
      iconName="undo"
      onClick={handleRefine}
    >
      Refine in Planner
    </Button>
  );
}
